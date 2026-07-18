# EasySudoku Evaluation

This document separates reproducible repository checks from unmeasured product claims. Results are updated only after the named command actually runs in the current checkout.

## Baseline recorded on 2026-07-18

| Check | Command | Result |
|---|---|---|
| Z3 solve and UNSAT fixture | `./venv312/bin/python test_phase1.py` | Passed |
| Iterative deductions | `./venv312/bin/python test_phase2.py` | Passed; fixed puzzle completed in 51 consistent steps |
| Vision module structure | `./venv312/bin/python test_phase3.py` | Passed |
| TypeScript | `./scripts/npm-safe.sh --prefix frontend run type-check` | Passed |
| Vue production build | `./scripts/npm-safe.sh --prefix frontend run build` | Passed; Vite transformed 54 modules |

The local WSL `npm` command currently resolves to a Windows-mounted shim without a compatible Linux `node`. It must not be treated as a valid pass merely because that shim can return exit code 0 after printing `node: not found`. Docker and CI use a clean Node image; local verification uses the repository safety wrapper until the host PATH is repaired.

## Expanded verification recorded on 2026-07-18

| Check | Command | Result |
|---|---|---|
| Deterministic demo contract | `./venv312/bin/python test_demo.py` | Passed; puzzle has a unique expected solution and the generated PNG OCR matches its fixed grid |
| FastAPI production behavior | `./venv312/bin/python test_api.py` | Passed; 5 tests cover health/version, frontend policy, API 404, upload validation, and fixed OCR |
| TypeScript after UI expansion | `./scripts/npm-safe.sh --prefix frontend run type-check` | Passed |
| Vue production build after UI expansion | `./scripts/npm-safe.sh --prefix frontend run build` | Passed; Vite transformed 55 modules |
| Playwright end-to-end suite | direct Playwright CLI with the repository config | Passed; 18/18 tests across desktop and mobile-390 projects |
| Dockerfile static build check | `docker build --check .` | Passed on the final Dockerfile; BuildKit reported no warnings |

The Playwright suite includes the language gate, Chinese content leakage check, solve confirmation branches, fixed OCR upload and correction, confirmation, history and persistence restoration, localStorage/IndexedDB clearing, structured upload/network errors, duplicate-action prevention, and responsive assertions at 360×800, 390×844, 768×1024, and 1440×900. These are automated browser viewport checks, not claims about testing on four physical devices.

## Metrics intentionally not claimed

- Real-photo OCR accuracy for the current submission: **TODO — run a labeled evaluation and publish the fixture list**.
- OCR latency distribution: **TODO — define hardware, warm-up, repetitions, and percentiles**.
- API/end-to-end latency: **TODO — define environment and measurement method**.
- Number and diversity of real-world test images: **TODO — assemble a consented, labeled set**.

Historical development notes contain earlier OCR experiments, but this submission does not reuse their percentage as a current evaluation result without rerunning the exact dataset and script.

## Deterministic demo fixture

`examples/demo_sudoku.png` is generated from a fixed JSON puzzle. It is intended to test upload plumbing and a clean synthetic OCR path. It does not represent camera perspective, glare, handwriting, printing variation, compression, or background clutter, so its result must not be reported as real-photo accuracy.

## Final verification matrix

The final audit must record real outcomes for:

- Python backend and API tests;
- `npm run type-check` and `npm run build` in a valid Node environment;
- the complete Playwright suite;
- Docker image build;
- container `/health` response;
- `/` returning the Vue build;
- production behavior when the Vue build is missing;
- legacy behavior only with `ALLOW_LEGACY_FRONTEND=1`.

The Python/API/TypeScript/Vue/Playwright checks and the final two production frontend-policy behaviors passed in the current checkout. A full local Docker image and container run are not recorded as passed: two attempts were stopped after Docker Hub base-image downloads remained extremely slow (approximately 15 minutes and 7 minutes without completing). The checked-in CI performs the full Docker build on a clean GitHub runner; its result and a container `/health` check must still be recorded before submission.

No container health result is inferred from the static Dockerfile check.
