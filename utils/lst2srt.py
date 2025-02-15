def list_to_srt(transcribe_list, srt_filename="output.srt"):
    """
    将字幕列表转换为SRT字幕文件。

    参数:
        subtitle_list (list): 包含字幕信息的字典列表。每个字典应包含 'start', 'end', 'text' 键。
        srt_filename (str, 可选): 输出SRT文件的文件名。默认为 "output.srt"。
    """
    with open(srt_filename, 'w', encoding='utf-8') as srt_file:
        for index, subtitle in enumerate(transcribe_list):
            start_time = format_srt_time(subtitle['start'])
            end_time = format_srt_time(subtitle['end'])
            text = subtitle['text']

            # 写入SRT格式的字幕段
            srt_file.write(str(index + 1) + '\n') # 字幕序号
            srt_file.write(f"{start_time} --> {end_time}\n") # 时间轴
            srt_file.write(text + '\n\n') # 字幕文本 (加两个换行符分隔段落)

def format_srt_time(time_in_seconds):
    """
    将秒数转换为SRT格式的时间字符串 (HH:MM:SS,毫秒)。

    参数:
        time_in_seconds (float): 以秒为单位的时间。

    返回:
        str: SRT格式的时间字符串。
    """
    milliseconds = int(round(time_in_seconds * 1000))
    hours = milliseconds // 3600000
    milliseconds %= 3600000
    minutes = milliseconds // 60000
    milliseconds %= 60000
    seconds = milliseconds // 1000
    milliseconds %= 1000

    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

if __name__ == '__main__':
    # 您的字幕列表
    subtitle_list = [{'id': 0, 'seek': 0, 'start': 0.0, 'end': 1.72, 'text': '在這四倍K信仗', 'tokens': [50364, 3581, 2664, 19425, 35477, 42, 17665, 1550, 245, 50450], 'temperature': 0.0, 'avg_logprob': -0.8799431059095595, 'compression_ratio': 0.872093023255814, 'no_speech_prob': 0.019094958901405334}, {'id': 1, 'seek': 0, 'start': 1.72, 'end': 5.6000000000000005, 'text': '我們計畫去Paris 西賞FART 塔和波浮宮的美景', 'tokens': [50450, 5884, 30114, 43822, 6734, 47, 27489, 220, 16220, 13352, 252, 37, 1899, 51, 220, 23965, 12565, 30806, 11038, 106, 39194, 1546, 9175, 50218, 50644], 'temperature': 0.0, 'avg_logprob': -0.8799431059095595, 'compression_ratio': 0.872093023255814, 'no_speech_prob': 0.019094958901405334}]

    # 调用函数生成SRT文件，默认文件名为 "output.srt"
    list_to_srt(subtitle_list)

    print("SRT 字幕文件 'output.srt' 已生成。")