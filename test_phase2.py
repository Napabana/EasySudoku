"""Test Phase 2: UNSAT Core step-by-step derivation."""

from smt_engine import get_next_logical_step, solve_full

# Same puzzle from Phase 1
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


def test_single_step():
    """Verify that get_next_logical_step returns a valid derivation."""
    result = get_next_logical_step(TEST_GRID)
    assert result is not None, "Expected at least one step to be derivable"

    row, col, value = result["row"], result["col"], result["value"]
    print(f"Step found: ({row + 1},{col + 1}) = {value}")
    print(result["explanation"])
    print()

    # The value must match the full solution
    full = solve_full(TEST_GRID)
    assert full is not None
    assert full[row][col] == value, \
        f"Step value {value} != solution value {full[row][col]}"

    # Updated grid must preserve all original givens
    updated = result["updated_grid"]
    for i in range(9):
        for j in range(9):
            if TEST_GRID[i][j] != 0:
                assert updated[i][j] == TEST_GRID[i][j]

    # The new cell must be filled
    assert updated[row][col] == value
    print("PASS: single step derivation correct\n")


def test_iterative_steps():
    """Repeatedly apply steps until the puzzle is solved or stuck."""
    grid = [row[:] for row in TEST_GRID]
    steps = 0

    while True:
        empty = sum(1 for i in range(9) for j in range(9) if grid[i][j] == 0)
        if empty == 0:
            print(f"Puzzle fully solved in {steps} steps!")
            break

        result = get_next_logical_step(grid)
        if result is None:
            print(f"Stuck after {steps} steps with {empty} cells remaining.")
            print("This is expected for harder puzzles that need advanced techniques.")
            break

        grid = result["updated_grid"]
        steps += 1
        if steps <= 5:
            print(f"Step {steps}: ({result['row'] + 1},{result['col'] + 1}) = {result['value']}")

    # Verify whatever we have so far is consistent
    solution = solve_full(TEST_GRID)
    assert solution is not None
    for i in range(9):
        for j in range(9):
            if grid[i][j] != 0:
                assert grid[i][j] == solution[i][j], \
                    f"Mismatch at ({i},{j}): got {grid[i][j]}, expected {solution[i][j]}"

    print(f"PASS: {steps} iterative steps, all consistent")


if __name__ == "__main__":
    test_single_step()
    test_iterative_steps()
    print("\nAll Phase 2 tests passed!")
