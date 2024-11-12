import os
import xxhash


def hash_file(file_path):
    """计算文件的xxHash哈希值"""
    h = xxhash.xxh64()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def find_duplicates(directory):
    """查找目录中的重复文件"""
    duplicates = {}

    # 遍历目录中的所有文件
    for root, _, files in os.walk(directory):
        file_sizes = {}
        for file in files:
            file_path = os.path.join(root, file)
            try:
                # 获取文件大小
                file_size = os.path.getsize(file_path)
                if file_size in file_sizes:
                    # 如果文件大小已经存在，计算哈希值
                    file_hash = hash_file(file_path)
                    if file_hash in duplicates:
                        duplicates[file_hash].append(file_path)
                    else:
                        duplicates[file_hash] = [file_sizes[file_size], file_path]
                else:
                    # 如果文件大小不存在，记录文件大小
                    file_sizes[file_size] = file_path
            except OSError as e:
                print(f"无法读取文件: {file_path}, 错误: {e}")
                continue

    # 移除没有重复的文件条目
    duplicates = {k: v for k, v in duplicates.items() if len(v) > 1}

    return duplicates


# 文件重复查找器  (多线程并不总是能提高性能，特别是在I/O密集型任务中。文件读取速度是瓶颈，多线程不会有太大帮助。)
def run_duplicates(directory_to_search):
    duplicates = find_duplicates(directory_to_search)

    if duplicates:
        result = "找到重复文件:\n"
        for hash_value, files in duplicates.items():
            result += f"哈希值 {hash_value}:\n"
            for file in files:
                result += f"  {file}\n"
    else:
        result = "没有找到重复文件。"

    return result


if __name__ == '__main__':
    directory_to_search = 'D:\\opt'  # 替换为你要搜索的目录路径
    print(run_duplicates(directory_to_search))
