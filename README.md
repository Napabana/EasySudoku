# EasySudoku

基于 Z3 SMT Solver 的数独逐步推导导师。用户可以上传数独照片或手动输入题目，系统先用本地 OCR 识别盘面，再通过人类规则和 SMT 验证逐步推导下一步，并用中英文解释每一步为什么成立。

## 功能特性

- **逐步 SMT 推导** — 基于 Z3 的 UNSAT Core 提取，精确到具体行/列/宫的冲突解释
- **启发式规则引擎** — Hidden Single、Naked Pair 等人类思维规则优先，Z3 作为保底验证
- **拍照识别** — 上传数独照片，OpenCV 透视变换 + 动态轮廓提取 + 本地 ONNX 模型数字识别（无需外部 OCR 服务）
- **单格提示** — 选中任意空格，查看候选数字及排除原因
- **中英文界面与解释** — Vue i18n 管理 UI、规则名称、解释模式和错误提示
- **候选数与历史回放** — 3x3 候选数显示、步骤历史、回退/前进和刷新恢复
- **多色状态标记** — 区分 OCR 识别、用户输入、推导结果、当前目标和选中格
- **盘面锁定** — 确认初始数字后只读保护，防止推导过程中误触
- **响应式 Web App** — 桌面三栏布局，移动端上下布局，Playwright smoke test 覆盖主流程

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+ / npm
- Windows / Linux / macOS

### 方式一：一键脚本

```bash
# Windows
run.bat

# Linux / macOS
chmod +x run.sh && ./run.sh
```

脚本会自动创建虚拟环境、安装依赖、启动服务。
如果检测到可用 npm，会构建 Vue 前端；如果 npm 在 WSL 中命中错误的 Windows shim，脚本会使用已安装的 `frontend/node_modules` 兜底构建，或回退到已有构建产物。

### 方式二：手动启动

```bash
python -m venv venv

# Windows
.\venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt

cd frontend
npm install
npm run build
cd ..

python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

### 方式三：Docker

```bash
docker build -t easysudoku .
docker run -p 8000:8000 easysudoku
```

启动后访问 http://127.0.0.1:8000

## 使用方法

1. **选择语言** — 首次进入选择中文或英文，之后会保存到浏览器本地
2. **拍照上传或手动输入** — 上传数独照片自动 OCR，或直接在 9x9 网格中输入已知数字
3. **修正并确认盘面** — 检查 OCR 结果，点击「确认初始盘面」锁定初始数字
4. **逐步推导** — 点击「推导下一步」，查看目标格、结论、原因和验证方式
5. **查看提示和历史** — 选中空格查看候选数，使用 Back/Forward 或历史列表回放步骤
6. **刷新恢复** — 盘面、历史、语言、解释模式和上传图片会保存在浏览器本地

## 项目结构

```
EasySudoku/
├── smt_engine.py            # Z3 SMT 核心引擎 (建模 + UNSAT Core 推导)
├── heuristic_engine.py      # 启发式规则引擎 (Hidden Single + Naked Pair)
├── vision.py                # 计算机视觉模块 (OpenCV + ONNX 数字识别)
├── main.py                  # FastAPI 后端
├── frontend/                # Vue 3 + Vite + TypeScript + Tailwind 前端
│   ├── src/
│   │   ├── components/      # 数独盘面、操作区、解释区、历史、上传等组件
│   │   ├── composables/     # useSudoku/useHistory/usePersistence 状态逻辑
│   │   ├── services/        # API adapter，兼容结构化和旧格式响应
│   │   ├── locales/         # zh-CN / en-US 文案
│   │   └── types/           # TypeScript 类型
│   └── tests/e2e/           # Playwright smoke tests
├── templates/
│   └── index.html           # 旧前端回退页面
├── docs/
│   └── demo_script.md       # 黑客松演示脚本
├── models/
│   └── sudoku_chars74k.onnx # Chars74K 训练的 CNN 数字识别模型
├── requirements.txt         # Python 依赖
├── Dockerfile               # Docker 容器配置
├── run.bat / run.sh         # 一键启动脚本
└── test_phase*.py           # 测试用例
```

## 技术架构

### 推导管线

```
用户输入/OCR → 启发式规则 (Hidden Single → Naked Pair) → Z3 UNSAT Core → 结构化推导步骤 → i18n 解释
```

| 层级 | 策略 | 说明 |
|------|------|------|
| L1 | Python 预剪枝 | O(1) 查表排除同行/同列/同宫冲突，拦截 60-70% Z3 调用 |
| L2 | Hidden Single | 某数字在某区域只有唯一空格可填，最符合人类直觉 |
| L3 | Naked Pair | 两格共享相同两候选数，排除同区域其他格子 |
| L4 | SMT UNSAT Core | Z3 `assert_and_track` 精确标签，覆盖所有复杂情况 |

### 数字识别管线

```
图片 → Canny 边缘检测 → 最大四边形轮廓 → 透视变换 → 切割 81 格
→ 动态轮廓提取 → 几何启发式拦截 → 等比例缩放 + 白色填充 → ONNX 模型推理
```

- **动态轮廓提取** — 自适应阈值 + `findContours`，基于面积和高度双重过滤判定空格
- **几何启发式** — 数字 1 的宽高比 < 0.45，直接硬逻辑拦截，绕过模型识别短板
- **等比例缩放** — 最长边缩放至 28px 保持宽高比，白色填充至 32x32，消除强制 resize 的拉伸失真
- **本地 ONNX 推理** — Chars74K 训练的 CNN 模型，通过 `cv2.dnn` 加载，零外部依赖，识别准确率约 97.5%

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 渲染前端页面 |
| POST | `/upload` | 上传数独照片，返回识别矩阵 |
| POST | `/next-step` | 返回下一步推导、结构化 step、旧字段兼容解释 |
| POST | `/hint-cell` | 查询单格候选数及排除原因 |
| POST | `/solve` | 直接求解完整答案 |

`/next-step` 保留旧字段以兼容早期前端，同时新增结构化字段：

```json
{
  "row": 2,
  "col": 6,
  "value": 5,
  "explanation": "legacy explanation",
  "eliminations": [],
  "updated_grid": [],
  "step": {
    "rule_type": "hidden_single",
    "difficulty": "basic",
    "target_cell": { "row": 2, "col": 6 },
    "value": 5,
    "explanation_key": "deduction.hiddenSingle",
    "explanation_params": {
      "row": 3,
      "column": 7,
      "value": 5,
      "region_type": "row",
      "region_index": 3
    },
    "candidate_changes": [],
    "verification_type": "human_rule"
  },
  "board": [],
  "legacy_explanation": "legacy explanation"
}
```

## 运行测试

```bash
python test_phase1.py   # Z3 SAT/UNSAT 基础验证
python test_phase2.py   # UNSAT Core 逐步推导 (51步完整求解)
python test_phase3.py   # 视觉模块结构验证
```

### 前端 Smoke Test

先启动后端服务：

```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

另开一个终端运行：

```bash
cd frontend
npm install
npm run test:smoke:install
EASYSUDOKU_BASE_URL=http://127.0.0.1:8000 npm run test:smoke
```

如果 Playwright 报 `libnspr4.so: cannot open shared object file` 或类似系统库缺失，在 Linux/WSL 中先安装浏览器依赖：

```bash
cd frontend
sudo npm run test:smoke:deps
```

也可以直接使用 Playwright 官方命令：

```bash
sudo npx playwright install-deps chromium
```

## 技术栈

- **后端**: Python 3.10+, FastAPI, uvicorn, python-multipart
- **SMT 引擎**: z3-solver (Z3 Python API)
- **计算机视觉**: opencv-python, numpy
- **数字识别**: 本地 ONNX 模型 (Chars74K CNN, cv2.dnn 推理)
- **前端**: Vue 3, Vite, TypeScript, Tailwind CSS, vue-i18n
- **测试**: Python 脚本测试 + Playwright smoke test
- **部署**: Docker 多阶段构建 (Node 构建 Vue, python:3.12-slim 运行 FastAPI)

## 黑客松演示

推荐演示流程见 [docs/demo_script.md](docs/demo_script.md)。核心展示顺序：

1. 中文/英文切换
2. 上传数独图片并修正 OCR 结果
3. 确认初始盘面
4. 展示候选数、选中格、当前目标和解释分组
5. 执行下一步并切换 Brief / Teaching / Technical
6. 历史回退/前进
7. 刷新页面并恢复状态

## 后续规划

- [ ] 扩展启发式规则 (Pointing Pair, Box-Line Reduction, Naked Triple, Hidden Pair)
- [ ] 第二阶段实现完整推导链生成与播放
- [ ] 增加更细粒度的候选数变化解释
- [ ] X-Wing 等复杂技巧放入后续高级规则阶段
