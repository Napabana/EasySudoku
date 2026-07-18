"""Regression checks for the deterministic hackathon demo fixture."""

import json
from pathlib import Path

from z3 import Or, unsat

from smt_engine import build_solver, solve_full
from vision import image_to_grid


ROOT = Path(__file__).resolve().parent
PUZZLE = json.loads((ROOT / "examples" / "demo_grid.json").read_text(encoding="utf-8"))
EXPECTED = json.loads((ROOT / "examples" / "expected_grid.json").read_text(encoding="utf-8"))
IMAGE = ROOT / "examples" / "demo_sudoku.png"


def main() -> None:
    assert solve_full(PUZZLE) == EXPECTED, "demo solution differs from expected_grid.json"

    solver, variables = build_solver(PUZZLE)
    solver.add(Or([
        variables[row][col] != EXPECTED[row][col]
        for row in range(9)
        for col in range(9)
    ]))
    assert solver.check() == unsat, "demo puzzle is not uniquely solved by expected_grid.json"

    recognized = image_to_grid(IMAGE.read_bytes())
    assert recognized == PUZZLE, f"synthetic OCR mismatch: {recognized!r}"
    print("PASS: deterministic demo puzzle is unique and OCR matches demo_grid.json")


if __name__ == "__main__":
    main()
