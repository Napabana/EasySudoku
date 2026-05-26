"""
Computer Vision module for Sudoku image recognition.
Uses OpenCV for image processing and EasyOCR for digit recognition.
"""

import cv2
import numpy as np
import easyocr
from typing import Optional


_reader = None


def _get_reader():
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(["en"], gpu=False)
    return _reader


def _find_puzzle_contour(gray: np.ndarray) -> Optional[np.ndarray]:
    """Find the largest quadrilateral contour (sudoku outer frame)."""
    blurred = cv2.GaussianBlur(gray, (7, 7), 3)
    edged = cv2.Canny(blurred, 50, 150)

    contours, _ = cv2.findContours(
        edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE,
    )
    if not contours:
        return None

    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            return approx.reshape(4, 2)

    return None


def _order_points(pts: np.ndarray) -> np.ndarray:
    """Order points: top-left, top-right, bottom-right, bottom-left."""
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    d = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(d)]
    rect[3] = pts[np.argmax(d)]
    return rect


def _warp_perspective(image: np.ndarray, pts: np.ndarray, size: int = 900) -> np.ndarray:
    """Perform perspective transform to get a top-down view of the puzzle."""
    rect = _order_points(pts)
    dst = np.array([
        [0, 0], [size - 1, 0],
        [size - 1, size - 1], [0, size - 1],
    ], dtype="float32")
    M = cv2.getPerspectiveTransform(rect, dst)
    return cv2.warpPerspective(image, M, (size, size))


def _extract_cells(warped: np.ndarray) -> list[list[np.ndarray]]:
    """Split the warped image into 81 individual cell images."""
    cell_h = warped.shape[0] // 9
    cell_w = warped.shape[1] // 9
    cells = []
    margin = 8  # crop border to remove grid lines

    for i in range(9):
        row = []
        for j in range(9):
            y1 = i * cell_h + margin
            y2 = (i + 1) * cell_h - margin
            x1 = j * cell_w + margin
            x2 = (j + 1) * cell_w - margin
            cell = warped[y1:y2, x1:x2]
            row.append(cell)
        cells.append(row)
    return cells


def _extract_digit_roi(cell_img: np.ndarray) -> Optional[np.ndarray]:
    """
    Dynamically extract the digit region from a cell using contour analysis.
    Returns None if the cell is empty (no significant contour found).
    Returns the cropped digit image with white padding if a digit is found.

    Pipeline:
    1. Grayscale + adaptive threshold (BINARY_INV → digits are white on black)
    2. findContours with RETR_EXTERNAL to get outer shapes
    3. Filter out tiny noise contours (area < MIN_CONTOUR_AREA)
    4. Merge all valid contour bounding boxes into one ROI
    5. Crop from original image and add white padding
    """
    MIN_CONTOUR_AREA = 30
    MIN_CONTOUR_HEIGHT_RATIO = 0.20  # contour must be ≥20% of cell height

    gray = cv2.cvtColor(cell_img, cv2.COLOR_BGR2GRAY) if len(cell_img.shape) == 3 else cell_img
    h, w = gray.shape[:2]

    # Adaptive threshold — handles uneven lighting
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 31, 10,
    )

    contours, _ = cv2.findContours(
        binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE,
    )

    if not contours:
        return None

    # Filter out noise: keep only contours with sufficient area and height
    valid_contours = []
    for c in contours:
        area = cv2.contourArea(c)
        _, _, cw, ch = cv2.boundingRect(c)
        if area >= MIN_CONTOUR_AREA and ch >= h * MIN_CONTOUR_HEIGHT_RATIO:
            valid_contours.append(c)

    if not valid_contours:
        return None

    # Merge all valid bounding boxes into one encompassing ROI
    x_min, y_min = w, h
    x_max, y_max = 0, 0
    for c in valid_contours:
        cx, cy, cw, ch = cv2.boundingRect(c)
        x_min = min(x_min, cx)
        y_min = min(y_min, cy)
        x_max = max(x_max, cx + cw)
        y_max = max(y_max, cy + ch)

    # Boundary safety check
    x_min = max(0, x_min)
    y_min = max(0, y_min)
    x_max = min(w, x_max)
    y_max = min(h, y_max)

    if x_max <= x_min or y_max <= y_min:
        return None

    # Crop digit from original grayscale image (not binary — preserves quality)
    digit_roi = gray[y_min:y_max, x_min:x_max]

    # Add white padding around the digit (EasyOCR needs margin)
    PAD = 8
    digit_padded = cv2.copyMakeBorder(
        digit_roi, PAD, PAD, PAD, PAD,
        cv2.BORDER_CONSTANT, value=255,
    )

    return digit_padded


def _recognize_digit(cell_img: np.ndarray) -> int:
    """
    Recognize a digit in a cell image, return 0 if empty.

    Pipeline:
    1. Dynamic contour extraction → determines if cell is empty and isolates digit
    2. Resize to minimum height if needed
    3. EasyOCR with strict digit-only allowlist
    """
    # Task 1 & 2: Dynamic ROI extraction + empty cell detection
    digit_roi = _extract_digit_roi(cell_img)
    if digit_roi is None:
        return 0

    # Task 3: Resize if too small — no morphological operations
    h, w = digit_roi.shape[:2]
    if h < 32 or w < 32:
        scale = max(32 / h, 32 / w)
        digit_roi = cv2.resize(
            digit_roi, None, fx=scale, fy=scale,
            interpolation=cv2.INTER_CUBIC,
        )

    # Task 4: EasyOCR with strict parameters
    # Convert grayscale to BGR for EasyOCR compatibility
    if len(digit_roi.shape) == 2:
        img_for_ocr = cv2.cvtColor(digit_roi, cv2.COLOR_GRAY2BGR)
    else:
        img_for_ocr = digit_roi

    reader = _get_reader()
    results = reader.readtext(
        img_for_ocr,
        allowlist="123456789",
        detail=0,
        paragraph=False,
    )

    if not results:
        return 0

    try:
        digit = int(results[0].strip())
        if 1 <= digit <= 9:
            return digit
    except (ValueError, IndexError):
        pass

    return 0


def image_to_grid(image_bytes: bytes) -> list[list[int]]:
    """
    Convert an uploaded image to a 9x9 sudoku grid.

    Args:
        image_bytes: raw image file bytes

    Returns:
        9x9 grid with 0 for empty cells, 1-9 for digits.
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Could not decode image")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    contour = _find_puzzle_contour(gray)
    if contour is None:
        # Fallback: assume the image is already a cropped puzzle
        warped = image
    else:
        warped = _warp_perspective(image, contour)

    cells = _extract_cells(warped)

    grid = [[0] * 9 for _ in range(9)]
    for i in range(9):
        for j in range(9):
            grid[i][j] = _recognize_digit(cells[i][j])

    return grid
