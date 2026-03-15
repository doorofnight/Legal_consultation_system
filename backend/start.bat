@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: AI 法律咨询系统  - 后端启动脚本 (Windows)
:: 适用于 Windows 系统

echo ========================================
echo    AI 法律咨询系统 - 后端启动脚本
echo ========================================
echo.

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo [信息] 检查Python版本...
python -c "import sys; print('Python版本:', sys.version)" 2>&1

REM 检查虚拟环境
if not exist "venv" (
    echo [信息] 创建虚拟环境...
    python -m venv venv
)

echo [信息] 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装/更新依赖
echo [信息] 安装依赖包...
pip install --upgrade pip
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

REM 检查环境变量文件
if not exist ".env" (
    echo [警告] .env文件不存在，从示例文件创建...
    copy ".env.example" ".env"
    echo [提示] 请编辑 .env 文件配置数据库和AI模型
)

REM 创建数据库表
echo [信息] 创建数据库表...
python -c "
from app.db.session import engine
from app.db.base import Base
Base.metadata.create_all(bind=engine)
print('数据库表创建完成')
"

REM 启动服务
echo [信息] 启动FastAPI服务...
echo [提示] 服务地址: http://localhost:8000
echo [提示] API文档: http://localhost:8000/docs
echo.

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause