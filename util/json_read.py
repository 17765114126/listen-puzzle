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
    with open(json_path, 'r') as file:
        data = json.load(file)
    return get_value(data, keys)


# 示例
if __name__ == '__main__':
    print(read_config('mysql', 'port'))
