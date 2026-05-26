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

# 检查并创建虚拟环境
if [ ! -f "venv/bin/activate" ]; then
    echo "[1/3] 正在创建虚拟环境..."
    python3 -m venv venv
    echo "      虚拟环境创建成功"
else
    echo "[1/3] 虚拟环境已存在，跳过创建"
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "[2/3] 正在安装依赖（首次运行可能需要几分钟）..."
pip install -r requirements.txt -q
echo "      依赖安装完成"

# 启动服务
echo "[3/3] 正在启动服务..."
echo ""
echo "  访问地址: http://127.0.0.1:8000"
echo "  按 Ctrl+C 停止服务"
echo ""
python -m uvicorn main:app --host 0.0.0.0 --port 8000
