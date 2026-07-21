# EasySudoku three-minute demo script

Target: finish by 3:00. Use `examples/demo_sudoku.png` and a clean browser profile. Do not claim an OCR percentage, latency, public deployment URL, Docker runtime result, or Codex Session ID that has not been verified.

## 0:00–0:20 — Problem and users

Show the landing screen.

> Most Sudoku apps reveal answers. EasySudoku is for learners who want the next justified move. It turns a photo or typed puzzle into solver-verified, step-by-step teaching.

Mention that runtime reasoning is deterministic human rules plus Z3, not an LLM guessing Sudoku moves.

## 0:20–1:35 — Core learning flow

1. Choose Chinese and upload `examples/demo_sudoku.png`.
2. Explain that OpenCV corrects the board and the local ONNX model recognizes digits without an external OCR service.
3. Point out that recognized cells are still editable. Correct one digit and restore it to demonstrate the review gate.
4. Confirm the givens so the starting clues become locked.
5. Select an empty cell to show candidates.
6. Click **推导下一步**. Point to the target, conclusion, reason, verification, and the new history entry.
7. Switch Brief → Teaching → Technical to show the same structured deduction at different depths.

Say explicitly: the included PNG is a reproducible synthetic integration fixture, not evidence of camera-photo accuracy.

## 1:35–1:55 — Language, history, and recovery

Switch to English and show that labels, rule names, and structured explanations change together. Move backward and forward in history, refresh once, and show that the board, history, language, explanation mode, and image preview return.

## 1:55–2:25 — Architecture and trust boundary

Show the README architecture diagram or keep the application visible while narrating:

> Image or manual input becomes an editable board. Candidate analysis tries human rules first. Z3 and UNSAT Core verify harder forced values. The backend returns a structured step; Vue localizes it and stores replayable history.

Emphasize that OCR may require correction, while confirmed givens and solver constraints remain the source of truth.

## 2:25–2:45 — Author decisions and Codex assistance

> The author chose the teaching-first product direction, local OCR, deterministic solver trust model, bilingual UX, and submission boundaries. Codex GPT-5.6 sol completed the repository audit, Vue/FastAPI hardening, automated tests, Docker/CI configuration, contribution audit, and submission documentation. The contribution audit is complete; no Codex Session ID or successful local Docker container run is claimed.

## 2:45–3:00 — Value and next step

Return to the explanation/history view.

> EasySudoku makes a solver's certainty useful to a learner: inspectable input, one justified move, and a replayable explanation. Next, we will add advanced human rules and a labeled real-photo OCR evaluation before publishing accuracy claims.

Stop before 3:00.

## Recording checklist

```bash
cd ~/EasySudoku
source venv312/bin/activate
./scripts/npm-safe.sh --prefix frontend run type-check
./scripts/npm-safe.sh --prefix frontend run build
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

In a second terminal:

```bash
cd ~/EasySudoku/frontend
EASYSUDOKU_BASE_URL=http://127.0.0.1:8000 npm run test:smoke
```

Before recording, verify the browser language gate, fixed upload, correction, confirmation, next step, all three explanation modes, history replay, and refresh restoration. Verify a public link in a clean browser only after deployment; otherwise do not claim one.
