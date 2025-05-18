from fastapi import APIRouter
import soundfile as sf
import shutil

from data import dh_live
from util import string_util
from util import file_util
import config
from db.Do import BaseReq

router = APIRouter()


# 分离音频和伴奏
@router.post("/separate_audio")
async def separate_audio(req: BaseReq):
    vocalUrl, accompanimentUrl = dh_live.do_s(req.audio_path, config.UPLOAD_DIR)
    access_url_path = config.ROOT_DIR_WIN / config.UPLOAD_DIR
    return {
        "vocalUrl": f"{access_url_path}{vocalUrl}",
        "vocalWebUrl": f"{config.UPLOAD_DIR}{vocalUrl}",
        "accompanimentUrl": f"{config.UPLOAD_DIR}{accompanimentUrl}",
        "accompanimentWebUrl": f"{access_url_path}{accompanimentUrl}"
    }


# 合并伴奏
@router.post("/merge_audio")
async def merge_audio(req: BaseReq):
    # 转换 歌曲人声req.vocalUrl  素材人声req.sourceAudioPath
    final_vocal = req.sourceAudioPath
    finalUrl = dh_live.do_m(final_vocal, req.accompanimentUrl, config.UPLOAD_DIR)
    access_url_path = config.ROOT_DIR_WIN / config.UPLOAD_DIR
    return {
        "finalUrl": f"{access_url_path}{finalUrl}",
        "finalWebUrl": f"{config.UPLOAD_DIR}{finalUrl}",
    }


@router.post("/get_source_audio")
def get_source_audio():
    # 获取已存在本地素材
    save_dir = config.ROOT_DIR_WIN / config.source_audios_dir
    folder_file_names = file_util.get_folder_file_name(save_dir)
    source_infos = []
    for folder_file_name in folder_file_names:
        source_info = {
            "source_name": folder_file_name,
            "source_url": f"{config.source_audios_dir}{folder_file_name}"
        }
        source_infos.append(source_info)
    return source_infos


@router.post("/del_source_audio")
def del_source_audio(req: BaseReq):
    # 删除本地素材
    return file_util.del_file(config.source_audios_dir + req.source_url)


# 保存音色
@router.post("/save_timbre")
async def save_timbre(req: BaseReq):
    access_url_path = config.ROOT_DIR_WIN / config.source_audios_dir / req.prompt_text
    shutil.copy2(req.ref_wav_path, access_url_path)
    return True


# 语音克隆
@router.post("/sovits_v4")
async def tts_endpoint(req: BaseReq):
    from data.sovits_v4 import use_sovits_v4
    # 获取字段，如果字段为空则返回None
    req_dict = req.dict()
    if req_dict.get("prompt_language", None) is None:
        language = string_util.detect_prompt_language(req_dict.get("prompt_text", None))
        req_dict["prompt_language"] = language
    if req_dict.get("text_language", None) is None:
        language = string_util.detect_prompt_language(req_dict.get("text", None))
        req_dict["text_language"] = language
    opt_sr, audio_opt = use_sovits_v4.get_tts_wav(
        ref_wav_path=req_dict.get("ref_wav_path", None),
        prompt_text=req_dict.get("prompt_text", None),
        prompt_language=req_dict.get("prompt_language", None),
        text=req_dict.get("text", None),
        text_language=req_dict.get("text_language", None),
        how_to_cut=req_dict.get("how_to_cut", None),
        top_k=req_dict.get("top_k", None),
        top_p=req_dict.get("top_p", None),
        temperature=req_dict.get("temperature", None),
        # ref_free=ref_free,
        speed=req_dict.get("speed", None),
        # if_freeze=if_freeze,
        # inp_refs=inp_refs,
        # sample_steps=sample_steps,
        # if_sr=if_sr,
        # pause_second=pause_second,
    )
    access_url_path = config.ROOT_DIR_WIN / config.UPLOAD_DIR / 'sovits_v4_audio.wav'
    sf.write(access_url_path, audio_opt, opt_sr)
    return {
        "vitsV4WebUrl": 'static/uploads/sovits_v4_audio.wav',
        "vitsV4Url": access_url_path,
    }
