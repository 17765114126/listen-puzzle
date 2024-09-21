import json
import os


# 递归获取多级键值
def get_value(d, keys):
    if len(keys) == 1:
        return d[keys[0]]
    else:
        return get_value(d[keys[0]], keys[1:])


# 读取指定配置文件配置
def read_url_config(json_url, *keys):
    """
    读取 JSON 配置文件并返回指定键的值。

    :param json_url: JSON 文件的路径
    :param keys: 键名，可以是一个或多个
    :return: 指定键的值
    """
    with open(json_url, 'r') as file:
        data = json.load(file)
    return get_value(data, keys)


# 读取默认配置文件配置（项目根目录的config.json）
def read_config(*keys):
    """
    读取 JSON 配置文件并返回指定键的值。

    :param keys: 键名，可以是一个或多个
    :return: 指定键的值
    """
    # 获取项目根目录
    current_file_path = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file_path)
    project_root = os.path.dirname(current_dir)
    json_path = os.path.join(project_root, 'config.json')
    with open(json_path, 'r', encoding='utf-8', errors='ignore') as file:
        data = json.load(file)
    return get_value(data, keys)


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


# 示例
if __name__ == '__main__':
    print(read_config('mysql', 'port'))
