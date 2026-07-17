export default {
  app: {
    title: "EasySudoku",
    subtitle: "拍照识别与可解释数独推导导师",
    languageFirst: "请选择语言开始",
    continue: "继续",
    board: "数独盘面",
    actions: "操作",
    explanation: "推导说明",
    history: "历史记录"
  },
  language: {
    label: "语言",
    zh: "中文",
    en: "English"
  },
  modes: {
    label: "解释风格",
    brief: "简洁",
    teaching: "教学",
    technical: "技术"
  },
  controls: {
    upload: "上传图片",
    confirm: "确认初始盘面",
    confirmed: "盘面已确认",
    edit: "重新编辑盘面",
    nextStep: "推导下一步",
    hint: "获取选中格提示",
    solve: "直接求解",
    clear: "清除当前会话",
    undo: "上一步",
    redo: "下一步",
    showCandidates: "显示候选数",
    hideCandidates: "隐藏候选数",
    close: "关闭",
    chooseFile: "选择图片",
    previewImage: "查看原图",
    puzzleLocked: "✓ 盘面已锁定",
    puzzleEditable: "盘面可编辑"
  },
  loading: {
    analyzing: "分析中..."
  },
  confirm: {
    cancel: "取消",
    solveTitle: "显示完整答案？",
    solveBody: "这会结束当前逐步推导流程，并直接填入完整解。",
    revealSolution: "显示答案",
    clearTitle: "清除当前会话？",
    clearBody: "这会删除当前盘面、历史记录和已上传图片。",
    clearSession: "清除会话",
    branchTitle: "替换后续历史？",
    branchBody: "你当前停在旧历史节点。继续推导会删除该节点之后的历史分支。",
    replaceHistory: "替换历史"
  },
  statusPanel: {
    title: "盘面状态",
    filledCells: "已填格数",
    currentStep: "当前步骤",
    difficultyReached: "达到难度",
    locked: "已锁定",
    editing: "编辑中"
  },
  shortcuts: {
    title: "快捷键",
    next: "推导下一步",
    candidates: "显示/隐藏候选数",
    closePreview: "关闭预览"
  },
  a11y: {
    empty: "空格",
    noValue: "无数字",
    cell: "第 {row} 行，第 {col} 列，值 {value}，状态 {origin}"
  },
  technical: {
    humanRule: "人类规则"
  },
  status: {
    ready: "上传图片或手动输入已知数字，然后确认初始盘面。",
    uploading: "正在识别图像...",
    uploaded: "识别完成。请检查并修正盘面，然后确认初始盘面。",
    confirmed: "初始盘面已锁定，可以开始推导。",
    editing: "已进入编辑模式，可以修改初始盘面。",
    deriving: "正在推导下一步...",
    hinting: "正在分析选中格...",
    solving: "正在求解...",
    solved: "已直接求解完成。",
    noStep: "当前盘面无法通过单步推导继续，可能需要更高级的技巧或检查输入。",
    restored: "已恢复上次会话。"
  },
  errors: {
    invalidCell: "请先选择一个空格。",
    locked: "初始盘面已锁定，点击“重新编辑盘面”后才能修改。",
    confirmFirst: "请先确认初始盘面。",
    uploadFailed: "图片识别失败",
    requestFailed: "请求失败",
    solveFailed: "无解或输入存在冲突。",
    storageFailed: "本地保存失败，当前会话仍可继续使用。"
  },
  legend: {
    given: "初始数字",
    user: "用户输入",
    derived: "推导数字",
    target: "当前目标"
  },
  rules: {
    hiddenSingle: "隐性唯一数",
    nakedPair: "显性数对",
    smtVerification: "高级推导 / SMT 验证",
    unknown: "推导步骤"
  },
  difficulty: {
    basic: "基础",
    intermediate: "中级",
    advanced: "高级",
    smt: "SMT"
  },
  explanations: {
    intro: "选择一个空格查看候选数，或点击“推导下一步”开始。",
    hiddenSingle: "在相关行、列或宫中，位置 ({row},{col}) 是数字 {value} 的唯一可放位置。",
    nakedPair: "数对排除后，位置 ({row},{col}) 只剩下候选数 {value}。",
    smtStep: "位置 ({row},{col}) 经过高级约束验证后只能填 {value}。",
    briefStep: "位置 ({row},{col}) = {value}。",
    technicalStep: "规则：{rule}\n难度：{difficulty}\n验证方式：{verification}\n目标格：第 {row} 行第 {col} 列\n结论：该格填 {value}\n候选数排除数量：{removedCount}",
    hintCandidates: "位置 ({row},{col}) 的候选数：{candidates}",
    noCandidates: "位置 ({row},{col}) 没有合法候选数。",
    eliminatedCandidates: "排除了 {count} 个候选数"
  },
  explanationGroups: {
    target: "目标",
    conclusion: "结论",
    why: "原因",
    verification: "验证",
    placeValue: "在 {target} 填入 {value}"
  },
  history: {
    empty: "还没有推导历史。",
    item: "第 {index} 步",
    compactItem: "第 {index} 步 · {rule}",
    current: "当前",
    target: "R{row}C{col} = {value}",
    progress: "第 {current} / {total} 步"
  },
  image: {
    uploaded: "已上传图片",
    noImage: "尚未上传图片",
    noFileSelected: "未选择图片",
    clickToPreview: "点击文件名查看原图"
  }
};
