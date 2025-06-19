@echo off
set HF_ENDPOINT=https://hf-mirror.com/
set HF_HOME=D:/hf-model
REM 设置工作目录
cd /d %~dp0


REM 激活虚拟环境
call venv\Scripts\activate

REM 运行
python run_web.py