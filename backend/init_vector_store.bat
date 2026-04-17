@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: 知识库向量存储初始化脚本 (Windows)
:: 对应本地大模型集成指南中的方法1
:: 支持选择模型提供商和重建选项

echo ========================================
echo    知识库向量存储初始化脚本
echo ========================================
echo.

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo "[错误] 未找到Python，请先安装Python 3.8+"
    pause
    exit /b 1
)

echo "[信息] 检查Python版本..."
python -c "import sys; print('Python版本:', sys.version)" 2>&1

REM 检查虚拟环境
if not exist "venv" (
    echo "[信息] 虚拟环境不存在，自动创建..."
    python -m venv venv
)

echo "[信息] 激活虚拟环境..."
call venv\Scripts\activate.bat

REM 检查服务是否运行
echo "[信息] 检查FastAPI服务是否运行..."
curl -s -o nul -w "%%{http_code}" http://localhost:8000/api/v1/knowledge/config > service_check.txt
set /p service_status=<service_check.txt
del service_check.txt

if "!service_status!"=="200" (
    echo "[信息] 服务运行正常"
) else (
    echo "[警告] 服务未运行或无法访问 (HTTP状态码: !service_status!)，自动启动服务..."
    echo "[信息] 启动FastAPI服务..."
    start /B cmd /c "venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    echo "[信息] 等待服务启动..."
    timeout /t 15 /nobreak >nul
    REM 再次检查服务是否就绪
    curl -s -o nul -w "%%{http_code}" http://localhost:8000/api/v1/knowledge/config > service_check2.txt
    set /p service_status2=<service_check2.txt
    del service_check2.txt
    if "!service_status2!"=="200" (
        echo "[信息] 服务启动成功"
    ) else (
        echo "[错误] 服务启动失败，请手动检查"
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo           选择模型提供商
echo ========================================
echo 1. Ollama (本地模型)
echo 2. SiliconFlow (云端API)
echo 3. 使用默认配置 (从.env文件读取)
echo.
set /p model_choice="请选择模型提供商 (1/2/3): "

if "!model_choice!"=="1" (
    set model_provider=ollama
    echo "[信息] 选择模型: Ollama"
) else if "!model_choice!"=="2" (
    set model_provider=siliconflow
    echo "[信息] 选择模型: SiliconFlow"
) else (
    set model_provider=
    echo "[信息] 使用默认模型提供商"
)

echo.
echo ========================================
echo           向量化选项
echo ========================================
echo 1. 仅向量化新文档 (增量更新)
echo 2. 重建整个向量存储 (删除后重新创建)
echo.
set /p rebuild_choice="请选择向量化选项 (1/2): "

if "!rebuild_choice!"=="2" (
    set rebuild=true
    echo "[信息] 选择重建整个向量存储"
) else (
    set rebuild=false
    echo "[信息] 选择增量更新"
)

echo.
echo ========================================
echo           开始处理
echo ========================================

REM 扫描文档
echo "[信息] 扫描知识库文档..."
curl -X POST http://localhost:8000/api/v1/knowledge/scan -H "Content-Type: application/json" -s
echo.

REM 构建API参数
set api_url=http://localhost:8000/api/v1/knowledge/vectorize
set query_params=

if defined model_provider (
    set query_params=?model_provider=!model_provider!
)

if "!rebuild!"=="true" (
    if defined query_params (
        set query_params=!query_params!^&rebuild=true
    ) else (
        set query_params=?rebuild=true
    )
)

if defined query_params (
    set api_url=!api_url!!query_params!
)

echo "[信息] 调用向量化API: !api_url!"
echo.

REM 调用向量化API
curl -X POST "!api_url!" -H "Content-Type: application/json" -s

echo.
echo "[信息] 向量化完成！"
echo.

REM 显示统计信息
echo "[信息] 获取知识库统计..."
curl -s http://localhost:8000/api/v1/knowledge/stats

echo.
echo ========================================
echo           完成
echo ========================================
echo "[提示] 知识库向量存储初始化完成"
echo "[提示] 可以访问 http://localhost:8000/docs 查看API文档"
echo.

pause