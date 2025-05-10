import json

import prompt_config
import use_llm, use_ffmpeg
from util import file_util
import config


# 分析str字幕文件
def parse_srt(srt_text):
    subs = []
    lines = [line.strip() for line in srt_text.split('\n') if line.strip()]
    i = 0
    while i < len(lines):
        # 跳过序号行
        if lines[i].isdigit():
            i += 1
        else:
            # 处理可能的格式错误
            i += 1
            continue

        time_line = lines[i]
        i += 1
        content_lines = []
        # 收集内容行，直到下一个序号或结束
        while i < len(lines) and not lines[i].isdigit():
            content_lines.append(lines[i])
            i += 1
        content = ' '.join(content_lines)

        # 解析时间线
        start_time, end_time = time_line.split(' --> ')

        # # 转换时间为秒
        # def to_seconds(time_str):
        #     h, m, rest = time_str.split(':', 2)
        #     s, ms = rest.split(',', 1)
        #     return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
        #
        # start = to_seconds(start_time)
        # end = to_seconds(end_time)剪辑
        start = start_time
        end = end_time
        subs.append({'start': start, 'end': end, 'content': content})
    for sub in subs:
        print(f"Start: {sub['start']}s")
        print(f"End: {sub['end']}s")
        print(f"Content: {sub['content']}\n")


if __name__ == '__main__':
    # parse_srt(prompt_config.demo_prompt)
    # creative = use_llm._generate_response(f"""
    # 要求：总结字幕内容生成文案
    # 风格：深度解读，结合人生感悟
    # 时长：1分钟
    # 注意：不要返回任何与文案无关的内容
    # 字幕内容：{prompt_config.demo_prompt}
    # """)
    # print("=========================================================")
    # print(creative)
    creative = """
    我当然知道那不是我的月亮
    但有一刻
    月亮的确照在了我身上
    可生活不是电影
    我也缺少点运气
    我悄然触摸你
    却未曾料想
    你像蒲公英散开了
    到处啊
    都是你的模样
    """
    amount = 5
    keywords_prompt = f"""
    为文案为{creative}的视频生成{amount}个搜索关键词。
    要求：
    1. 搜索词以,分隔
    2. 每个搜索词应由 1-3 个单词组成，始终添加视频的主要主题。
    3. 搜索词只能返回关键词，不要标题和解释性说明
    4. 搜索词必须与视频主题相关。
    5. 仅使用英文搜索词进行回复。
    返回示例:
    search term 1, "search term 2,  search term 3, search term 4, search term 5
    请注意，您必须使用英语生成视频搜索词;不接受中文。
    """

    # script1 = use_llm._generate_response(keywords_prompt)开始时间
    # keywords = script1.strip(",")
    # print("=========================================================")
    # print(keywords)
    # keywords = ["lost love", "moonlight", "dandelion", "chance", "touch"]
    save_dir = config.ROOT_DIR_WIN / "static/source_videos"
    folder_file_names = file_util.get_folder_file_name(save_dir)
    source_infos = []
    for folder_file_name in folder_file_names:
        parts = folder_file_name.split("-")
        source_info = {
            "source_name": folder_file_name,
            "video_duration": parts[1],
            "video_describe": parts[2]
        }
        source_infos.append(source_info)

    clip_prompt = f"""
    {{
  "task": "video_edit_sequence_generator",
  "requirements": {{
    "input": {{
      "creative_script": "{creative}",
      "source_materials": "{source_infos}"
    }},
    "output": {{
      "format": "strict_json",
      "critical_rules": [
        "⚠️ 绝对时间约束: start_time必须小于end_time，且end_time不得超过对应素材的video_duration",
        "⏱ 总时长控制: 所有片段的(end_time - start_time)累计必须等于30秒",
        "🔒 源数据锁定: 必须完整保留source_name的原始哈希值（如3851984）"
      ],
      "technical_specs": [
        "时间格式: 时间码格式强制为HH:MM:SS.mmm（例：00:00:07.500）",
        "帧率兼容: 不同帧率素材转换需保持时间码连续性",
        "安全间隔: 相邻片段至少保留10帧重叠（如24fps需≥0.42秒）"
      ],
      "quality_standards": [
        "转场匹配: dissolve仅限场景渐变，cut用于硬切/静帧",
        "优先级: 情感匹配度 > 构图质量 > 运动连贯性",
        "画中画标记: 需要同屏显示时添加picture_in_picture=true"
      ]
    }},
    "processing_logic": [
      "STEP 1: 语义分析 - 解析文案中的关键词/情感/节奏",
      "STEP 2: 时长校验 - 验证所有end_time ≤ video_duration",
      "STEP 3: 语义映射 - 建立创意脚本关键词与视频描述的匹配矩阵",
      "STEP 3: 节奏规划 - 按『建立-发展-高潮-收尾』结构分配时段",
      "STEP 4: 技术校验 - 确保片段间无黑场/跳帧/分辨率冲突"
      "STEP 5: 冲突解决 - 当规则冲突时按critical_rules > quality_standards优先级处理"
    ]
  }},
  "response_example":     
  [
     {{
      "source_name": "moonlight-120-...-3851984-hd_1920_1080_30fps.mp4",
      "video_duration": 120,
      "start_time": "00:01:05.200",
      "end_time": "00:01:10.800",  // 实际截取5.6秒
      "transition": "dissolve"
    }},
    {{
      "source_name": "dandelion-33-...-4438190-hd_1920_1080_24fps.mp4",
      "video_duration": 33,
      "start_time": "00:00:02.500",
      "end_time": "00:00:08.000",  // 实际截取5.5秒
      "transition": "cut"
    }}
  ],
  "validation_rules": {{
    "error_conditions": [
      "任一end_time超过video_duration → 立即终止并返回错误码1002",
      "总时长偏差超过±0.5秒 → 返回错误码1003",
      "哈希值校验失败 → 返回错误码1004"
    ],
    "warning_conditions": [
      "单片段时长<1秒 → 触发警告码2001",
      "match_score<0.8 → 触发警告码2002"
    ]
  }}
}}
    """
    print("========================剪辑视频提示词=================================")
    print(clip_prompt)
    clip_resp = use_llm._generate_response(clip_prompt)
    print("========================剪辑视频信息返回=================================")
    # 步骤1：定位起始和结束位置
    start = clip_resp.find('[')  # 找到第一个 [ 的位置
    end = clip_resp.rfind(']') + 1  # 找到最后一个 ] 的位置并包含它
    if start == -1 or end == 0:
        raise ValueError("字符串中缺少有效的JSON数组边界 [ 或 ]")
    # 步骤2：提取 [ 和 ] 之间的内容
    json_str = clip_resp[start:end].strip()  # 去除首尾空白
    print(json_str)
    clip_infos = json.loads(json_str)
    use_ffmpeg.concatenate_videos_with_transitions(clip_infos, "output.mp4")
    # for clip_info in clip_infos:
    #     source_name = config.ROOT_DIR_WIN / "static/source_videos" / clip_info.get("source_name")
    #     start_time = clip_info.get("start_time")
    #     end_time = clip_info.get("end_time")
    #     transition = clip_info.get("transition")
