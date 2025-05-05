from data import dh_live
from fastapi import APIRouter
from api.Do import BaseReq
import config
from data.sovits_v4 import use_sovits_v4
import soundfile as sf

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


# 语音克隆
@router.post("/sovits_v4")
async def tts_endpoint(req: BaseReq):
    opt_sr, audio_opt = use_sovits_v4.get_tts_wav(
        ref_wav_path=req.ref_wav_path,
        prompt_text=req.prompt_text,
        prompt_language=req.prompt_language,
        text=req.text,
        text_language=req.text_language,
        # how_to_cut=req.how_to_cut,
        top_k=req.top_k,
        top_p=req.top_p,
        temperature=req.temperature,
        # ref_free=ref_free,
        speed=req.speed,
        # if_freeze=if_freeze,
        # inp_refs=inp_refs,
        # sample_steps=sample_steps,
        # if_sr=if_sr,
        # pause_second=pause_second,
    )
    access_url_path = config.ROOT_DIR_WIN / "static" / "uploads" / 'sovits_v4_audio.wav'
    sf.write(access_url_path, audio_opt, opt_sr)
    return {
        "vitsV4WebUrl": 'static/uploads/sovits_v4_audio.wav',
        "vitsV4Url": access_url_path,
    }
