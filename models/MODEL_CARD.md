# EasySudoku OCR Model Card

## Model overview

| Field | Value |
|---|---|
| Artifact | `sudoku_chars74k.onnx` |
| SHA-256 | `a4fa6608d0d6a3b5b3ef287f811f810ace5cc737f36ce38a1daf6ec6114deec6` |
| Task | Sudoku-cell digit classification |
| Classes | 10 classes (`0`–`9`) |
| Format | ONNX |
| Trainer / exporter | EasySudoku project author |
| Pretrained origin | Author-trained artifact; not a downloaded third-party pretrained model |
| Training data origin | Chars74K digit data |
| Model-weight license | Not separately declared; confirmation remains required |

## Provenance

The EasySudoku project author trained and exported this model using Chars74K
digit data. The initial training implementation referenced Karnika Kapoor's
Kaggle Notebook, [*Sudoku Solutions From Image: Computer
Vision*](https://www.kaggle.com/code/karnikakapoor/sudoku-solutions-from-image-computer-vision),
and was modified for EasySudoku's digit-model training and ONNX export workflow.
This is the “EasySudoku modified version” referenced in this card. The
repository does not contain the original Notebook, the exact modified
training source, or a reproducible training manifest.

The Kaggle page did not display an explicit software license when checked on
2026-07-21. This model card therefore makes no Apache-2.0 or MIT claim for the
Notebook or adapted code. See [`THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md)
for the current attribution and open questions.

## Dataset

The training data came from the digit portion of [Chars74K, *Character
Recognition in Natural Images*](https://teodecampos.github.io/chars74k/). The
raw Chars74K images are not included in EasySudoku.

Please cite:

> T. E. de Campos, B. R. Babu, and M. Varma, “Character Recognition in Natural
> Images,” in *Proceedings of the International Conference on Computer Vision
> Theory and Applications (VISAPP)*, Lisbon, Portugal, February 2009.

The dataset page asks users to acknowledge the source and cite that paper in
related publications. Chars74K is not described as MIT-licensed by this project.

## Runtime interface

EasySudoku loads the artifact locally through OpenCV DNN. The current inference
integration prepares a white-background, black-digit tensor normalized to
`[0, 1]`, with shape `(1, 32, 32, 1)` (NHWC), and consumes a 10-class output.
This card documents the existing integration only; it does not change the model
or OCR implementation.

## Intended use

The model is intended to classify digits extracted from cells of a photographed
or scanned 9×9 Sudoku grid. OCR output is shown in an editable grid so that a
user can correct recognition errors before logical solving.

It is not intended for identity, handwriting-authorship, biometric, safety-
critical, or general document-recognition decisions.

## Limitations and evaluation status

- Recognition quality depends on perspective correction, lighting, grid-line
  removal, font style, crop quality, and similarity to the training data.
- The repository does not currently include a reproducible training script,
  exact data manifest, split, random seed, hyperparameters, framework versions,
  or training/evaluation report for this artifact.
- No metric is asserted in this card without a preserved evaluation artifact.
- Users should review and correct OCR output before relying on the puzzle state.

## Licensing and distribution

The repository's MIT License covers only original EasySudoku code. It does not
relicense Chars74K or Karnika Kapoor's Notebook. The author-trained ONNX
artifact is not described here as MIT- or Apache-2.0-licensed. A license for
distributing those weights has not been separately declared and should be
confirmed after the applicable upstream terms are
verified.

## Information still needed for reproducibility

- The exact modified training Notebook or script and its version or commit.
- The precise Chars74K archive(s) and digit subset used.
- Data preprocessing, augmentation, train/validation/test split, and deduping.
- Model architecture, optimizer, loss, epochs, batch size, seed, and framework
  versions.
- ONNX export command, opset, and source checkpoint identifier.
- Preserved evaluation inputs, methodology, and results.
- The project author's intended license for the ONNX weights.
