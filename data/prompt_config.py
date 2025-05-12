def keywords_prompt(creative):
    return f"""
    为文案为{creative}的视频生成3个搜索关键词。
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


def clip_prompt(creative, source_infos):
    return f"""
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
