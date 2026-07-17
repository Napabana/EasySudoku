"""
EasySudoku - FastAPI backend for SMT-based Sudoku Tutor.
"""

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional, Literal
import os

from smt_engine import get_next_logical_step, solve_full, get_cell_candidates
from vision import image_to_grid

app = FastAPI(title="EasySudoku")

BASE_DIR = os.path.dirname(__file__)

# Serve legacy/static files
STATIC_DIR = os.path.join(BASE_DIR, "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

FRONTEND_DIST = os.path.join(BASE_DIR, "frontend", "dist")
FRONTEND_ASSETS = os.path.join(FRONTEND_DIST, "assets")
if os.path.isdir(FRONTEND_ASSETS):
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


@app.get("/", response_class=HTMLResponse)
async def index():
    dist_index = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.exists(dist_index):
        return FileResponse(dist_index)

    html_path = os.path.join(BASE_DIR, "templates", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()


@app.post("/upload", response_model=GridRequest)
async def upload_image(file: UploadFile = File(...)):
    """Receive a photo, run OCR, return the initial sudoku grid."""
    image_bytes = await file.read()
    grid = image_to_grid(image_bytes)
    return GridRequest(grid=grid)


@app.post("/next-step", response_model=Optional[StepResponse])
async def next_step(req: GridRequest):
    """Given the current grid, return the next logical derivation step."""
    result = get_next_logical_step(req.grid)
    if result is None:
        return None
    return StepResponse(**result)


@app.post("/solve", response_model=SolveResponse)
async def solve(req: GridRequest):
    """Solve the entire puzzle at once."""
    solution = solve_full(req.grid)
    return SolveResponse(solution=solution)


@app.post("/hint-cell")
async def hint_cell(req: HintCellRequest):
    """Get candidates and reasoning for a specific cell."""
    return get_cell_candidates(req.grid, req.row, req.col)


@app.get("/{full_path:path}", response_class=HTMLResponse)
async def spa_fallback(full_path: str):
    """Serve Vue router fallback in production, with legacy HTML fallback."""
    dist_index = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.exists(dist_index) and not full_path.startswith(("upload", "next-step", "hint-cell", "solve")):
        return FileResponse(dist_index)
    html_path = os.path.join(BASE_DIR, "templates", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()
