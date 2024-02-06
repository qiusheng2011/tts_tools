import os
import httpx
from .edge_model import (
    VoiceTag,
    VoiceType
)
from .edge_tts import EdgeTTS
from .tts import TtsSDK


class EdgeTtsSDK(TtsSDK):

    def __init__(self, baseurl=""):
        self.baseurl = baseurl

    def get_voice_type(self, apipath="/consumer/speech/synthesize/readaloud/voices/list", trustedclienttoken="6A5AA1D4EAFF4E9FB37E23D68491D6F4") -> list[VoiceType]:
        """获取发音的类型信息
        """
        api_url = f"{self.baseurl}/{apipath}"
        rst = httpx.get(api_url, params=dict(
            trustedclienttoken=trustedclienttoken))
        if rst.status_code == 200:
            out_l = []
            for i in rst.json():
                out_l.append(VoiceType.model_validate(i))
            return out_l
        else:
            raise rst.raise_for_status()

    def text_to_speech(self, content: str, voice_type: VoiceType):
        tts: EdgeTTS = EdgeTTS(content, voice_type)
        tts.execute()
        rsts = tts.get_rsts()
        return rsts

    def textfile_to_speech_file(self, filepath: str, voice_type: VoiceType, debug=False):
        out_dirpath = os.path.dirname(os.path.abspath(filepath))
        out_filename =  os.path.splitext(os.path.basename(filepath))[0]+f"_vt{voice_type.name_md5}"
        tts = None
        with open(filepath, "r") as f:
            tts: EdgeTTS = EdgeTTS(f.read(), voice_type)
        tts.execute()
        tts.audio_save(out_filename, out_dirpath)
        tts.subtitle_save(out_filename, out_dirpath, debug=debug)
        return 