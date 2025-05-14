from data import use_llm, use_ffmpeg, prompt_config, video_downloader
from data.util import file_util, string_util
import config
from fastapi import APIRouter
from api.Do import BaseReq

router = APIRouter()


@router.post("/get_source_videos")
def get_source_videos():
    # 获取已存在本地素材
    save_dir = config.ROOT_DIR_WIN / config.source_videos_dir
    folder_file_names = file_util.get_folder_file_name(save_dir)
    source_infos = []
    for folder_file_name in folder_file_names:
        duration, description = video_downloader.read_metadata(save_dir / folder_file_name)
        source_info = {
            "source_name": folder_file_name,
            "source_url": f"{config.source_videos_dir}{folder_file_name}",
            "description": description,
            "duration": duration,
        }
        source_infos.append(source_info)
    return source_infos


@router.post("/del_source_videos")
def del_source_videos(req: BaseReq):
    # 删除本地素材
    return file_util.del_file(config.source_videos_dir + req.source_url)


@router.post("/del_all_source_videos")
def del_source_videos():
    # 删除全部本地素材
    return file_util.del_file(config.source_videos_dir)


@router.post("/llm_get_source")
def llm_get_source(req: BaseReq):
    print("=================================llm获取搜索关键词=================================")
    keywords_prompt = prompt_config.keywords_prompt(req.creative)
    keywords_resp = use_llm._generate_response(keywords_prompt)
    keywords = keywords_resp.split(",")
    print(keywords)
    print("=================================下载关键词对应视频=================================")
    return video_downloader.keywords_download(keywords)


@router.post("/videos_transitions")
def videos_transitions(req: BaseReq):
    print("=================================llm获取剪辑视频提示词=================================")
    save_dir = config.ROOT_DIR_WIN / config.source_videos_dir
    folder_file_names = file_util.get_folder_file_name(save_dir)
    source_infos = []
    for folder_file_name in folder_file_names:
        duration, description = video_downloader.read_metadata(save_dir / folder_file_name)
        source_info = {
            "source_name": folder_file_name,
            "video_duration": duration,
            "video_describe": description
        }
        source_infos.append(source_info)
    clip_prompt = prompt_config.clip_prompt(req.creative, source_infos)
    print(clip_prompt)
    clip_resp = use_llm._generate_response(clip_prompt)
    bracket_json = string_util.get_bracket_json(clip_resp)
    print("=================================根据llm返回视频信息进行剪辑=================================")
    print(bracket_json)
    output = f"{config.UPLOAD_DIR}concatenate_videos.mp4"
    use_ffmpeg.concatenate_videos_with_transitions(bracket_json, output)
    return {
        "concatenate_web_url": output
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
