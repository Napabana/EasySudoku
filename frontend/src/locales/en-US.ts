export default {
  app: {
    title: "EasySudoku",
    subtitle: "An explainable Sudoku tutor with photo recognition",
    languageFirst: "Choose a language to start",
    continue: "Continue",
    board: "Sudoku Board",
    actions: "Actions",
    explanation: "Explanation",
    history: "History"
  },
  language: {
    label: "Language",
    zh: "中文",
    en: "English"
  },
  modes: {
    label: "Explanation style",
    brief: "Brief",
    teaching: "Teaching",
    technical: "Technical"
  },
  controls: {
    upload: "Upload image",
    confirm: "Confirm givens",
    confirmed: "Puzzle confirmed",
    edit: "Edit puzzle",
    nextStep: "Next step",
    hint: "Hint selected cell",
    solve: "Solve",
    clear: "Clear session",
    undo: "Back",
    redo: "Forward",
    showCandidates: "Show candidates",
    hideCandidates: "Hide candidates",
    close: "Close",
    chooseFile: "Choose image",
    previewImage: "Preview image",
    puzzleLocked: "✓ Puzzle locked",
    puzzleEditable: "Puzzle editable"
  },
  loading: {
    analyzing: "Analyzing..."
  },
  confirm: {
    cancel: "Cancel",
    solveTitle: "Reveal the complete solution?",
    solveBody: "This will end the step-by-step solving session and fill the complete solution.",
    revealSolution: "Reveal solution",
    clearTitle: "Clear the current session?",
    clearBody: "This will remove the current board, deduction history, and uploaded image.",
    clearSession: "Clear session",
    branchTitle: "Replace later history?",
    branchBody: "You are viewing an older history point. A new step will replace all later history.",
    replaceHistory: "Replace history"
  },
  statusPanel: {
    title: "Puzzle status",
    filledCells: "Filled cells",
    currentStep: "Current step",
    difficultyReached: "Difficulty reached",
    locked: "Locked",
    editing: "Editing"
  },
  shortcuts: {
    title: "Shortcuts",
    next: "Next step",
    candidates: "Toggle candidates",
    closePreview: "Close preview"
  },
  a11y: {
    empty: "empty",
    noValue: "no value",
    cell: "Row {row}, column {col}, value {value}, state {origin}"
  },
  technical: {
    humanRule: "Human rule"
  },
  status: {
    ready: "Upload an image or enter the givens, then confirm the board.",
    uploading: "Recognizing image...",
    uploaded: "Recognition finished. Review the board, correct it, then confirm the givens.",
    confirmed: "The initial board is locked. You can start deriving steps.",
    editing: "Editing is enabled. You can update the initial board.",
    deriving: "Deriving the next step...",
    hinting: "Analyzing the selected cell...",
    solving: "Solving...",
    solved: "The puzzle has been solved.",
    noStep: "No single logical step is available. The puzzle may need a harder technique or input review.",
    restored: "Restored your previous session."
  },
  errors: {
    invalidCell: "Select an empty cell first.",
    locked: "The board is locked. Use “Edit givens” before changing it.",
    confirmFirst: "Confirm the initial board first.",
    uploadFailed: "Image recognition failed",
    requestFailed: "Request failed",
    solveFailed: "No solution was found, or the input contains a conflict.",
    storageFailed: "Local save failed. You can keep using the current session."
  },
  legend: {
    given: "Given",
    user: "User input",
    derived: "Derived",
    target: "Current target"
  },
  rules: {
    hiddenSingle: "Hidden Single",
    nakedPair: "Naked Pair",
    smtVerification: "Advanced deduction / SMT verification",
    unknown: "Deduction"
  },
  difficulty: {
    basic: "Basic",
    intermediate: "Intermediate",
    advanced: "Advanced",
    smt: "SMT"
  },
  explanations: {
    intro: "Select an empty cell to inspect candidates, or use “Next step” to start.",
    hiddenSingle: "In the related row, column, or box, cell ({row},{col}) is the only place for {value}.",
    nakedPair: "After the naked-pair elimination, cell ({row},{col}) has only candidate {value}.",
    smtStep: "Cell ({row},{col}) can only be {value} after advanced constraint verification.",
    briefStep: "Cell ({row},{col}) = {value}.",
    technicalStep: "Rule: {rule}\nDifficulty: {difficulty}\nVerification: {verification}\nTarget cell: row {row}, column {col}\nConclusion: place {value} in this cell\nEliminated candidates: {removedCount}",
    hintCandidates: "Candidates for ({row},{col}): {candidates}",
    noCandidates: "Cell ({row},{col}) has no legal candidates.",
    eliminatedCandidates: "{count} candidates were eliminated"
  },
  explanationGroups: {
    target: "Target",
    conclusion: "Conclusion",
    why: "Why",
    verification: "Verification",
    placeValue: "Place {value} in {target}"
  },
  history: {
    empty: "No deduction history yet.",
    item: "Step {index}",
    compactItem: "Step {index} · {rule}",
    current: "Current",
    target: "R{row}C{col} = {value}",
    progress: "Step {current} of {total}"
  },
  image: {
    uploaded: "Uploaded image",
    noImage: "No image uploaded",
    noFileSelected: "No image selected",
    clickToPreview: "Click the file name to preview the original image"
  }
};
