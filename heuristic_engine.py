"""
Lightweight heuristic rules for human-like Sudoku derivation.
These run before Z3 as fast O(n) / O(n^2) filters.
Z3 acts as a fallback for cases these rules cannot resolve.
"""

from typing import Optional


def _box_cells(br: int, bc: int) -> list[tuple[int, int]]:
    """Return all 9 cell coordinates in a 3x3 box."""
    return [
        (br * 3 + dr, bc * 3 + dc)
        for dr in range(3) for dc in range(3)
    ]


def _get_candidates(
    grid: list[list[int]], row: int, col: int,
) -> set[int]:
    """Compute candidate digits for an empty cell using row/col/box peers."""
    if grid[row][col] != 0:
        return set()

    used = set()
    # Row
    for j in range(9):
        used.add(grid[row][j])
    # Column
    for i in range(9):
        used.add(grid[i][col])
    # Box
    br, bc = row // 3, col // 3
    for i2, j2 in _box_cells(br, bc):
        used.add(grid[i2][j2])

    return set(range(1, 10)) - used


def _compute_all_candidates(
    grid: list[list[int]],
) -> dict[tuple[int, int], set[int]]:
    """Compute candidates for every empty cell."""
    result = {}
    for i in range(9):
        for j in range(9):
            if grid[i][j] == 0:
                result[(i, j)] = _get_candidates(grid, i, j)
    return result


def _format_step(
    row: int, col: int, value: int,
    technique: str, reason: str,
    grid: list[list[int]],
) -> dict:
    """Build a standard step result dict."""
    updated = [r[:] for r in grid]
    updated[row][col] = value

    explanation = (
        f"【{technique}】\n"
        f"位置 ({row + 1},{col + 1}) = {value}\n"
        f"{reason}"
    )

    return {
        "row": row,
        "col": col,
        "value": value,
        "explanation": explanation,
        "eliminations": [reason],
        "updated_grid": updated,
    }


# ---------------------------------------------------------------------------
# Rule 1: Hidden Single
# ---------------------------------------------------------------------------

def find_hidden_single(grid: list[list[int]]) -> Optional[dict]:
    """
    For each digit k, check each row/col/box. If k can only go in one
    empty cell within that unit, it's a Hidden Single.

    This is O(9 * 27 * 9) = O(2187), trivially fast.
    """
    candidates = _compute_all_candidates(grid)

    # Scan rows
    for r in range(9):
        for digit in range(1, 10):
            # Check if digit is already in this row
            if any(grid[r][j] == digit for j in range(9)):
                continue

            # Find empty cells in this row where digit is a candidate
            possible_cols = [
                j for j in range(9)
                if grid[r][j] == 0 and digit in candidates.get((r, j), set())
            ]
            if len(possible_cols) == 1:
                c = possible_cols[0]
                return _format_step(
                    r, c, digit,
                    "隐性唯一数 (Hidden Single)",
                    f"数字 {digit} 在第 {r + 1} 行中只能填在位置 ({r + 1},{c + 1})",
                    grid,
                )

    # Scan columns
    for c in range(9):
        for digit in range(1, 10):
            if any(grid[i][c] == digit for i in range(9)):
                continue

            possible_rows = [
                i for i in range(9)
                if grid[i][c] == 0 and digit in candidates.get((i, c), set())
            ]
            if len(possible_rows) == 1:
                r = possible_rows[0]
                return _format_step(
                    r, c, digit,
                    "隐性唯一数 (Hidden Single)",
                    f"数字 {digit} 在第 {c + 1} 列中只能填在位置 ({r + 1},{c + 1})",
                    grid,
                )

    # Scan boxes
    for br in range(3):
        for bc in range(3):
            cells = _box_cells(br, bc)
            for digit in range(1, 10):
                if any(grid[i][j] == digit for i, j in cells):
                    continue

                possible = [
                    (i, j) for i, j in cells
                    if grid[i][j] == 0 and digit in candidates.get((i, j), set())
                ]
                if len(possible) == 1:
                    r, c = possible[0]
                    return _format_step(
                        r, c, digit,
                        "隐性唯一数 (Hidden Single)",
                        f"数字 {digit} 在宫格（第 {br * 3 + 1}-{br * 3 + 3} 行、"
                        f"第 {bc * 3 + 1}-{bc * 3 + 3} 列）中只能填在位置 ({r + 1},{c + 1})",
                        grid,
                    )

    return None


# ---------------------------------------------------------------------------
# Rule 2: Naked Pair elimination
# ---------------------------------------------------------------------------

def find_naked_pair(grid: list[list[int]]) -> Optional[dict]:
    """
    Find two cells in the same row/col/box that share exactly the same
    two candidates. Eliminate those two digits from other cells in the unit.
    If this resolves to a single candidate in another cell, return that step.

    Returns a step if the pair elimination directly determines a cell value.
    Returns None if no cell is directly resolved.
    """
    candidates = _compute_all_candidates(grid)

    def _find_pair_in_unit(cells: list[tuple[int, int]]) -> Optional[dict]:
        """Check a unit (row/col/box) for naked pairs."""
        # Find cells with exactly 2 candidates
        pairs = [
            ((i, j), cands)
            for i, j in cells
            if grid[i][j] == 0 and len(cands := candidates.get((i, j), set())) == 2
        ]

        for idx_a in range(len(pairs)):
            for idx_b in range(idx_a + 1, len(pairs)):
                (r1, c1), cands_a = pairs[idx_a]
                (r2, c2), cands_b = pairs[idx_b]

                if cands_a != cands_b:
                    continue

                # Found a naked pair! Check if elimination resolves another cell
                eliminated = cands_a
                for i, j in cells:
                    if (i, j) in ((r1, c1), (r2, c2)):
                        continue
                    if grid[i][j] != 0:
                        continue

                    cell_cands = candidates.get((i, j), set())
                    remaining = cell_cands - eliminated

                    if len(remaining) == 1:
                        val = remaining.pop()
                        return _format_step(
                            i, j, val,
                            "显性数对排除 (Naked Pair)",
                            f"位置 ({r1 + 1},{c1 + 1}) 和 ({r2 + 1},{c2 + 1}) "
                            f"形成数对 {sorted(cands_a)}，"
                            f"排除后位置 ({i + 1},{j + 1}) 只能填 {val}",
                            grid,
                        )

        return None

    # Scan rows
    for r in range(9):
        cells = [(r, j) for j in range(9)]
        result = _find_pair_in_unit(cells)
        if result:
            return result

    # Scan columns
    for c in range(9):
        cells = [(i, c) for i in range(9)]
        result = _find_pair_in_unit(cells)
        if result:
            return result

    # Scan boxes
    for br in range(3):
        for bc in range(3):
            result = _find_pair_in_unit(_box_cells(br, bc))
            if result:
                return result

    return None
