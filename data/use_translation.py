import translators as ts
from util import file_util
import os


# 搜索引擎
# bing - 必应
# sogou - 搜狗
# alibaba 阿里云
# caiyun - 彩云小译
# deepl -DeepL

# 支持语言
# zh - 中文
# ar - 阿拉伯语
# de - 德语
# en - 英语
# es - 西班牙语
# fr - 法语
# ja - 日语
# ko - 韩语
# ru - 俄语
# vi - 越南语
# pt - 葡萄牙语
# id - 印度尼西亚语

# 单句翻译
def translator_response(messages, to_language='zh', translator_server='bing'):
    return ts.translate_text(query_text=messages, translator=translator_server, from_language='auto',
                             to_language=to_language)


# 批量翻译
def batch_translate(texts, to_lang='zh', translator_server='bing'):
    translations = []
    for text in texts:
        translation = ts.translate_text(query_text=text, translator=translator_server, from_language='auto',
                                        to_language=to_lang)
        translations.append(translation)
    return translations


# def subtitle_translate(file_url, translator_engine, subtitle_language, subtitle_bilingual):
#     # 读取SRT文件内容
#     content = file_util.get_file_content(file_url)
#     # # 解析SRT内容
#     parsed_subtitles = []
#     for entry in content:
#         lines = entry.split('\n')
#         if len(lines) >= 3:
#             index = lines[0]
#             time_range = lines[1]
#             text = '\n'.join(lines[2:])
#             parsed_subtitles.append((index, time_range, text))
#     # 提取所有需要翻译的文本
#     texts_to_translate = [text for _, _, text in parsed_subtitles]
#     # 批量翻译
#     translated_texts = batch_translate(texts_to_translate, subtitle_language, translator_engine)
#
#     if subtitle_bilingual:
#         # 更新字幕条目中的文本，创建双语文本
#         translated_subtitles = []
#         for (index, time_range, original_text), translated_text in zip(parsed_subtitles, translated_texts):
#             # 每行原文后面加上翻译，用换行符分隔
#             bilingual_text = "\n".join([f"{orig} {translated}" for orig, translated in
#                                         zip(original_text.split('\n'), translated_text.split('\n'))])
#             translated_subtitles.append((index, time_range, bilingual_text))
#     else:
#         # 更新字幕条目中的文本
#         translated_subtitles = [(index, time_range, translated_text) for (index, time_range, _), translated_text in
#                                 zip(parsed_subtitles, translated_texts)]
#     # 写入新的SRT文件
#     with open(os.path.join(file_util.get_download_folder(), "translated_" + file_util.get_file_name(file_url) + '.srt'),
#               'w', encoding='utf-8') as file:
#         for index, time_range, text in translated_subtitles:
#             file.write(f"{index}\n{time_range}\n{text}\n\n")
#     return '字幕翻译成功，文件在下载文件夹下'


if __name__ == '__main__':
    # response = translator_response('你好，最近怎么样？ ', 'en', 'youdao')
    # print(response)
    response1 = translator_response('how are you?', 'zh', 'bing')
    print(response1)
    # response = batch_translate(['Hello', 'how are you?'], 'zh', 'bing')
    # print(response)
