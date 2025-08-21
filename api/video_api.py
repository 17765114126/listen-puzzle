from data import use_ffmpeg, video_downloader, use_fast_whisper, use_video_analyse
from util import time_util, file_util
from fastapi import APIRouter, UploadFile, File
from db.Do import BaseReq, we_library, VideoSource
from pathlib import Path
import time
import config
import logging as logger
import os
router = APIRouter()


@router.post("/get_source_videos")
def get_source_videos(req: BaseReq):
    # 获取素材库素材
    return we_library.fetch_all(f"SELECT * FROM video_source WHERE video_type=?;",
                                (req.video_type,))


@router.post("/update_video_source")
def update_video_description(req: VideoSource):
    # 修改
    return we_library.add_or_update(req, req.table_name)


@router.post("/del_source_videos")
def del_source_videos(req: BaseReq):
    # 删除本地素材
    video_source = we_library.fetch_one(f"SELECT * FROM video_source WHERE id=?;", (req.id,))
    file_util.del_file(video_source['local_path'])
    return we_library.execute_query("DELETE FROM video_source WHERE id=?;", (req.id,))


# @router.post("/del_all_source_videos")
# def del_source_videos():
#     # 删除全部本地素材
#     return file_util.del_file(config.source_videos_dir)


# 上传视频素材
@router.post("/upload_source_videos_stream")
async def upload_source_videos_stream(file_stream: UploadFile = File(...)):
    # 生成唯一文件名
    file_ext = file_stream.filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{file_ext}"
    file_path = os.path.join(config.source_videos_dir, filename)
    # 分块写入文件（适合大文件）
    with open(file_path, "wb") as buffer:
        while content := await file_stream.read(1024 * 1024):  # 每次读取1MB
            buffer.write(content)
    access_url_path = config.ROOT_DIR_WIN / config.source_videos_dir / filename
    video_info = use_ffmpeg.get_video_info(access_url_path)
    # 创建 VideoSource 实例
    video_source = VideoSource(
        table_name="video_source",
        video_name=filename,
        web_path=f"{config.source_videos_dir}{filename}",
        local_path=str(access_url_path),
        duration=video_info["duration"],
        duration_hms=video_info["duration_hms"],
    )
    we_library.add_or_update(video_source, video_source.table_name)
    return True

@router.get("/get_description")
def get_description(id:int):
    video_source = we_library.fetch_one(f"SELECT * FROM video_source WHERE id=?;", (req.id,))
    # 解析视频描述
    video_analyse_result = use_video_analyse.video_analyze(video_source['local_path'])
    description = video_analyse_result[0].get("description")
    video_source = VideoSource(
        table_name="video_source",
        id=id,
        description=description,
    )
    we_library.add_or_update(video_source, video_source.table_name)
    return description

# 下载视频
@router.post("/download_video")
async def download_video(req: BaseReq):
    title, duration = video_downloader.download_videos_from_url(req.video_url, config.UPLOAD_DIR)
    access_url_path = config.ROOT_DIR_WIN / "static" / "uploads" / title
    # video_info = use_ffmpeg.get_info(access_url_path)
    # 转换时长格式
    try:
        duration = time_util.seconds_to_hms(duration)
    except (ValueError, TypeError):
        duration = "00:00:00"  # 异常时返回默认值
    return {
        "videoWebPath": f"{config.UPLOAD_DIR}{title}",
        "videoPath": access_url_path,
        "duration": duration
        # "duration": video_info["duration"]
    }


# 视频处理
@router.post("/process_video")
async def process_video(req: BaseReq):
    # 验证文件路径
    if not Path(req.input_path).exists():
        return {"error": "文件不存在"}
    input_path = getattr(req, 'input_path', None)
    output_format = getattr(req, 'output_format', 'mp4')
    # 生成默认输出路径
    input_file = Path(input_path)
    output_path = input_file.parent / f"{input_file.stem}_processed.{output_format}"

    output_path = use_ffmpeg.process_video(
        input_path=input_path,
        output_path=output_path,
        start_time=getattr(req, 'start_time', None),
        end_time=getattr(req, 'end_time', None),
        duration=getattr(req, 'duration', None),
        speed_factor=getattr(req, 'speed', None),
        volume_factor=getattr(req, 'volume', None),
        width=getattr(req, 'width', None),
        height=getattr(req, 'height', None),
        cover_image=getattr(req, 'cover_image', None),
        output_format=output_format
    )
    video_info = use_ffmpeg.get_video_info(output_path)
    return {
        "videoWebPath": f"{config.UPLOAD_DIR}{input_file.stem}_processed.{output_format}",
        "videoPath": output_path,
        "duration": video_info["duration_hms"]
    }


# 提取图片
@router.post("/extract_frame")
async def extract_frame(req: BaseReq):
    # 生成唯一文件名
    timestamp = int(time.time())
    filename = f"extracted_frame_{timestamp}.png"
    access_url_path = config.ROOT_DIR_WIN / config.UPLOAD_DIR / filename
    use_ffmpeg.extract_frame(req.video_input, req.time_ss, access_url_path)
    return {
        "webPath": f"{config.UPLOAD_DIR}{filename}",
        "localPath": access_url_path,
    }


# # 设置封面图
# @router.post("/set_video_cover")
# async def set_video_cover(req: BaseReq):
#     video_path = save_upload_file(req.video_input, ".mp4")
#     cover_path = save_upload_file(req.cover_image, ".jpg")
#     output_path = use_ffmpeg.set_video_cover(video_path, cover_path)
#     return FileResponse(output_path, filename="with_cover.mp4")
#

# 提取音频
@router.post("/get_audio")
async def get_audio(req: BaseReq):
    output_dir = config.ROOT_DIR_WIN / config.UPLOAD_DIR / 'distill_audio.mp3'
    use_ffmpeg.get_audio(req.video_url, output_dir)
    return {
        "audioPath": f'{config.UPLOAD_DIR}distill_audio.mp3',
        "audioWebPath": f"{output_dir}"
    }


# 添加音频到视频
@router.post("/add_audio_to_video")
async def add_audio_to_video(req: BaseReq):
    # 生成唯一文件名
    timestamp = int(time.time())
    filename = f"video_with_audio_{timestamp}.mp4"
    output_dir = config.ROOT_DIR_WIN / config.UPLOAD_DIR / filename
    use_ffmpeg.add_audio_to_video(req.video_path, req.audio_path, output_dir)
    return {
        "webPath": f'{config.UPLOAD_DIR}{filename}',
        "localPath": f"{output_dir}"
    }


# 音视频转录
@router.post("/transcribe")
async def transcribe(req: BaseReq):
    subtitle_content = use_fast_whisper.transcribe(
        req.input_path, req.model,
        req.output_format, req.is_translate, req.subtitle_double,
        req.translator_engine, req.subtitle_language
    )
    return {
        "subtitle_content": subtitle_content
    }


# 视频添加字幕
@router.post("/video_add_subtitle")
async def video_add_subtitle(req: BaseReq):
    title = use_ffmpeg.add_subtitle(req.video_input, req.subtitle_content, req.is_soft, req.fontname, req.fontsize,
                                    req.fontcolor, req.subtitle_bottom)
    access_url_path = config.ROOT_DIR_WIN / config.UPLOAD_DIR / title
    video_info = use_ffmpeg.get_video_info(access_url_path)
    return {
        "videoWebPath": f"{config.UPLOAD_DIR}{title}",
        "videoPath": access_url_path,
        "duration": video_info["duration_hms"]
    }


@router.post("/start_compression")
def start_compression(req: BaseReq):
    logger.info("启动批量视频压缩任务")
    use_ffmpeg.batch_compress_videos(
        input_dir=file_util.format_windows_path(req.input_dir),
        backup_dir=file_util.format_windows_path(req.backup_dir),
        crf=req.crf,
        max_bitrate=req.max_bitrate
    )
    return True
