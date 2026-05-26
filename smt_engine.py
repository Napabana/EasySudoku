"""
SMT-based Sudoku Engine using Z3.
Uses assert_and_track for precise UNSAT core mapping,
Python-side pre-pruning for O(1) acceleration,
and integrates heuristic rules for human-like derivation.
"""

from z3 import (
    Solver, Int, Distinct, And, Or, Not, Implies, sat, unsat, Bool,
    ArithRef, BoolRef,
)
from typing import Optional


def _make_vars() -> list[list[ArithRef]]:
    return [[Int(f"V_{i}_{j}") for j in range(9)] for i in range(9)]


def _domain_constraints(V: list[list[ArithRef]]) -> list[BoolRef]:
    constraints = []
    for i in range(9):
        for j in range(9):
            constraints.append(And(V[i][j] >= 1, V[i][j] <= 9))
    return constraints


def _row_constraints(V: list[list[ArithRef]]) -> list[BoolRef]:
    return [Distinct(*V[i]) for i in range(9)]


def _col_constraints(V: list[list[ArithRef]]) -> list[BoolRef]:
    return [Distinct(*(V[i][j] for i in range(9))) for j in range(9)]


def _box_constraints(V: list[list[ArithRef]]) -> list[BoolRef]:
    constraints = []
    for br in range(3):
        for bc in range(3):
            cells = [
                V[br * 3 + dr][bc * 3 + dc]
                for dr in range(3)
                for dc in range(3)
            ]
            constraints.append(Distinct(*cells))
    return constraints


def build_solver(grid: list[list[int]]) -> tuple[Solver, list[list[ArithRef]]]:
    """
    Build a Z3 solver with full sudoku constraints plus given cell values.

    Args:
        grid: 9x9 matrix, 0 = empty, 1-9 = given value.

    Returns:
        (solver, V) tuple — the configured solver and its variable matrix.
    """
    V = _make_vars()
    solver = Solver()

    for c in _domain_constraints(V):
        solver.add(c)
    for c in _row_constraints(V):
        solver.add(c)
    for c in _col_constraints(V):
        solver.add(c)
    for c in _box_constraints(V):
        solver.add(c)

    for i in range(9):
        for j in range(9):
            if grid[i][j] != 0:
                solver.add(V[i][j] == grid[i][j])

    return solver, V


def solve_full(grid: list[list[int]]) -> Optional[list[list[int]]]:
    """
    Solve the sudoku completely, returning the full 9x9 solution or None.
    """
    solver, V = build_solver(grid)
    if solver.check() == sat:
        model = solver.model()
        return [
            [model.eval(V[i][j]).as_long() for j in range(9)]
            for i in range(9)
        ]
    return None


# ---------------------------------------------------------------------------
# Task 3: Python-side pre-pruning with row/col/box bitmask sets
# ---------------------------------------------------------------------------

def _build_used_sets(grid: list[list[int]]) -> tuple[
    list[set[int]], list[set[int]], list[list[set[int]]]
]:
    """
    Build in-memory sets of used digits for each row, column, and box.
    Returns (row_sets, col_sets, box_sets) where box_sets is indexed [br][bc].
    """
    row_sets = [set() for _ in range(9)]
    col_sets = [set() for _ in range(9)]
    box_sets = [[set() for _ in range(3)] for _ in range(3)]

    for i in range(9):
        for j in range(9):
            v = grid[i][j]
            if v != 0:
                row_sets[i].add(v)
                col_sets[j].add(v)
                box_sets[i // 3][j // 3].add(v)

    return row_sets, col_sets, box_sets


def _precheck_elimination(
    row: int, col: int, digit: int,
    row_sets: list[set[int]],
    col_sets: list[set[int]],
    box_sets: list[list[set[int]]],
) -> Optional[str]:
    """
    Python-side O(1) pre-check: if digit is already in the same row,
    column, or box, return a human-readable reason immediately.
    Returns None if the digit passes the pre-check (needs Z3 to verify).
    """
    reasons = []

    if digit in row_sets[row]:
        # Find the exact position for the reason
        reasons.append(f"第 {row + 1} 行已有 {digit}")

    if digit in col_sets[col]:
        reasons.append(f"第 {col + 1} 列已有 {digit}")

    br, bc = row // 3, col // 3
    if digit in box_sets[br][bc]:
        reasons.append(f"宫格已有 {digit}")

    if reasons:
        return f"因为 " + "，且 ".join(reasons) + f"，所以位置 ({row + 1},{col + 1}) 不能填 {digit}"
    return None


# ---------------------------------------------------------------------------
# Task 1: assert_and_track for precise UNSAT core labels
# ---------------------------------------------------------------------------

def _build_tracked_solver(
    grid: list[list[int]],
) -> tuple[Solver, list[list[ArithRef]]]:
    """
    Build a solver where ALL constraints are tracked via assert_and_track.
    This allows unsat_core() to return precise human-readable labels.
    """
    V = _make_vars()
    solver = Solver()
    solver.set("unsat_core", True)

    # Domain constraints — tracked per cell
    for i in range(9):
        for j in range(9):
            solver.assert_and_track(
                And(V[i][j] >= 1, V[i][j] <= 9),
                Bool(f"DOMAIN_{i}_{j}"),
            )

    # Row distinct — tracked per row
    for r in range(9):
        solver.assert_and_track(
            Distinct(*V[r]),
            Bool(f"RULE_ROW_{r}"),
        )

    # Col distinct — tracked per column
    for c in range(9):
        solver.assert_and_track(
            Distinct(*(V[i][c] for i in range(9))),
            Bool(f"RULE_COL_{c}"),
        )

    # Box distinct — tracked per box
    for br in range(3):
        for bc in range(3):
            cells = [
                V[br * 3 + dr][bc * 3 + dc]
                for dr in range(3) for dc in range(3)
            ]
            solver.assert_and_track(
                Distinct(*cells),
                Bool(f"RULE_BOX_{br * 3 + bc}"),
            )

    # Given cell values — tracked individually
    for i in range(9):
        for j in range(9):
            if grid[i][j] != 0:
                solver.assert_and_track(
                    V[i][j] == grid[i][j],
                    Bool(f"GIVEN_R{i}_C{j}_V{grid[i][j]}"),
                )

    return solver, V


def _parse_core_labels(core) -> list[str]:
    """
    Parse unsat_core() labels into human-readable strings.
    Prioritize GIVEN labels (most informative) and summarize RULE labels.
    Limits output to avoid overwhelming the user with indirect conflicts.
    """
    given_reasons = []
    rule_types = {"row": 0, "col": 0, "box": 0}

    for atom in core:
        label = str(atom)
        if label.startswith("GIVEN_R"):
            parts = label.replace("GIVEN_", "").split("_")
            r, c, v = int(parts[0][1:]), int(parts[1][1:]), parts[2][1:]
            given_reasons.append(f"第 {r + 1} 行第 {c + 1} 列已有 {v}")
        elif label.startswith("RULE_ROW_"):
            rule_types["row"] += 1
        elif label.startswith("RULE_COL_"):
            rule_types["col"] += 1
        elif label.startswith("RULE_BOX_"):
            rule_types["box"] += 1

    # If we have specific given-cell reasons, show top ones + summary
    if given_reasons:
        if len(given_reasons) <= 4:
            return given_reasons
        # Show first 3 + summary count
        shown = given_reasons[:3]
        shown.append(f"等共 {len(given_reasons)} 个已知数字产生组合冲突")
        return shown

    # Otherwise show rule-level summary
    parts = []
    if rule_types["row"]:
        parts.append(f"{rule_types['row']} 行")
    if rule_types["col"]:
        parts.append(f"{rule_types['col']} 列")
    if rule_types["box"]:
        parts.append(f"{rule_types['box']} 个宫格")
    if parts:
        return [f"涉及 " + "、".join(parts) + "的唯一性约束组合冲突"]
    return []


def _explain_via_core(
    row: int, col: int, digit: int,
    solver: Solver,
) -> str:
    """
    Use unsat_core() from a tracked solver to generate a precise explanation.
    """
    core = solver.unsat_core()
    labels = _parse_core_labels(core)

    if not labels:
        return f"位置 ({row + 1},{col + 1}) 不能填 {digit}（与多重约束组合冲突）"

    prefix = f"因为 "
    suffix = f"，所以位置 ({row + 1},{col + 1}) 不能填 {digit}"
    return prefix + "，且 ".join(labels) + suffix


# ---------------------------------------------------------------------------
# Shared explanation dispatcher
# ---------------------------------------------------------------------------

def _explain_elimination(
    row: int, col: int, digit: int,
    grid: list[list[int]],
    row_sets: list[set[int]],
    col_sets: list[set[int]],
    box_sets: list[list[set[int]]],
    solver: Optional[Solver] = None,
) -> str:
    """
    Tiered explanation:
    1. Python pre-check (O(1) — direct peer lookup)
    2. Z3 unsat_core (precise tracked labels — if solver provided)
    3. Fallback generic message
    """
    precheck = _precheck_elimination(row, col, digit, row_sets, col_sets, box_sets)
    if precheck:
        return precheck

    if solver is not None:
        return _explain_via_core(row, col, digit, solver)

    return f"位置 ({row + 1},{col + 1}) 不能填 {digit}（与多重约束组合冲突）"


# ---------------------------------------------------------------------------
# Task 4: Heuristic engine integration point
# ---------------------------------------------------------------------------

def _apply_heuristics(grid: list[list[int]]) -> Optional[dict]:
    """
    Apply lightweight heuristic rules before falling back to Z3.
    Returns a step dict if a heuristic succeeds, None otherwise.

    Currently integrates:
    - Hidden Single (from heuristic_engine.py)
    - Naked Pair elimination (from heuristic_engine.py)
    """
    try:
        from heuristic_engine import find_hidden_single, find_naked_pair
    except ImportError:
        return None

    # Try Hidden Single first (simpler, faster)
    result = find_hidden_single(grid)
    if result:
        return result

    # Try Naked Pair
    result = find_naked_pair(grid)
    if result:
        return result

    return None


# ---------------------------------------------------------------------------
# Core derivation functions
# ---------------------------------------------------------------------------

def get_next_logical_step(
    grid: list[list[int]],
) -> Optional[dict]:
    """
    Find the next cell that can be uniquely determined.

    Pipeline (Task 4):
    1. Heuristic rules (Hidden Single, Naked Pair) — fast, human-like
    2. SMT UNSAT Core elimination — precise, covers all cases

    Returns:
        None if no cell can be uniquely determined.
        Otherwise a dict with row, col, value, explanation, eliminations, updated_grid.
    """
    # Phase 1: Try heuristic rules
    heuristic_result = _apply_heuristics(grid)
    if heuristic_result is not None:
        return heuristic_result

    # Phase 2: SMT-based derivation with pre-pruning + tracked solver
    row_sets, col_sets, box_sets = _build_used_sets(grid)
    solver, V = _build_tracked_solver(grid)

    empty_cells = [
        (i, j)
        for i in range(9) for j in range(9)
        if grid[i][j] == 0
    ]

    for row, col in empty_cells:
        possible: list[int] = []
        elimination_reasons: list[str] = []

        for digit in range(1, 10):
            # Task 3: Python pre-pruning — skip Z3 if digit is clearly impossible
            precheck = _precheck_elimination(
                row, col, digit, row_sets, col_sets, box_sets,
            )
            if precheck:
                elimination_reasons.append(precheck)
                continue

            # Task 3: Use check with assumption instead of push/pop
            assumption = Bool(f"place_{row}_{col}_{digit}")
            solver.push()
            solver.add(Implies(assumption, V[row][col] == digit))

            result = solver.check([assumption])

            if result == unsat:
                # Task 1: Extract precise core labels
                reason = _explain_via_core(row, col, digit, solver)
                elimination_reasons.append(reason)
            else:
                possible.append(digit)

            solver.pop()

        if len(possible) == 1:
            value = possible[0]
            updated = [r[:] for r in grid]
            updated[row][col] = value

            elim_text = "\n".join(f"  - {r}" for r in elimination_reasons)
            explanation = (
                f"位置 ({row + 1},{col + 1}) 只能填 {value}：\n"
                f"{elim_text}\n"
                f"  因此唯一可能的数字是 {value}。"
            )

            return {
                "row": row,
                "col": col,
                "value": value,
                "explanation": explanation,
                "eliminations": elimination_reasons,
                "updated_grid": updated,
            }

    return None


def get_cell_candidates(
    grid: list[list[int]], row: int, col: int,
) -> dict:
    """
    For a specific empty cell (row, col), determine all valid candidates
    and explain why each eliminated digit is impossible.

    Returns:
        dict with row, col, candidates, eliminations, explanation.
    """
    row_sets, col_sets, box_sets = _build_used_sets(grid)
    solver, V = _build_tracked_solver(grid)

    candidates: list[int] = []
    eliminations: list[str] = []

    for digit in range(1, 10):
        # Python pre-pruning
        precheck = _precheck_elimination(
            row, col, digit, row_sets, col_sets, box_sets,
        )
        if precheck:
            eliminations.append(precheck)
            continue

        # Z3 check with assumption (no push/pop)
        assumption = Bool(f"hint_{row}_{col}_{digit}")
        solver.push()
        solver.add(Implies(assumption, V[row][col] == digit))

        if solver.check([assumption]) == sat:
            candidates.append(digit)
        else:
            reason = _explain_via_core(row, col, digit, solver)
            eliminations.append(reason)

        solver.pop()

    if len(candidates) == 1:
        val = candidates[0]
        elim_text = "\n".join(f"  - {r}" for r in eliminations)
        explanation = (
            f"位置 ({row + 1},{col + 1}) 的唯一候选数是 {val}：\n"
            f"{elim_text}\n"
            f"  因此该位置只能填 {val}。"
        )
    elif len(candidates) == 0:
        explanation = f"位置 ({row + 1},{col + 1}) 无合法候选数，盘面可能存在错误。"
    else:
        explanation = (
            f"位置 ({row + 1},{col + 1}) 的候选数为 "
            f"{candidates}（共 {len(candidates)} 个）。"
        )
        if eliminations:
            elim_text = "\n".join(f"  - {r}" for r in eliminations)
            explanation += f"\n排除原因：\n{elim_text}"

    return {
        "row": row,
        "col": col,
        "candidates": candidates,
        "eliminations": eliminations,
        "explanation": explanation,
    }
