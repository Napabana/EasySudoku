#!/bin/bash
set -e

echo "========================================"
echo "  EasySudoku - 一键启动"
echo "========================================"
echo ""

# 检查 Python 是否可用
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到 Python3，请先安装 Python 3.10+"
    exit 1
fi

NPM_CMD="./scripts/npm-safe.sh"

# 检查 Node/npm 是否可用。WSL 中可能误命中 Windows npm shim，必须避免挂住启动脚本。
if timeout 10 npm --version &> /dev/null; then
    HAS_NPM=1
elif [ -d "frontend/node_modules" ]; then
    echo "[警告] npm 不可用，将使用已安装的 node_modules 执行前端构建"
    HAS_NPM=2
else
    echo "[警告] 未检测到可用 npm，将跳过 Vue 前端构建并回退到已有构建或旧页面"
    HAS_NPM=0
fi

# 检查并创建虚拟环境
if [ ! -f "venv/bin/activate" ]; then
    echo "[1/4] 正在创建虚拟环境..."
    python3 -m venv venv
    echo "      虚拟环境创建成功"
else
    echo "[1/4] 虚拟环境已存在，跳过创建"
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "[2/4] 正在安装 Python 依赖（首次运行可能需要几分钟）..."
pip install -r requirements.txt -q
echo "      依赖安装完成"

if [ "$HAS_NPM" = "1" ]; then
    echo "[3/4] 正在构建 Vue 前端..."
    "$NPM_CMD" --prefix frontend install
    "$NPM_CMD" --prefix frontend run build
    echo "      前端构建完成"
elif [ "$HAS_NPM" = "2" ]; then
    echo "[3/4] 正在使用本地 node_modules 构建 Vue 前端..."
    "$NPM_CMD" --prefix frontend run build
    echo "      前端构建完成"
else
    echo "[3/4] 跳过 Vue 前端构建"
fi

# 启动服务
echo "[4/4] 正在启动服务..."
echo ""
echo "  访问地址: http://127.0.0.1:8000"
echo "  按 Ctrl+C 停止服务"
echo ""
python -m uvicorn main:app --host 0.0.0.0 --port 8000
