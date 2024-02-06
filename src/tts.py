
from abc import abstractmethod
from enum import Enum
import hashlib
import math

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
    def __init__(self, content:str):
        self.status: TTSStatus = TTSStatus.UNSTART
        self.content = content
        self.content_md5 = hashlib.md5(content.encode()).hexdigest()

    @abstractmethod
    def execute(self):
        """执行
        """
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
    def subtitle_save(self,filename, filepath, subtile_type="srt"):
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
        hour = math.floor(time_unit / 10**7 / 3600)
        minute = math.floor((time_unit / 10**7 / 60) % 60)
        seconds = (time_unit / 10**7) % 60
        return f"{hour:02d}:{minute:02d}:{seconds:06.3f}"



class TtsSDK():


    def get_voice_type(self):
        pass

    def text_to_speech(self, content, voice_type):
        pass

    def textfile_to_speech_file(self, filepath, voice_type, debug=False):
        pass