from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from data import use_ffmpeg
import config
import shutil, os, uvicorn, uuid
import logging
from api.svc_api import router as api_interface
from api.little_tool_api import router as api_tool
from api.video_api import router as video_api
from api.llm_clip_api import router as llm_clip_api

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.include_router(api_interface)
app.include_router(api_tool)
app.include_router(video_api)
app.include_router(llm_clip_api)

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
    # 生成唯一文件名
    file_ext = file_stream.filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{file_ext}"
    file_path = os.path.join(config.UPLOAD_DIR, filename)

    # 分块写入文件（适合大文件）
    with open(file_path, "wb") as buffer:
        while content := await file_stream.read(1024 * 1024):  # 每次读取1MB
            buffer.write(content)
    access_url_path = config.ROOT_DIR_WIN / config.UPLOAD_DIR / filename
    video_info = use_ffmpeg.get_info(access_url_path)
    return {
        "videoWebPath": f"{config.UPLOAD_DIR}{filename}",
        "videoPath": access_url_path,
        "duration": video_info["duration"]
    }


@app.post("/upload_source_file_stream")
async def upload_source_video(file_stream: UploadFile = File(...)):
    # 生成唯一文件名
    file_ext = file_stream.filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{file_ext}"
    file_path = os.path.join(config.source_videos_dir, filename)

    # 分块写入文件（适合大文件）
    with open(file_path, "wb") as buffer:
        while content := await file_stream.read(1024 * 1024):  # 每次读取1MB
            buffer.write(content)
    access_url_path = config.ROOT_DIR_WIN / config.source_videos_dir / filename
    video_info = use_ffmpeg.get_info(access_url_path)
    return {
        "videoWebPath": f"{config.source_videos_dir}{filename}",
        "videoPath": access_url_path,
        "duration": video_info["duration"]
    }


@app.get("/loadLog")
async def loadLog():
    return ""


# 使用 Python 3 提供静态文件服务命令（在dist根目录运行）: python -m http.server 8688

# 启动命令（必须在主类目录下）：uvicorn run_api:app --reload
# 访问地址：http://127.0.0.1:8686
# 自动动生成交互式 API 文档，访问地址： http://127.0.0.1:8686/docs
def run():
    os.environ['HF_ENDPOINT'] = "https://hf-mirror.com/"
    os.environ['HF_HOME'] = 'D:/hf-model'

    # 清除upload_dir
    clean_upload_dir()

    logging.info('------主程序开始运行-------')
    uvicorn.run(app='run_api:app',
                host="127.0.0.1",
                port=config.api_host,
                reload=True,
                access_log=True,  # 开启访问日志
                )


if __name__ == '__main__':
    run()
