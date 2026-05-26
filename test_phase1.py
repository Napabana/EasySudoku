"""Test Phase 1: Z3 basic modeling with a hardcoded sudoku."""

from smt_engine import solve_full, build_solver
from z3 import sat

# A well-known sudoku puzzle (0 = empty)
TEST_GRID = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
]


def test_solve_full():
    solution = solve_full(TEST_GRID)
    assert solution is not None, "Solver returned UNSAT — puzzle should be solvable"

    # Verify all values in range
    for i in range(9):
        for j in range(9):
            assert 1 <= solution[i][j] <= 9, f"Out of range: [{i}][{j}] = {solution[i][j]}"

    # Verify given cells preserved
    for i in range(9):
        for j in range(9):
            if TEST_GRID[i][j] != 0:
                assert solution[i][j] == TEST_GRID[i][j], \
                    f"Given cell changed: [{i}][{j}] expected {TEST_GRID[i][j]}, got {solution[i][j]}"

    # Verify rows distinct
    for i in range(9):
        assert len(set(solution[i])) == 9, f"Row {i} not distinct"

    # Verify columns distinct
    for j in range(9):
        col = [solution[i][j] for i in range(9)]
        assert len(set(col)) == 9, f"Col {j} not distinct"

    # Verify boxes distinct
    for br in range(3):
        for bc in range(3):
            box = [
                solution[br * 3 + dr][bc * 3 + dc]
                for dr in range(3)
                for dc in range(3)
            ]
            assert len(set(box)) == 9, f"Box ({br},{bc}) not distinct"

    print("PASS: Full solution verified")
    for row in solution:
        print(row)


def test_unsat_puzzle():
    """An impossible puzzle should return None."""
    bad_grid = [
        [1, 2, 3, 4, 5, 6, 7, 8, 9],
        [1, 0, 0, 0, 0, 0, 0, 0, 0],  # duplicate 1 in col 0
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]
    result = solve_full(bad_grid)
    assert result is None, "Expected UNSAT for contradictory puzzle"
    print("PASS: UNSAT detection works")


if __name__ == "__main__":
    test_solve_full()
    test_unsat_puzzle()
    print("\nAll Phase 1 tests passed!")
