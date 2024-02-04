
from abc import abstractmethod
from enum import Enum
import hashlib


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
        pass

    @abstractmethod
    def subtitle_save(self):
        pass


