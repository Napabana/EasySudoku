# EasySudoku Submission Checklist

Unchecked items are incomplete or require manual/external verification. Do not mark them complete based only on generated instructions.

## Repository and licensing

- [ ] Add and verify an MIT `LICENSE` file owned by the project author.
- [ ] Confirm the GitHub repository is public and contains the intended commit only.
- [ ] Review the ONNX model/dataset license and include required attribution.
- [ ] Review privacy wording: uploaded images are processed locally by the app server and persisted in the browser; verify deployment logging/retention separately.

## Build Week evidence

- [x] README distinguishes pre-Build-Week work from Build Week work using Git history.
- [x] README separates author decisions from Codex assistance.
- [x] Runtime Sudoku answers are documented as deterministic rule/Z3 output rather than LLM guesses.
- [ ] Add the real Codex Session ID after verifying the correct session to disclose.
- [ ] Complete the final GPT-5.6 contribution audit; current status is pending.

## Product verification

- [x] Record final Python test results.
- [x] Record final TypeScript and Vue build results.
- [x] Record final Playwright results.
- [ ] Record final Docker build and container `/health` results.
- [ ] Check 360×800, 390×844, 768×1024, and 1440×900 layouts on actual browsers/devices where possible.
- [x] Confirm no private path, environment value, uploaded image, or credential is exposed by `/health` or `/version`.

## External submission tasks

- [ ] Replace `LIVE_DEMO_URL_PENDING` only after opening and testing the deployed URL in a clean browser.
- [ ] Publish a public demonstration video and verify its permissions.
- [ ] Complete the Devpost description, screenshots, technology list, and team information.
- [ ] Add the verified public GitHub URL to Devpost.
- [ ] Add the verified public video URL to Devpost.
- [ ] Add the verified live demo URL to Devpost.

## Final content review

- [ ] Run the three-minute script without exceeding 3:00.
- [ ] Ensure the demo does not claim unmeasured OCR accuracy, latency, or sample counts.
- [ ] Ensure synthetic demo OCR is described as an integration fixture, not real-photo evidence.
- [ ] Verify all links from README.
- [ ] Remove or explain any submission-only TODO that judges would encounter.
