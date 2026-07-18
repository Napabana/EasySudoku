"""EasySudoku FastAPI backend for the solver-verified Sudoku tutor."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Literal, Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from smt_engine import get_cell_candidates, get_next_logical_step, solve_full
from vision import image_to_grid


BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"
FRONTEND_INDEX = FRONTEND_DIST / "index.html"
FRONTEND_ASSETS = FRONTEND_DIST / "assets"
LEGACY_INDEX = BASE_DIR / "templates" / "index.html"
OCR_MODEL_PATH = BASE_DIR / "models" / "sudoku_chars74k.onnx"

ALLOWED_IMAGE_TYPES = {
    "image/bmp",
    "image/jpeg",
    "image/png",
    "image/tiff",
    "image/webp",
}
API_ROUTE_ROOTS = {
    "api",
    "docs",
    "health",
    "hint-cell",
    "next-step",
    "openapi.json",
    "redoc",
    "solve",
    "upload",
    "version",
}


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _positive_int_env(name: str, default: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError:
        return default
    return value if value > 0 else default


def _public_version(value: str, fallback: str) -> str:
    candidate = value.strip()
    if re.fullmatch(r"[A-Za-z0-9._+-]{1,64}", candidate):
        return candidate
    return fallback


ALLOW_LEGACY_FRONTEND = _env_flag("ALLOW_LEGACY_FRONTEND")
MAX_UPLOAD_BYTES = _positive_int_env("MAX_UPLOAD_BYTES", 10 * 1024 * 1024)
APP_VERSION = _public_version(os.getenv("APP_VERSION", "0.2.0"), "0.2.0")
_git_commit = os.getenv("GIT_COMMIT", "").strip()
GIT_COMMIT = _git_commit if re.fullmatch(r"[0-9a-fA-F]{7,40}", _git_commit) else None

app = FastAPI(title="EasySudoku", version=APP_VERSION)

STATIC_DIR = BASE_DIR / "static"
if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
if FRONTEND_ASSETS.is_dir():
    app.mount("/assets", StaticFiles(directory=FRONTEND_ASSETS), name="frontend-assets")


class GridRequest(BaseModel):
    grid: list[list[int]]


class HintCellRequest(BaseModel):
    grid: list[list[int]]
    row: int
    col: int


class TargetCell(BaseModel):
    row: int
    col: int


class CandidateChange(BaseModel):
    row: int
    col: int
    removed: list[int]
    reason_key: Optional[str] = None
    reason_params: dict[str, str | int | float] = Field(default_factory=dict)


class StructuredStep(BaseModel):
    rule_type: str
    difficulty: Literal["basic", "intermediate", "advanced", "smt"]
    target_cell: Optional[TargetCell] = None
    value: Optional[int] = None
    explanation_key: str
    explanation_params: dict[str, str | int | float] = Field(default_factory=dict)
    candidate_changes: list[CandidateChange] = Field(default_factory=list)
    verification_type: Optional[Literal["human_rule", "smt"]] = None


class StepResponse(BaseModel):
    row: int
    col: int
    value: int
    explanation: str
    eliminations: list[str]
    updated_grid: list[list[int]]
    step: Optional[StructuredStep] = None
    board: Optional[list[list[int]]] = None
    candidates: Optional[list] = None
    legacy_explanation: Optional[str] = None


class SolveResponse(BaseModel):
    solution: Optional[list[list[int]]]


def _frontend_response() -> FileResponse:
    if FRONTEND_INDEX.is_file():
        return FileResponse(FRONTEND_INDEX)
    if ALLOW_LEGACY_FRONTEND and LEGACY_INDEX.is_file():
        return FileResponse(LEGACY_INDEX)
    raise HTTPException(
        status_code=503,
        detail={
            "code": "FRONTEND_BUILD_MISSING",
            "message": "Vue frontend build is unavailable. Run `cd frontend && npm ci && npm run build`.",
        },
    )


@app.get("/health")
async def health() -> dict[str, str | bool]:
    frontend_available = FRONTEND_INDEX.is_file()
    model_available = OCR_MODEL_PATH.is_file()
    return {
        "status": "ok" if frontend_available and model_available else "degraded",
        "frontend_build_available": frontend_available,
        "ocr_model_available": model_available,
        "application_version": APP_VERSION,
    }


@app.get("/version")
async def version() -> dict[str, Optional[str]]:
    return {"version": APP_VERSION, "git_commit": GIT_COMMIT}


@app.get("/")
async def index() -> FileResponse:
    return _frontend_response()


@app.post("/upload", response_model=GridRequest)
async def upload_image(file: UploadFile = File(...)) -> GridRequest:
    """Validate an uploaded image, run local OCR, and return a 9x9 grid."""
    content_type = (file.content_type or "").split(";", 1)[0].strip().lower()
    if content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=415,
            detail={"code": "UNSUPPORTED_MEDIA_TYPE", "message": "Upload a supported image file."},
        )
    if not OCR_MODEL_PATH.is_file():
        raise HTTPException(
            status_code=503,
            detail={"code": "OCR_MODEL_UNAVAILABLE", "message": "OCR model is unavailable."},
        )

    try:
        image_bytes = await file.read(MAX_UPLOAD_BYTES + 1)
    finally:
        await file.close()

    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail={"code": "EMPTY_FILE", "message": "The uploaded file is empty."},
        )
    if len(image_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail={"code": "FILE_TOO_LARGE", "message": "The uploaded image exceeds the size limit."},
        )

    try:
        grid = image_to_grid(image_bytes)
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail={"code": "OCR_PROCESSING_FAILED", "message": "The image could not be processed."},
        ) from exc

    if not any(value for row in grid for value in row):
        raise HTTPException(
            status_code=422,
            detail={"code": "OCR_NO_DIGITS", "message": "No Sudoku digits were recognized."},
        )
    return GridRequest(grid=grid)


@app.post("/next-step", response_model=Optional[StepResponse])
async def next_step(req: GridRequest) -> Optional[StepResponse]:
    result = get_next_logical_step(req.grid)
    return None if result is None else StepResponse(**result)


@app.post("/solve", response_model=SolveResponse)
async def solve(req: GridRequest) -> SolveResponse:
    return SolveResponse(solution=solve_full(req.grid))


@app.post("/hint-cell")
async def hint_cell(req: HintCellRequest):
    return get_cell_candidates(req.grid, req.row, req.col)


@app.get("/{full_path:path}")
async def spa_fallback(full_path: str) -> FileResponse:
    """Serve client-side routes without turning missing API paths into HTML."""
    route_root = full_path.split("/", 1)[0]
    if route_root in API_ROUTE_ROOTS:
        raise HTTPException(status_code=404, detail="API route not found")
    return _frontend_response()
