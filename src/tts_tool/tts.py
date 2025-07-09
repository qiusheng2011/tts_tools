
from abc import abstractmethod
from enum import Enum
import hashlib
import math
import re


class TTSStatus(Enum):
    """转语音的状态
    """
    # 未开始
    UNSTART = 1
    # 正在进行
    DOING = 2
    # 完成
    COMPLETED = 3
    # 错误中断
    ERROREXIT = 4


class TTS:
    def __init__(self, content: str):
        self.status: TTSStatus = TTSStatus.UNSTART
        self.content = content
        self.content_md5 = hashlib.md5(content.encode()).hexdigest()

    @abstractmethod
    def execute(self):
        """执行
        """
        pass

    @abstractmethod
    def execute_process(self) -> float:
        pass

    @abstractmethod
    def get_rsts(self):
        """获取结果
        """
        pass

    @abstractmethod
    def audio_save(self, filename, filepath, filetype):
        if self.status != TTSStatus.COMPLETED:
            raise ValueError(f"任务处于{self.status.name}状态,无法完成存储")

    @abstractmethod
    def subtitle_save(self, filename, filepath, subtile_type="srt"):
        if self.status != TTSStatus.COMPLETED:
            raise ValueError(f"任务处于{self.status.name}状态,无法完成存储")

    @staticmethod
    def mktimestamp(time_unit: float) -> str:
        """
        mktimestamp returns the timecode of the subtitle.

        The timecode is in the format of 00:00:00.000.

        Returns:
            str: The timecode of the subtitle.
        """
        try:
            hour = math.floor(time_unit / 10**7 / 3600)
            minute = math.floor((time_unit / 10**7 / 60) % 60)
            seconds = (time_unit / 10**7) % 60
        except Exception as ex:
            raise ex
        return f"{hour:02d}:{minute:02d}:{seconds:06.3f}"

    @staticmethod
    def partoff_content(content, m_l_c):
        content_parts = []
        if len(content) <= m_l_c:
            return [content]
        else:
            tmp_index = 0
            while (tmp_index+m_l_c) < len(content):
                step = 0
                while re.match(r"[\u4E00-\u9FFF]",  content[tmp_index+m_l_c+step]):
                    step -= 1
                content_parts.append(content[tmp_index:tmp_index+m_l_c+step+1])
                tmp_index = tmp_index+m_l_c+step+1
            if content[tmp_index:]:
                content_parts.append(content[tmp_index:])
        return content_parts


class TtsSDK():

    def get_voice_type(self):
        pass

    def text_to_speech(self, content, voice_type):
        pass

    def textfile_to_speech_file(self, filepath, voice_type, show_process_bar=False, debug=False):
        pass
