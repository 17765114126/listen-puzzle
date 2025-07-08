def keywords_prompt(creative):
    return f"""
    根据下面的文案生成2个高度相关的视频搜索关键词：
    {creative}
    要求：
    1. 搜索词以,分隔
    2. 每个搜索词应由 1-3 个单词组成，始终添加视频的主要主题。
    3. 搜索词只能返回关键词，不要标题和解释性说明
    4. 仅使用英文搜索词进行回复。
    返回示例:
    search term 1, "search term 2,  search term 3
    注意，必须使用英语生成视频搜索词;不接受中文。
    """


def clip_prompt(creative, source_infos, duration):
    return f"""
        {{
      "task": "根据给出的source_materials给出剪辑如response_example的信息",
      "requirements": {{
        "input": {{
          "creative_script": "{creative}",
          "source_materials": "{source_infos}"
        }},
        "output": {{
          "format": "strict_json",
          "critical_rules": [
            "⚠️ 绝对时间约束: start_time全部等于00:00:00.000" 
            "⚠️ 绝对时间约束: start_time全部等于00:00:00.000" 
            "⚠️ 绝对时间约束: end_time < duration",
            "⏱ 总时长控制: 所有片段的(end_time)累计必须等于{duration}秒",
            "🔒 源数据锁定: 必须完整保留source_name的原始哈希值（如3851984）"
            "⚠️ 与主题creative_script无关的source_info不要反回"
          ],
          "technical_specs": [
            "时间格式: 时间码格式强制为HH:MM:SS.mmm（例：00:00:07.500）",
            "帧率兼容: 不同帧率素材转换需保持时间码连续性",
            "安全间隔: 相邻片段至少保留10帧重叠（如24fps需≥0.42秒）"
          ],
          "quality_standards": [
            "转场匹配: dissolve仅限场景渐变，cut用于硬切/静帧",
            "优先级: 情感匹配度 > 构图质量 > 运动连贯性"          
            ]
        }},
        "processing_logic": [
          "STEP 1: 语义分析 - 解析文案中的关键词/情感/节奏",
          "STEP 2: 时长校验 - 验证所有end_time ≤ duration",
          "STEP 3: 节奏规划 - 按『建立-发展-高潮-收尾』结构分配时段",
      }},
      "response_example":     
      [
         {{
          "id": 1,
          "duration": 15,
          "start_time": "00:00:00.000",
          "end_time": "00:00:12.000",
          "transition": "dissolve"
        }},
        {{
          "id": 2,
          "duration": 20,
          "start_time": "00:00:00.000",
          "end_time": "00:00:18.000",
          "transition": "cut"
        }}
      ]
    }}
        """
