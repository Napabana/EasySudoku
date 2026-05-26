"""Test Phase 3: Vision module import and basic structure."""

import sys


def test_vision_import():
    """Verify all vision module functions are importable."""
    from vision import (
        image_to_grid,
        _find_puzzle_contour,
        _order_points,
        _warp_perspective,
        _extract_cells,
        _recognize_digit,
    )
    print("PASS: vision module imports successfully")


def test_vision_with_test_image():
    """
    Create a synthetic test image (blank white with a few digits)
    and verify the pipeline runs without crashing.
    """
    import cv2
    import numpy as np
    from vision import _extract_cells

    # Create a blank 450x450 white image (simulates empty puzzle)
    img = np.ones((450, 450, 3), dtype=np.uint8) * 255
    cells = _extract_cells(img)

    assert len(cells) == 9, f"Expected 9 rows, got {len(cells)}"
    assert all(len(row) == 9 for row in cells), "Expected 9 cells per row"

    print("PASS: cell extraction works on synthetic image")


def test_order_points():
    """Test the point ordering utility."""
    import numpy as np
    from vision import _order_points

    # Unordered quadrilateral points
    pts = np.array([
        [100, 0],    # top-right
        [0, 0],      # top-left
        [0, 100],    # bottom-left
        [100, 100],  # bottom-right
    ], dtype="float32")

    ordered = _order_points(pts)
    assert ordered[0][0] == 0 and ordered[0][1] == 0, "Top-left should be first"
    assert ordered[1][0] == 100 and ordered[1][1] == 0, "Top-right should be second"
    assert ordered[2][0] == 100 and ordered[2][1] == 100, "Bottom-right should be third"
    assert ordered[3][0] == 0 and ordered[3][1] == 100, "Bottom-left should be fourth"

    print("PASS: point ordering is correct")


if __name__ == "__main__":
    test_vision_import()
    test_vision_with_test_image()
    test_order_points()
    print("\nAll Phase 3 tests passed!")
