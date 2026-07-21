# Build Week Development Audit

Audit date: 2026-07-21

## Evidence boundary

The current public release history contains nine commits. The evidence boundary is:

- Before Build Week: 4 commits, `8e8e856` through `639f9da`, dated 2026-05-26 to 2026-05-27.
- Build Week: 4 commits—`171a34c` (`Migrate frontend to Vue and add structured steps`, 2026-07-17), `8ee8689` (`Create LICENSE`, 2026-07-17), `b621577` (`Harden hackathon submission`, 2026-07-18), and `915a61c` (`Verify production container in CI`, 2026-07-18).
- Final public-release cleanup: 1 commit dated 2026-07-21, covering submission status, OCR provenance, and repository hygiene.

This classification follows the checked-in Git history. Submission hardening was completed in `b621577`, production-container verification was completed in `915a61c`, and the final public-release cleanup synchronized audit/provenance documents while removing internal process artifacts. Remaining external and licensing decisions are tracked separately and are not treated as unfinished repository implementation.

## Present before Build Week

- Python/FastAPI Sudoku tutor prototype.
- Basic single-page HTML frontend under `templates/index.html`.
- OpenCV grid detection and local ONNX digit recognition.
- Z3 constraint model, assumptions, tracked constraints, and UNSAT Core explanations.
- Candidate pre-checking plus Hidden Single and Naked Pair heuristics.
- Phase 1–3 Python scripts for solver, iterative deduction, and vision structure.
- Cross-platform launch scripts and the initial Docker packaging.

## Completed during Build Week

### `171a34c` — Vue migration and structured steps

- Vue 3, TypeScript, Vite, and Tailwind frontend migration.
- Responsive desktop/mobile layout.
- English/Chinese UI and structured explanation localization.
- Brief, Teaching, and Technical explanation modes.
- Structured deduction-step fields for heuristic and Z3 results while retaining compatibility fields.
- History back/forward/jump behavior and branch truncation.
- localStorage session recovery and IndexedDB uploaded-image recovery.
- Playwright smoke coverage for the main path and responsive overflow.
- Multi-stage Docker build that compiles the Vue frontend.

### `8ee8689` — MIT License

- Added the repository's MIT `LICENSE` file.

### `b621577` — Harden hackathon submission

The hardening commit changed 38 files and completed the planned repository work:

- Added the public architecture, evaluation, Build Week, and demo documentation.
- Added deterministic demo puzzle/solution JSON, the OpenCV generator, synthetic PNG fixture, and the UI action for loading the demo puzzle.
- Added `/health` and `/version`, explicit production frontend behavior, API-safe 404 handling, bounded upload validation, and structured OCR errors.
- Expanded localized frontend error handling, stable test IDs, solve confirmation coverage, OCR correction flow, persistence restoration, and dual-storage clearing.
- Fixed the session-clear persistence race that could re-save cleared state.
- Expanded Playwright coverage to 18 passing tests across the configured desktop and mobile projects, including the required viewport assertions.
- Added deterministic demo and FastAPI API tests, production Docker configuration, and a GitHub Actions workflow for Python, frontend, Playwright, and Docker checks.
- Reworked the README and three-minute submission script without inventing OCR metrics, deployment URLs, Docker runtime success, or a Codex Session ID.

The commit did not modify `smt_engine.py`, `heuristic_engine.py`, `vision.py`, or the ONNX model.

### `915a61c` — CI production-container verification

- Starts the built `easysudoku:ci` image as a real container on port 8001.
- Polls the Dockerfile `HEALTHCHECK` until the container becomes healthy or fails.
- Requests the container's `/health` and `/` endpoints after it becomes healthy.
- Always removes the CI container.
- GitHub Actions run [29636708583](https://github.com/Napabana/EasySudoku/actions/runs/29636708583) completed successfully; the image build, container start, health verification, root-page request, and cleanup steps all reported `success`.

This clean-runner result verifies the production Docker image and running-container health. A full local Docker build remains unperformed because the local Docker Hub downloads were stopped for low throughput; it is not presented as a local pass.

## Final submission documentation

### Final public-release cleanup

- Completed the Codex GPT-5.6 sol contribution audit and synchronized the README, Build Week, evaluation, demo, and repository status.
- Added `THIRD_PARTY_NOTICES.md` and `models/MODEL_CARD.md`.
- Documented that the ONNX artifact was trained and exported by the project author from Chars74K digit data and was not downloaded as third-party pretrained weights.
- Recorded Karnika Kapoor's *Sudoku Solutions From Image: Computer Vision* as the modified training reference without assigning it an unsupported license.
- Added the Chars74K source and VISAPP 2009 citation, while keeping upstream reuse and model-weight distribution terms open for author confirmation.
- Changed documentation only; it did not modify the ONNX artifact, OCR inference, Z3, or Sudoku-rule code.

## Human and AI roles

### Author decisions

The author chose and approved:

- the teaching-first product direction—show one justified next step rather than only a completed grid;
- local, reviewable OCR and confirmed givens as the trust boundary;
- recognizable Sudoku rules first and Z3 as the deterministic correctness fallback;
- Vue/FastAPI integration, structured bilingual explanations, browser persistence, and compatibility constraints;
- the scope boundary that preserved existing OCR and solver algorithms during submission hardening;
- the requirement not to invent metrics, deployment status, external links, or disclosure records.

### Codex GPT-5.6 sol contribution

Codex GPT-5.6 sol completed the Build Week engineering and final documentation work recorded above: repository/history analysis, Vue and FastAPI implementation, structured step metadata integration, responsive/i18n/history/persistence work, test design and execution, demo fixtures, production hardening, Docker/CI configuration, contribution auditing, provenance documentation, and submission documentation.

In `171a34c`, its changes to `smt_engine.py` and `heuristic_engine.py` added structured response metadata for the existing heuristic and SMT results; they did not replace the Z3 model, UNSAT Core process, or Sudoku rule algorithms. In `b621577`, those core modules and `vision.py` were not changed.

Sudoku answers remain deterministic rule/Z3 output, not LLM-generated moves. The completed contribution record is in `docs/gpt56_contribution_audit.md`.

## Still outside the completed repository work

- Optional reproduction of the now-CI-verified Docker flow on the local machine.
- Online deployment and clean-browser verification of the final URL.
- Public demonstration video and Devpost completion.
- Codex Session ID selection and disclosure.
- Kaggle Notebook reuse permission, exact Chars74K subset/terms, and the intended ONNX weight-distribution license.
