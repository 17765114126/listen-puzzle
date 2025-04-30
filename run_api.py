from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from data import use_ffmpeg
import shutil
import uvicorn
import logging
import config
import os
import uuid

from api.svc_api import router as api_interface
from api.little_tool_api import router as api_tool
from api.video_api import router as video_api

app = FastAPI()

app.include_router(api_interface)
app.include_router(api_tool)
app.include_router(video_api)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 配置静态文件服务
os.makedirs(config.UPLOAD_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头部
)


def clean_upload_dir():
    """清空上传目录"""
    try:
        if os.path.exists(config.UPLOAD_DIR):
            # 删除整个目录（包括所有子文件和子目录）
            shutil.rmtree(config.UPLOAD_DIR)
        # 重新创建目录（保持目录存在）
        os.makedirs(config.UPLOAD_DIR, exist_ok=True)
    except Exception as e:
        raise RuntimeError(f"目录清理失败: {str(e)}")


@app.post("/upload_file_stream")
async def upload_video(file_stream: UploadFile = File(...)):
    # try:
    # 1. 清理上传目录
    # clean_upload_dir()

    # # 2. 验证文件类型流
    # if not video.content_type.startswith("video/"):
    #     raise HTTPException(400, "仅支持视频文件上传")

    # 3. 生成唯一文件名
    file_ext = file_stream.filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{file_ext}"
    file_path = os.path.join(config.UPLOAD_DIR, filename)

    # 4. 分块写入文件（适合大文件）
    with open(file_path, "wb") as buffer:
        while content := await file_stream.read(1024 * 1024):  # 每次读取1MB
            buffer.write(content)
    access_url_path = config.ROOT_DIR_WIN / "static" / "uploads" / filename
    video_info = use_ffmpeg.get_info(access_url_path)
    return {
        "videoWebPath": f"static/uploads/{filename}",
        "videoPath": access_url_path,
        "duration": video_info["duration"]
    }


# except RuntimeError as e:
#     raise HTTPException(500, detail=str(e))
# except Exception as e:
#     raise HTTPException(500, detail=f"上传失败: {str(e)}")


# 使用 Python 3 提供静态文件服务命令（在dist根目录运行）: python -m http.server 8688

# 启动命令（必须在主类目录下）：uvicorn run_api:app --reload
# 访问地址：http://127.0.0.1:8686
# 自动动生成交互式 API 文档，访问地址： http://127.0.0.1:8686/docs
def run():
    os.environ['HF_ENDPOINT'] = "https://hf-mirror.com/"
    os.environ['HF_HOME'] = 'D:/hf-model'
    clean_upload_dir()
    uvicorn.run(app='run_api:app', host="127.0.0.1", port=config.api_host, reload=True)


if __name__ == '__main__':
    run()
