from moviepy.editor import (VideoFileClip,
                            concatenate_videoclips,
                            AudioFileClip,
                            TextClip,
                            ImageClip)


# 视频剪辑
def clip_video(video_file, t_start, t_end, output):
    clip = VideoFileClip(video_file)
    clip = clip.subclip(t_start, t_end)  # 裁剪视频的第5秒到第10秒
    clip.write_videofile(output)


# 视频拼接
def split_joint(video_one, video_two, output):
    clip1 = VideoFileClip(video_one)
    clip2 = VideoFileClip(video_two)
    final_clip = concatenate_videoclips([clip1, clip2])
    final_clip.write_videofile(output)


# 添加音频
def add_audio(video_file, audio_file, output):
    video = VideoFileClip(video_file)
    audio = AudioFileClip(audio_file)
    video_with_audio = video.set_audio(audio)
    video_with_audio.write_videofile(output)


# 提取视频
def get_video(video_file, output):
    video = VideoFileClip(video_file)
    # 提取视频（不包含音频）
    video_without_audio = video.without_audio()
    # 保存视频文件
    video_without_audio.write_videofile(output, codec='libx264', threads=4)


# 提取音频
def get_audio(video_file, output):
    video = VideoFileClip(video_file)
    audio = video.audio
    audio.write_audiofile(output)


# 添加字幕
def add_subtitle(video_file, output):
    video = VideoFileClip(video_file)
    subtitle = TextClip("Hello, World!", fontsize=24, color='white')
    subtitle = subtitle.set_position(('center', 'bottom')).set_duration(video.duration)
    final_video = CompositeVideoClip([video, subtitle])
    final_video.write_videofile(output)


# 调整视频速度
def change_speed(video_file, output):
    clip = VideoFileClip(video_file)
    faster_clip = clip.speedx(2)  # 加速视频速度为原来的2倍
    faster_clip.write_videaclass(output)


# 调整视频分辨率
def change_resolution(video_file, output):
    clip = VideoFileClip(video_file)
    resized_clip = clip.resize(height=480)  # 将视频高度调整为480像素
    resized_clip.write_videofile(output)


# 应用滤镜和效果：对视频应用各种滤镜和效果。
def change_effect(video_file, output):
    clip = VideoFileClip(video_file)
    image_clip = ImageClip("my_image.png").set_duration(clip.duration)
    final_clip = CompositeVideoClip([clip, image_clip.set_position(('center', 'center'))])
    final_clip.write_videofile(output)


if __name__ == '__main__':
    video_path = "D:/abm.mp4"
    video_output = "D:/output.mp4"
    audio_output = "D:/output.mp3"
    # clip_video(video_path, 60, 67, video_output)
    # split_joint("D:/1.mp4", "D:/2.mp4", video_output)
    get_audio(video_path, audio_output)
    # get_video(video_path, video_output)