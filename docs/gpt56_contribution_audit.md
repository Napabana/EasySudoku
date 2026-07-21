# Codex GPT-5.6 sol Contribution Audit

Audit date: 2026-07-21

## Verified model and evidence

The confirmed model used for the Build Week engineering work was **Codex GPT-5.6 sol**. This audit is grounded in the current nine-commit public release history, especially `171a34c` (`Migrate frontend to Vue and add structured steps`), `b621577` (`Harden hackathon submission`), `915a61c` (`Verify production container in CI`), and the final documentation/provenance cleanup. It does not invent a Codex Session ID or infer unverified external-platform results.

## Modules inspected or modified

### Product and frontend

Codex GPT-5.6 sol inspected or modified:

- the Vue 3/TypeScript application shell and Sudoku UI components;
- bilingual locale files and Brief/Teaching/Technical explanation rendering;
- API response/error adaptation in `frontend/src/services/sudokuApi.ts`;
- board, candidate, history, confirmation, upload, persistence, and demo-loading flows;
- Playwright configuration, helpers, smoke tests, localization, solve, OCR/persistence, error, duplicate-action, and responsive tests.

### Backend and deterministic reasoning boundary

Codex GPT-5.6 sol inspected or modified:

- `main.py` for structured API responses, Vue serving, `/health`, `/version`, API-safe 404 handling, bounded uploads, and structured OCR errors;
- `smt_engine.py` and `heuristic_engine.py` in `171a34c` to attach structured step metadata to existing deterministic results;
- backend and demo-contract tests in `test_api.py` and `test_demo.py`.

The structured metadata work did not replace the Z3 model, UNSAT Core reasoning, Hidden Single, Naked Pair, or OCR algorithms. The submission-hardening commit `b621577` did not modify `smt_engine.py`, `heuristic_engine.py`, `vision.py`, or `models/sudoku_chars74k.onnx`.

### Build, release, and documentation

Codex GPT-5.6 sol inspected or modified:

- `Dockerfile`, `.dockerignore`, launch/build flow, and `scripts/npm-safe.sh`;
- `.github/workflows/ci.yml` and `requirements-dev.txt`;
- deterministic demo JSON/PNG assets and their OpenCV generator;
- README, architecture, Build Week, evaluation, contribution-audit, provenance, and demo-script documents.
- the contribution audit, third-party notices, and OCR model card.

## Tests executed by Codex GPT-5.6 sol

The recorded local results are:

- `test_phase1.py`: passed;
- `test_phase2.py`: passed, with the fixed puzzle completed in 51 consistent steps;
- `test_phase3.py`: passed;
- `test_demo.py`: passed, including unique-solution and synthetic-fixture OCR checks;
- `test_api.py`: 5 checks passed;
- frontend type-check: passed;
- Vue production build: passed, with 55 transformed modules in the final recorded run;
- Playwright: 18/18 tests passed across the configured desktop and mobile projects;
- `docker build --check .`: passed with no Dockerfile warnings.
- GitHub Actions run [29636708583](https://github.com/Napabana/EasySudoku/actions/runs/29636708583): passed for production image build, container start, Docker health, `/health`, `/`, and cleanup.

A full local Docker image build and running-container check were not completed, but the equivalent clean-runner workflow passed in GitHub Actions. The verified container result comes from that CI run, not from the earlier static Dockerfile check.

## Decisions made by the author

The project author decided and approved:

- that EasySudoku should teach the next justified move rather than only reveal a full answer;
- that runtime Sudoku conclusions must come from deterministic rules and Z3, not an LLM;
- that OCR should remain local and reviewable before givens are confirmed;
- that the interface should support Chinese/English explanations, multiple explanation depths, history, and browser persistence;
- that submission hardening should preserve the existing Z3, Sudoku-rule, and OCR algorithms;
- that unmeasured OCR accuracy, latency, deployment status, links, and disclosure identifiers must not be claimed.

## Manual items not completed by the model

The following remain human responsibilities:

- confirm the Kaggle Notebook reuse permission, exact Chars74K subset/terms, and intended ONNX weight-distribution license; attribution is already recorded in `THIRD_PARTY_NOTICES.md` and `models/MODEL_CARD.md`;
- optionally reproduce the CI-verified Docker image/container flow locally if local evidence is required;
- deploy the application and verify the public URL in a clean browser;
- record and publish the demonstration video;
- complete Devpost fields, screenshots, links, and final submission review;
- identify and decide whether to disclose the correct Codex Session ID;
- perform the final legal, privacy, licensing, and submission review.

The MIT License, public GitHub repository, and CI production-container verification are confirmed complete. No unverified OCR metric, latency, local Docker result, deployment URL, video URL, Devpost status, or Codex Session ID is asserted here.
