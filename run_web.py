import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import multiprocessing
from multiprocessing import freeze_support  # 新增导入
import run_api
import webbrowser
import socket
import time
import config

app = FastAPI()
# 挂载静态文件（自动处理 index.html）
app.mount("/", StaticFiles(directory="dist", html=True), name="static")


# 兜底路由处理前端 history 模式
@app.exception_handler(404)
async def custom_404_handler(request, exc: HTTPException):
    index_path = Path("dist") / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404)
    return FileResponse(index_path)


def run():
    uvicorn.run(
        "run_web:app",  # 使用字符串形式
        host="127.0.0.1",
        port=config.web_host,
        access_log=False
    )


def is_port_ready(port: int, timeout=30) -> bool:
    """检测端口是否就绪"""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                if s.connect_ex(("127.0.0.1", port)) == 0:
                    return True
        except:
            pass
        time.sleep(0.2)
    return False


# pip install pyinstaller
# pyinstaller -F -i icon.ico run.py
# pyinstaller -F -i icon.ico --paths "D:\develop\project\reptile_project\excel_tool" run.py

if __name__ == "__main__":
    freeze_support()
    # 创建两个进程
    api_process = multiprocessing.Process(target=run_api.run)
    web_process = multiprocessing.Process(target=run)

    # 启动进程
    api_process.start()
    web_process.start()
    # 等待端口就绪
    if is_port_ready(8688):
        # 打开默认浏览器
        webbrowser.open(f"http://localhost:{config.web_host}")
    else:
        print(f"⚠️ 服务启动失败，请手动访问 http://localhost:{config.web_host}")
    # 保持主进程运行
    try:
        api_process.join()
        web_process.join()
    except KeyboardInterrupt:
        api_process.terminate()
        web_process.terminate()
