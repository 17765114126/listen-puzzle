from data import dh_live
from fastapi import APIRouter
from api.Do import BaseReq
import config

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
