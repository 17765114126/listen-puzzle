import cv2
import re
from difflib import SequenceMatcher
from collections import defaultdict
from transformers import pipeline
import json
import config
from PIL import Image

# 初始化模型
model_path = config.ROOT_DIR_WIN / "models/blip-image-captioning-base"
image_to_text = pipeline("image-to-text", model=model_path)

# 全局参数
FRAME_INTERVAL = 1  # 采样间隔（秒）
MIN_DURATION = 2  # 场景最小持续时间（秒）
# RESIZE_SIZE = (320, 320)
RESIZE_SIZE = (224, 224)

def normalize_text(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', '', text)
    return text


def is_similar(a, b, threshold=0.1):
    """
    相似度阈值
    默认 0.8，可根据实际效果调整（值越高合并越严格）。
    示例：若 牛群 和 奶牛 需要合并，可降低至 0.7。
    """
    return SequenceMatcher(None, normalize_text(a), normalize_text(b)).ratio() > threshold


def preprocess_image(frame):
    # 调整尺寸为模型训练标准（如 224x224）
    resized = cv2.resize(frame, RESIZE_SIZE)

    # 直方图均衡化（增强对比度）
    lab = cv2.cvtColor(resized, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    merged = cv2.merge((l, a, b))

    # 转回 RGB 并归一化
    rgb = cv2.cvtColor(merged, cv2.COLOR_LAB2RGB)
    return rgb.astype("float32") / 255.0  # 归一化到 [0,1]


def analyze_scene(frame):
    processed = preprocess_image(frame)
    pil_image = Image.fromarray((processed * 255).astype("uint8"))
    result = image_to_text(pil_image)
    return result[0]['generated_text']


def video_analyze(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: 视频无法打开！")
        exit()
    # fps = cap.get(cv2.CAP_PROP_FPS)
    # frame_step = int(fps * FRAME_INTERVAL)
    scene_buffer = defaultdict(list)
    last_time = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break

        timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
        if timestamp - last_time >= FRAME_INTERVAL:
            last_time = timestamp
            description = analyze_scene(frame)
            scene_buffer[description].append(timestamp)
    # 合并相似场景
    merged_scenes = []
    used_descriptions = set()
    for desc in scene_buffer:
        if desc in used_descriptions:
            continue
        # 寻找所有相似描述
        similar_group = [d for d in scene_buffer
                         if d not in used_descriptions
                         and is_similar(desc, d)]
        # 合并时间戳
        all_timestamps = []
        for d in similar_group:
            all_timestamps.extend(scene_buffer[d])
            used_descriptions.add(d)
        start = min(all_timestamps)
        end = max(all_timestamps)
        if end - start >= MIN_DURATION:
            merged_scenes.append({
                "start": start,
                "end": end,
                "description": desc.capitalize()
            })

    merged_scenes.sort(key=lambda x: x['start'])
    formatted = [{
        "start": round(s['start'], 1),
        "end": round(s['end'], 1),
        "duration": round(s['end'] - s['start'], 1),
        "description": s['description']
    } for s in merged_scenes]
    cap.release()
    format_result = json.dumps(formatted, indent=2, ensure_ascii=False)
    return json.loads(format_result)  # 解析为 Python 列表


if __name__ == '__main__':
    video_path = config.ROOT_DIR_WIN / "static/source_videos/touch-13-3249676-hd_1920_1080_25fps.mp4"
    result = video_analyze(video_path)
    print(result[0].get("description"))
