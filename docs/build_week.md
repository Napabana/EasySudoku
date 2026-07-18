# Build Week Development Audit

Audit date: 2026-07-18

## Evidence boundary

The repository has five commits in the current `main` history. Commits `8e8e856` through `639f9da` are dated 2026-05-26/27. Commit `171a34c` is dated 2026-07-17 and is titled `Migrate frontend to Vue and add structured steps`. The before/during classification below follows that history rather than memory or submission marketing.

## Present before Build Week

- Python/FastAPI Sudoku tutor prototype.
- Basic single-page HTML frontend under `templates/index.html`.
- OpenCV grid detection and local ONNX digit recognition.
- Z3 constraint model, assumptions, tracked constraints, and UNSAT Core explanations.
- Candidate pre-checking plus Hidden Single and Naked Pair heuristics.
- Phase 1–3 Python scripts for solver, iterative deduction, and vision structure.
- Cross-platform launch scripts and the initial Docker packaging.

## Added or substantially improved during Build Week

Commit `171a34c` added or changed the following areas:

- Vue 3, TypeScript, Vite, and Tailwind frontend migration.
- Responsive desktop/mobile layout.
- English/Chinese UI and structured explanation localization.
- Brief, Teaching, and Technical explanation modes.
- Structured deduction-step API fields while retaining legacy fields.
- History back/forward/jump behavior and branch truncation.
- localStorage session recovery and IndexedDB uploaded-image recovery.
- Playwright smoke coverage for the main path and responsive overflow.
- Multi-stage Docker build that compiles the Vue frontend.

The 2026-07-18 submission-hardening iteration is planned to add deterministic demo assets, deeper E2E coverage, production frontend safeguards, `/health`, `/version`, upload validation, reproducible `npm ci` container builds, CI, and submission documentation. Completion is tracked in `docs/2026-07-18-task-plan.md` and must be backed by test output.

## Human and AI roles

The author chose the product direction and trust model: teach one step at a time, keep OCR local, prioritize recognizable Sudoku rules, use Z3 as the correctness fallback, preserve compatibility, and avoid requiring user accounts.

Codex assisted with repository analysis, incremental frontend/backend work, test design and execution, and documentation. Sudoku answers are produced by deterministic rules and Z3, not by an LLM. The 2026-07-18 iteration uses Codex 5.6 sol. GPT-5.6 contribution remains pending final audit; this document does not claim a GPT-5.6 record or a Codex Session ID.
