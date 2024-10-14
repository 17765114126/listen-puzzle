import json
import os


def json_format(response):
    """
    格式化 HTTP 响应中的 JSON 数据为易读的字符串形式。
    :param response: requests 库返回的 Response 对象
    :return: 格式化的 JSON 字符串
    """
    try:
        # 解码响应内容
        decoded_content = response.content.decode('utf-8')

        # 将字符串解析为 JSON 对象
        parsed_json = json.loads(decoded_content)

        # 格式化 JSON 为易读的字符串
        # formatted_json = json.dumps(parsed_json, indent=4, separators=(',', ': '))
        return parsed_json
    except UnicodeDecodeError as e:
        print(f"UnicodeDecodeError: {e}")
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: {e}")
