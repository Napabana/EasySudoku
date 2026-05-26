"""
EasySudoku - FastAPI backend for SMT-based Sudoku Tutor.
"""

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import os

from smt_engine import get_next_logical_step, solve_full, get_cell_candidates
from vision import image_to_grid

app = FastAPI(title="EasySudoku")

# Serve static files
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class GridRequest(BaseModel):
    grid: list[list[int]]


class HintCellRequest(BaseModel):
    grid: list[list[int]]
    row: int
    col: int


class StepResponse(BaseModel):
    row: int
    col: int
    value: int
    explanation: str
    eliminations: list[str]
    updated_grid: list[list[int]]


class SolveResponse(BaseModel):
    solution: Optional[list[list[int]]]


@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
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
