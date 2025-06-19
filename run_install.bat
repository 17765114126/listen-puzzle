@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

:: 设置项目信息
set GIT_REPO=https://gitee.com/zhaofu233/carla.git
set PROJECT_NAME=carla
set REQUIREMENTS_FILE=requirements.txt
set VENV_NAME=venv

:: 检查Git是否安装
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo 错误：未检测到Git，请先安装Git并添加到系统路径
    echo 从以下网址下载：https://git-scm.com/downloads
    pause
    exit /b 1
)

:: 检查Python是否安装
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo 错误：未检测到Python，请先安装Python并添加到系统路径
    echo 从以下网址下载：https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 检查Python版本是否符合venv要求
python -c "import sys; sys.exit(0) if sys.version_info >= (3,3) else sys.exit(1)"
if %errorlevel% neq 0 (
    echo 错误：Python版本低于3.3，无法使用内置venv模块
    echo 请安装Python 3.3或更高版本
    python --version
    pause
    exit /b 1
)

:: 克隆或更新项目
if exist "%PROJECT_NAME%" (
    echo 项目已存在，开始更新...
    cd "%PROJECT_NAME%"
    git pull
    if %errorlevel% neq 0 (
        echo 错误：Git更新失败
        cd ..
        pause
        exit /b 1
    )
    cd ..
) else (
    echo 正在克隆项目...
    git clone %GIT_REPO% %PROJECT_NAME%
    if %errorlevel% neq 0 (
        echo 错误：Git克隆失败
        pause
        exit /b 1
    )
)

:: 进入项目目录
cd "%PROJECT_NAME%"

:: 创建或使用虚拟环境
if exist "%VENV_NAME%" (
    echo 检测到现有的虚拟环境 %VENV_NAME%，准备激活...
) else (
    echo 正在创建新的虚拟环境...
    python -m venv "%VENV_NAME%"
    if %errorlevel% neq 0 (
        echo 错误：创建虚拟环境失败
        pause
        exit /b 1
    )
    echo 虚拟环境创建成功
)

:: 激活虚拟环境
echo 激活虚拟环境...
call "%VENV_NAME%\Scripts\activate.bat"
if %errorlevel% neq 0 (
    echo 错误：无法激活虚拟环境
    pause
    exit /b 1
)
:: 设置镜像源
pip config set global.index-url https://pypi.doubanio.com/simple/
:: 升级pip
echo 升级pip到最新版本...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo 警告：pip升级失败，尝试继续执行...
)

:: 安装Python依赖
if exist "%REQUIREMENTS_FILE%" (
    echo 正在安装Python依赖...
    pip install -r %REQUIREMENTS_FILE%
    if %errorlevel% neq 0 (
        echo 错误：依赖安装失败
        pause
        exit /b 1
    )
) else (
    echo 警告：未找到requirements.txt文件，跳过依赖安装
)

:: 完成信息
echo.
echo ==============================
echo 项目设置完成！
echo 项目路径：%cd%
echo 虚拟环境：%VENV_NAME%
echo.
echo 下次使用时，可以运行以下命令激活环境：
echo cd %PROJECT_NAME%
echo call %VENV_NAME%\Scripts\activate.bat
echo.
echo 要退出虚拟环境，请输入：deactivate
echo ==============================

endlocal