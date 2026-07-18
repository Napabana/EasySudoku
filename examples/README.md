# Deterministic Demo Puzzle

`demo_grid.json` contains a fixed Sudoku puzzle with one solution. `expected_grid.json` contains that solution. Both are shared by documentation, API tests, and browser flows so the demo does not depend on a private upload.

Generate the image from the repository root:

```bash
source venv312/bin/activate
python examples/generate_demo_image.py
```

The script writes `examples/demo_sudoku.png` using only deterministic OpenCV drawing operations. The intended OCR transcription is exactly `demo_grid.json`; users must still be allowed to correct any recognized cell before confirming the givens.

This clean synthetic image is an integration fixture. It does not model camera angle, glare, blur, handwriting, compression, printing variation, or background clutter and must not be used as evidence of real-photo OCR accuracy.

The optional “Load demo puzzle / 加载示例盘面” UI action loads the same fixed grid as editable input and then follows the normal confirm, deduction, hint, solve, history, and persistence logic. It does not inject a solution or bypass the backend deduction API.
