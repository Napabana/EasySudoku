# Third-Party Notices

This document records the external material used to produce EasySudoku's OCR
model. It is an attribution and provenance record, not legal advice and not a
grant of rights to any third-party work.

## Kaggle training-code reference

- **Author:** Karnika Kapoor (`karnikakapoor` on Kaggle)
- **Title:** *Sudoku Solutions From Image: Computer Vision*
- **Source:** https://www.kaggle.com/code/karnikakapoor/sudoku-solutions-from-image-computer-vision
- **EasySudoku modified version:** the project author's adapted digit-model
  training and ONNX-export workflow. Its exact source file and version are not
  currently preserved in this repository.
- **Use in EasySudoku:** the EasySudoku project author used this Notebook as a
  starting reference, modified the training code for the project's digit-model
  workflow, trained the model, and exported the resulting ONNX artifact. The
  included `models/sudoku_chars74k.onnx` is therefore author-trained; it is not
  a downloaded third-party pretrained model.

As checked on 2026-07-21, the Notebook page did not display an explicit software
license. EasySudoku does **not** describe the Notebook as Apache-2.0 or MIT.
Permission and license terms applicable to reused or adapted Notebook code must
be confirmed with the Notebook author or another authoritative record. The
original Notebook is not redistributed in this repository. The exact modified
training source and a line-by-line change record are not currently included in
the repository.

## Chars74K dataset

- **Dataset:** Chars74K, *Character Recognition in Natural Images*
- **Dataset / paper attribution:** T. E. de Campos, B. R. Babu, and M. Varma
- **Official project page:** https://teodecampos.github.io/chars74k/
- **Original University of Surrey page:**
  http://www.ee.surrey.ac.uk/CVSSP/demos/chars74k/
- **Use in EasySudoku:** the project author used Chars74K digit data to train
  the 10-class OCR model. EasySudoku does not redistribute the original
  Chars74K image files.

The official project page asks users to acknowledge the dataset source and cite
the paper below in related publications. That notice is not represented here as
an MIT license, and the EasySudoku MIT License does not relicense Chars74K.
Users who retrain or redistribute data should consult the official source and
confirm the terms that apply to the exact Chars74K subset they use.

### Required dataset citation

T. E. de Campos, B. R. Babu, and M. Varma, “Character Recognition in Natural
Images,” in *Proceedings of the International Conference on Computer Vision
Theory and Applications (VISAPP)*, Lisbon, Portugal, February 2009.

Publication record:
https://www.microsoft.com/en-us/research/publication/character-recognition-in-natural-images/

## Author-trained ONNX artifact

`models/sudoku_chars74k.onnx` was trained and exported by the EasySudoku project
author from the modified training workflow described above. Its presence does
not transfer or expand rights in Chars74K or the referenced Notebook. A separate
license for the model artifact has not been declared in this repository, and
EasySudoku does not describe the ONNX artifact as MIT- or Apache-2.0-licensed.
The project author should confirm the intended model-weight distribution terms after
resolving the upstream training-code and dataset terms.

## Scope of the EasySudoku MIT License

The repository's `LICENSE` applies only to original EasySudoku code. It does
not relicense Chars74K, the Kaggle Notebook, or any other third-party material.
Each external work remains subject to its own terms.
