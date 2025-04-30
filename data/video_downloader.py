import os
import yt_dlp
from data.util.file_util import sanitize_title


def download_video(info, output_dir, resolution='1080p'):
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
        'writeinfojson': True,
        'writethumbnail': True,
        'outtmpl': os.path.join(output_dir, f"{series}{season}{title}.%(ext)s"),
        'ignoreerrors': True,
        'cookiefile': 'cookies.txt' if os.path.exists("cookies.txt") else None,
        'noplaylist': True,  # 不下载播放列表（仅当前视频）,
    }

    # 执行下载
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([info['webpage_url']])
    return output_dir


def download_videos_from_urls(urls, output_dir, resolution='1080p', limit=5):
    """
    从给定的URL列表中下载视频。

    :param urls: 单个或多个视频/播放列表的URL列表
    :param resolution: 目标分辨率，默认为'1080p'
    :param limit: 如果是播放列表，则限制下载的视频数量
    :return: 下载文件夹路径的消息
    """
    # 将通过竖线分隔的字符串转换为列表
    url_list = [url.strip() for url in urls.split('|') if url.strip()]

    # 设置用于提取视频信息的选项
    extraction_options = {
        'dump_single_json': True,
        'playlistend': limit,
        'ignoreerrors': True,
        'cookies_from_browser': 'chrome'
    }

    # 收集所有要下载的视频信息
    video_info_list = []
    with yt_dlp.YoutubeDL(extraction_options) as ydl:
        for url in url_list:
            result = ydl.extract_info(url, download=False)
            if 'entries' in result:
                # 如果结果包含条目，说明这是个播放列表
                video_info_list.extend(result['entries'])
            else:
                # 否则，它是单个视频
                video_info_list.append(result)

    # 对于每个视频信息，调用download_video进行下载
    for video_info in video_info_list:
        download_video(video_info, output_dir, resolution)
    title = sanitize_title(video_info_list[0]['title'])
    title += ".mp4"
    return title


if __name__ == '__main__':
    # Bilbili Title 奥巴马开学演讲，纯英文字幕
    video_url = 'https://www.bilibili.com/video/BV1Tt411P72Q/'
    download_videos_from_urls(video_url)
