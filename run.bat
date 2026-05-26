@echo off
chcp 65001 >nul
echo ========================================
echo   EasySudoku - 一键启动
echo ========================================
echo.

:: 检查 Python 是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

:: 检查并创建虚拟环境
if not exist "venv\Scripts\activate.bat" (
    echo [1/3] 正在创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo [错误] 创建虚拟环境失败
        pause
        exit /b 1
    )
    echo       虚拟环境创建成功
) else (
    echo [1/3] 虚拟环境已存在，跳过创建
)

:: 激活虚拟环境
call .\venv\Scripts\activate

:: 安装依赖
echo [2/3] 正在安装依赖（首次运行可能需要几分钟）...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)
echo       依赖安装完成

:: 启动服务
echo [3/3] 正在启动服务...
echo.
echo   访问地址: http://127.0.0.1:8000
echo   按 Ctrl+C 停止服务
echo.
python -m uvicorn main:app --host 127.0.0.1 --port 8000
