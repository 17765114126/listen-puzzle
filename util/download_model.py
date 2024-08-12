# 模型下载
from modelscope import snapshot_download


def download_model(model_name):
    # faster-whisper模型下载
    model_dir = snapshot_download('pengzhendong/faster-whisper-' + model_name)
    print(f"模型 {model_name} 已下载到 {model_dir}")
    return model_name + "模型下载成功"
    # model_dir = snapshot_download('pengzhendong/faster-whisper-tiny')
    # model_dir = snapshot_download('pengzhendong/faster-whisper-base')
    # model_dir = snapshot_download('pengzhendong/faster-whisper-small')
    # model_dir = snapshot_download('pengzhendong/faster-whisper-medium')
    # model_dir = snapshot_download('pengzhendong/faster-whisper-large-v3')
