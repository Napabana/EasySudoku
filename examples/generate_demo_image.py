"""Generate the deterministic EasySudoku demo image with OpenCV."""

from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np


HERE = Path(__file__).resolve().parent
GRID_PATH = HERE / "demo_grid.json"
OUTPUT_PATH = HERE / "demo_sudoku.png"

CANVAS_SIZE = 990
BOARD_START = 45
CELL_SIZE = 100
BOARD_END = BOARD_START + 9 * CELL_SIZE


def load_grid() -> list[list[int]]:
    grid = json.loads(GRID_PATH.read_text(encoding="utf-8"))
    if len(grid) != 9 or any(len(row) != 9 for row in grid):
        raise ValueError("demo_grid.json must contain a 9x9 grid")
    return grid


def generate_image(grid: list[list[int]]) -> np.ndarray:
    image = np.full((CANVAS_SIZE, CANVAS_SIZE, 3), 255, dtype=np.uint8)

    for index in range(10):
        thickness = 7 if index % 3 == 0 else 3
        coordinate = BOARD_START + index * CELL_SIZE
        cv2.line(image, (BOARD_START, coordinate), (BOARD_END, coordinate), (0, 0, 0), thickness)
        cv2.line(image, (coordinate, BOARD_START), (coordinate, BOARD_END), (0, 0, 0), thickness)

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 2.15
    digit_thickness = 5
    for row in range(9):
        for col in range(9):
            value = grid[row][col]
            if value == 0:
                continue
            text = str(value)
            (width, height), baseline = cv2.getTextSize(text, font, font_scale, digit_thickness)
            cell_x = BOARD_START + col * CELL_SIZE
            cell_y = BOARD_START + row * CELL_SIZE
            origin = (
                cell_x + (CELL_SIZE - width) // 2,
                cell_y + (CELL_SIZE + height) // 2 - baseline,
            )
            cv2.putText(image, text, origin, font, font_scale, (0, 0, 0), digit_thickness, cv2.LINE_AA)

    return image


def main() -> None:
    image = generate_image(load_grid())
    if not cv2.imwrite(str(OUTPUT_PATH), image):
        raise RuntimeError(f"Could not write {OUTPUT_PATH}")
    print(f"Generated {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
