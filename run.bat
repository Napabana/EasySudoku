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

:: 检查 Node/npm 是否可用
npm --version >nul 2>&1
if errorlevel 1 (
    echo [警告] 未检测到 npm，将跳过 Vue 前端构建并回退到旧页面
    set HAS_NPM=0
) else (
    set HAS_NPM=1
)

:: 检查并创建虚拟环境
if not exist "venv\Scripts\activate.bat" (
    echo [1/4] 正在创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo [错误] 创建虚拟环境失败
        pause
        exit /b 1
    )
    echo       虚拟环境创建成功
) else (
    echo [1/4] 虚拟环境已存在，跳过创建
)

:: 激活虚拟环境
call .\venv\Scripts\activate

:: 安装依赖
echo [2/4] 正在安装 Python 依赖（首次运行可能需要几分钟）...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)
echo       依赖安装完成

if "%HAS_NPM%"=="1" (
    echo [3/4] 正在构建 Vue 前端...
    pushd frontend
    call npm install
    if errorlevel 1 (
        popd
        echo [错误] 前端依赖安装失败
        pause
        exit /b 1
    )
    call npm run build
    if errorlevel 1 (
        popd
        echo [错误] 前端构建失败
        pause
        exit /b 1
    )
    popd
    echo       前端构建完成
) else (
    echo [3/4] 跳过 Vue 前端构建
)

:: 检查端口占用
netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 goto start_server

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do set OLD_PID=%%a
echo.
echo [警告] 端口 8000 已被占用 (PID: %OLD_PID%)
echo         可能是之前的服务未正常关闭。
echo.
echo   1. 关闭旧进程并重新启动
echo   2. 直接退出
echo.
set /p CHOICE=请选择 (1/2):
if "%CHOICE%"=="1" (
    taskkill /PID %OLD_PID% /F >nul 2>&1
    echo       已关闭旧进程 (PID: %OLD_PID%)
    timeout /t 1 /nobreak >nul
    goto start_server
) else (
    pause
    exit /b 0
)

:start_server
echo [4/4] 正在启动服务...
echo.
echo   访问地址: http://127.0.0.1:8000
echo   按 Ctrl+C 停止服务
echo.
python -m uvicorn main:app --host 127.0.0.1 --port 8000
pause
