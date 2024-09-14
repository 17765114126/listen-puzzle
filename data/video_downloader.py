import os
import yt_dlp
from util import file_util


def download_single_video(info, folder_path, resolution='1080p'):
    series = file_util.sanitize_title(info.get('series', ""))
    season = file_util.sanitize_title(info.get('season', ""))
    title = file_util.sanitize_title(info['title'])
    resolution = resolution.replace('p', '')
    ydl_opts = {
        'format': f'bestvideo[ext=mp4][height<={resolution}]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'writeinfojson': True,
        'writethumbnail': True,
        'outtmpl': os.path.join(folder_path, series + season + title),
        'ignoreerrors': True,
        'cookiefile': 'cookies.txt' if os.path.exists("cookies.txt") else None,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([info['webpage_url']])
    return folder_path


def download_from_url(video_url, folder_path, resolution='1080p', num_videos=5):
    if folder_path is None or folder_path == "":
        folder_path = file_util.get_download_folder()
    resolution = resolution.replace('p', '')
    if isinstance(video_url, str):
        video_url = [video_url]

    # Download JSON information first
    ydl_opts = {
        "None": "b",
        'dumpjson': True,
        'playlistend': num_videos,
        'ignoreerrors': True,
        'cookies-from-browser': 'chrome'
    }

    video_info_list = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for u in video_url:
            result = ydl.extract_info(u, download=False)
            if 'entries' in result:
                # Playlist
                video_info_list.extend(result['entries'])
            else:
                # Single video
                video_info_list.append(result)
    for info in video_info_list:
        download_single_video(info, folder_path, resolution)
    return f"视频下载成功，下载地址为： {folder_path}"


if __name__ == '__main__':
    # Bilbili Title 奥巴马开学演讲，纯英文字幕
    video_url = 'https://www.bilibili.com/video/BV1Tt411P72Q/'
    download_from_url(video_url, file_util.get_download_folder())
