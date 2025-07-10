from data import use_llm, use_ffmpeg, prompt_config, video_downloader
from util import string_util
import config
from fastapi import APIRouter
from db.Do import BaseReq, we_library
import logging as logger

router = APIRouter()


@router.post("/llm_get_source")
def llm_get_source(req: BaseReq):
    logger.info("=================================llm获取搜索关键词=================================")
    keywords_prompt = prompt_config.keywords_prompt(req.creative)
    messages = [{"role": "user", "content": keywords_prompt}]
    keywords_resp = use_llm._generate_response(messages)
    keywords_resp = string_util.remove_think_tags(keywords_resp)
    keywords = keywords_resp.split(",")
    logger.info(keywords)
    logger.info("=================================下载关键词对应视频=================================")
    return video_downloader.keywords_download(keywords)


@router.post("/videos_transitions")
def videos_transitions(req: BaseReq):
    audioUrl = req.dict().get("audioUrl", None)
    logger.info("=================================视频处理=================================")
    # save_dir = config.ROOT_DIR_WIN / config.source_videos_dir
    # folder_file_names = file_util.get_folder_file_name(save_dir)
    # source_infos = []
    source_infos = we_library.fetch_all(f"SELECT id,duration,description FROM video_source WHERE video_type=?;",
                                        (1,))
    # for video_source in video_source_use:
    #     source_info = {
    #         "source_name": folder_file_name,
    #         "video_duration": video_source["duration"],
    #         "video_describe": video_source["description"]
    #     }
    #     source_infos.append(source_info)
    duration = 30
    if audioUrl is not None:
        video_info = use_ffmpeg.get_video_info(req.audioUrl)
        duration = video_info['duration']
    logger.info("=================================llm获取剪辑视频提示词=================================")
    clip_prompt = prompt_config.clip_prompt(req.creative, source_infos, duration)
    logger.info(clip_prompt)
    messages = [{"role": "user", "content": clip_prompt}]
    clip_resp = use_llm._generate_response(messages)
    keywords_resp = string_util.remove_think_tags(clip_resp)
    logger.info("=================================根据llm返回视频信息进行剪辑=================================")
    logger.info(keywords_resp)
    bracket_json = string_util.get_bracket_json(keywords_resp)
    final_video = f"{config.UPLOAD_DIR}concatenate_videos.mp4"
    use_ffmpeg.concatenate_videos_with_transitions(bracket_json, final_video)

    if audioUrl is not None:
        logger.info("=================================合并文案音频=================================")
        use_ffmpeg.add_audio_to_video(final_video, audioUrl, f"{config.UPLOAD_DIR}final_video.mp4")
        final_video = f"{config.UPLOAD_DIR}final_video.mp4"
    return {
        "concatenate_web_url": final_video
    }


if __name__ == '__main__':
    # parse_srt(prompt_config.demo_prompt)
    # creative = use_llm._generate_response(f"""
    # 要求：总结字幕内容生成文案
    # 风格：深度解读，结合人生感悟
    # 时长：1分钟
    # 注意：不要返回任何与文案无关的内容
    # 字幕内容：{prompt_config.demo_prompt}
    # """)
    print("=========================================================")
    # print(creative)
