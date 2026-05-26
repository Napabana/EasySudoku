# EasySudoku

基于 Z3 SMT Solver 的数独逐步推导导师。拍照上传或手动输入数独题目，系统利用 UNSAT Core 机制逐步推导每个空格的唯一解，并给出人类可读的逻辑解释。

## 功能特性

- **逐步 SMT 推导** — 基于 Z3 的 UNSAT Core 提取，精确到具体行/列/宫的冲突解释
- **启发式规则引擎** — Hidden Single、Naked Pair 等人类思维规则优先，Z3 作为保底验证
- **拍照识别** — 上传数独照片，OpenCV 透视变换 + 动态轮廓提取 + EasyOCR 数字识别
- **单格提示** — 选中任意空格，查看候选数字及排除原因
- **多色状态标记** — 区分 OCR 识别、用户输入、SMT 推导三种来源
- **盘面锁定** — 确认初始数字后只读保护，防止推导过程中误触

## 快速开始

### 环境要求

- Python 3.10+
- Windows / Linux / macOS

### 方式一：一键脚本

```bash
# Windows
run.bat

# Linux / macOS
chmod +x run.sh && ./run.sh
```

脚本会自动创建虚拟环境、安装依赖、启动服务。

### 方式二：手动启动

```bash
python -m venv venv

# Windows
.\venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

### 方式三：Docker

```bash
docker build -t easysudoku .
docker run -p 8000:8000 easysudoku
```

启动后访问 http://127.0.0.1:8000

## 使用方法

1. **手动输入** — 在 9x9 网格中填入已知数字，点击「确认初始盘面」锁定
2. **拍照上传** — 点击上传按钮选择数独照片，OCR 自动识别填入网格
3. **逐步推导** — 点击「推导下一步」，查看 Z3 给出的逻辑推理和排除原因
4. **单格提示** — 点击选中一个空格，点击「获取当前格提示」查看候选数
5. **直接求解** — 点击「直接求解」一键获得完整答案

## 项目结构

```
EasySudoku/
├── smt_engine.py            # Z3 SMT 核心引擎 (建模 + UNSAT Core 推导)
├── heuristic_engine.py      # 启发式规则引擎 (Hidden Single + Naked Pair)
├── vision.py                # 计算机视觉模块 (OpenCV + EasyOCR)
├── main.py                  # FastAPI 后端
├── templates/
│   └── index.html           # 前端页面 (TailwindCSS)
├── requirements.txt         # Python 依赖
├── Dockerfile               # Docker 容器配置
├── run.bat / run.sh         # 一键启动脚本
└── test_phase*.py           # 测试用例
```

## 技术架构

### 推导管线

```
用户输入/OCR → 启发式规则 (Hidden Single → Naked Pair) → Z3 UNSAT Core → 人类可读解释
```

| 层级 | 策略 | 说明 |
|------|------|------|
| L1 | Python 预剪枝 | O(1) 查表排除同行/同列/同宫冲突，拦截 60-70% Z3 调用 |
| L2 | Hidden Single | 某数字在某区域只有唯一空格可填，最符合人类直觉 |
| L3 | Naked Pair | 两格共享相同两候选数，排除同区域其他格子 |
| L4 | SMT UNSAT Core | Z3 `assert_and_track` 精确标签，覆盖所有复杂情况 |

### OCR 管线

```
图片 → Canny 边缘检测 → 最大四边形轮廓 → 透视变换 → 切割 81 格
→ 动态轮廓 bounding box 提取 → 白边 padding → EasyOCR 识别
```

- 动态轮廓提取替代固定裁剪，避免截断数字笔画
- 基于面积+高度的双重过滤判定空格，跳过不必要的 OCR 调用

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 渲染前端页面 |
| POST | `/upload` | 上传数独照片，返回识别矩阵 |
| POST | `/next-step` | 返回下一步推导及解释 |
| POST | `/hint-cell` | 查询单格候选数及排除原因 |
| POST | `/solve` | 直接求解完整答案 |

## 运行测试

```bash
python test_phase1.py   # Z3 SAT/UNSAT 基础验证
python test_phase2.py   # UNSAT Core 逐步推导 (51步完整求解)
python test_phase3.py   # 视觉模块结构验证
```

## 技术栈

- **后端**: Python 3.10+, FastAPI, uvicorn
- **SMT 引擎**: z3-solver (Z3 Python API)
- **计算机视觉**: opencv-python, EasyOCR
- **前端**: 原生 HTML/JS + TailwindCSS
- **部署**: Docker (python:3.12-slim)

## 后续规划

- [ ] 扩展启发式规则 (Naked Triple/Quad, Pointing Pair, X-Wing)
- [ ] 推导历史回放，支持撤销/重做
- [ ] 移动端响应式优化
