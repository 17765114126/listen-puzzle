import os
import random
import yt_dlp
from data.util.file_util import sanitize_title
import config
import requests
from urllib.parse import urlencode
from data import use_video_analyse
from mutagen.mp4 import MP4


def dlp_download_video(info, output_dir, resolution='1080p'):
    """
    下载单个视频，并将其保存到指定目录。

    :param info: 包含视频信息的字典
    :param output_dir: 视频输出目录
    :param resolution: 分辨率，默认为'1080p'
    :return: 输出目录路径
    """
    # 清理标题中的非法字符
    series = sanitize_title(info.get('series', ""))
    season = sanitize_title(info.get('season', ""))
    title = sanitize_title(info['title'])

    # 准备下载选项
    ydl_opts = {
        'format': f'bestvideo[ext=mp4][height<={resolution}]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'writeinfojson': False,  # 关闭元数据文件生成
        'writethumbnail': False,  # 关闭缩略图下载
        'outtmpl': os.path.join(output_dir, f"{series}{season}{title}.%(ext)s"),
        'ignoreerrors': True,
        'cookiefile': 'cookies.txt' if os.path.exists("cookies.txt") else None,
        'noplaylist': True,  # 不下载播放列表（仅当前视频）,
        'no_check_certificate': True,  # 跳过 SSL 验证
        'ssl_version': 'TLSv1_2',  # 强制 TLS 1.2
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
    }

    # 执行下载
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([info['webpage_url']])
    return output_dir


def download_videos_from_url(url, output_dir, resolution='1080p', limit=5):
    """
    从给定的URL列表中下载视频。

    :param url: 单个或多个视频/播放列表的URL列表
    :param resolution: 目标分辨率，默认为'1080p'
    :param limit: 如果是播放列表，则限制下载的视频数量
    :return: 下载文件夹路径的消息
    """

    # 设置用于提取视频信息的选项
    extraction_options = {
        'dump_single_json': True,
        'playlistend': limit,
        'ignoreerrors': True,
        'cookies_from_browser': 'chrome'
    }

    # 收集所有要下载的视频信息
    ydl = yt_dlp.YoutubeDL(extraction_options)
    result = ydl.extract_info(url, download=False)

    # 调用download_video进行下载
    dlp_download_video(result, output_dir, resolution)
    title = sanitize_title(result['title']) + ".mp4"
    return title, result['duration']


# pexels视频下载
def search_videos_pexels(
        search_term: str,
        minimum_duration: int,
):
    """
    minimum_duration：所需的视频方向。当前支持的方向为：
    landscape = "16:9"  video_width, video_height = 1920, 1080
    portrait = "9:16"   video_width, video_height = 1080, 1920
    square = "1:1"      video_width, video_height = 1080, 1080
    """
    video_orientation = "landscape"
    video_width, video_height = 1920, 1080
    api_key = (config.pexels_api_keys)
    headers = {
        "Authorization": api_key,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    }
    # Build URL
    params = {"query": search_term, "per_page": 20, "orientation": video_orientation}
    query_url = f"https://api.pexels.com/videos/search?{urlencode(params)}"

    r = requests.get(
        query_url,
        headers=headers,
        proxies=[],
        verify=False,
        timeout=(30, 60),
    )
    response = r.json()
    video_items = []
    if "videos" not in response:
        return video_items
    videos = response["videos"]
    # loop through each video in the result
    for v in videos:
        duration = v["duration"]
        # check if video has desired minimum duration
        if duration < minimum_duration:
            continue
        video_files = v["video_files"]
        # loop through each url to determine the best quality
        for video in video_files:
            w = int(video["width"])
            h = int(video["height"])
            if w == video_width and h == video_height:
                item = {
                    "provider": "pexels",
                    "url": video["link"],
                    "duration": duration,
                    "search_term": search_term
                }
                video_items.append(item)
    return video_items


# pixabay视频下载
def search_videos_pixabay(
        search_term: str,
        minimum_duration: int
):
    video_width, video_height = 1920, 1080
    api_key = config.pixabay_api_keys
    # Build URL
    params = {
        "q": search_term,
        "video_type": "all",  # Accepted values: "all", "film", "animation"
        "per_page": 50,
        "key": api_key,
    }
    query_url = f"https://pixabay.com/api/videos/?{urlencode(params)}"

    r = requests.get(
        query_url, proxies=config.proxy, verify=False, timeout=(30, 60)
    )
    response = r.json()
    video_items = []
    if "hits" not in response:
        return video_items
    videos = response["hits"]
    # loop through each video in the result
    for v in videos:
        duration = v["duration"]
        # check if video has desired minimum duration
        if duration < minimum_duration:
            continue
        video_files = v["videos"]
        # loop through each url to determine the best quality
        for video_type in video_files:
            video = video_files[video_type]
            w = int(video["width"])
            if w >= video_width:
                item = {
                    "provider": "pixabay",
                    "url": video["url"],
                    "duration": duration,
                    "search_term": search_term
                }
                video_items.append(item)
    return video_items


def download_video(video_info):
    # 设置保存目录
    save_dir = config.ROOT_DIR_WIN / config.source_videos_dir
    url = video_info['url']
    duration = video_info['duration']
    # search_term = video_info['search_term']
    """下载单个视频到指定目录"""
    # 创建目录（如果不存在）
    os.makedirs(save_dir, exist_ok=True)
    # 从URL提取文件名
    filename = url.split('/')[-1]
    # 发送请求并下载
    response = requests.get(url, stream=True)
    response.raise_for_status()  # 检查请求状态
    filepath = os.path.join(save_dir, filename)
    # 写入文件
    with open(filepath, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    # 解析视频具体内容
    video_analyse_result = use_video_analyse.video_analyze(filepath)
    # 获取描述
    description = video_analyse_result[0].get("description")
    # 添加元数据
    video = MP4(filepath)
    video["\xa9des"] = description  # 标准描述字段
    video["\xa9alb"] = str(duration)  # 使用专辑字段存储时长
    video.save()
    print(f"已下载：{filename}")
    return True


def read_metadata(filepath):
    # 读取元数据
    try:
        video = MP4(filepath)
        description = video.get("\xa9des", ["无描述"])[0]
        duration = video.get("\xa9alb", ["未知时长"])[0]
        return duration, description
    except Exception as e:
        print(f"读取元数据失败: {str(e)}")
        return {}


def keywords_download(keywords):
    print(f"开始下载任务:")
    for keyword in keywords:
        print(f"关键词:{keyword}")
        video_infos = search_videos_pexels(keyword, 0)
        count = 2
        if len(video_infos) < count:
            print(f"警告：关键词 '{keyword}' 的视频数量不足 {count} 个（实际 {len(video_infos)} 个），跳过下载")
            continue  # 或改为下载所有可用视频
        # 随机选择？个URL
        video_infos = random.sample(video_infos, count)
        # 执行下载
        for video_info in video_infos:
            try:
                download_video(video_info)
            except Exception as e:
                print(f"video_info：{video_info}，下载异常：{e}")
    print("下载任务完成")
    return True


if __name__ == '__main__':
    # Bilbili Title 奥巴马开学演讲，纯英文字幕
    video_url = 'https://www.bilibili.com/video/BV1Tt411P72Q/'
    download_videos_from_url(video_url)
