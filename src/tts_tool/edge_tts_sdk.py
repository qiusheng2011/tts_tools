import asyncio
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
        self.tts_process_info = None

    def get_voice_type(self, apipath="/consumer/speech/synthesize/readaloud/voices/list", trustedclienttoken="6A5AA1D4EAFF4E9FB37E23D68491D6F4") -> list[VoiceType]:
        """获取发音的类型信息
            https://speech.platform.bing.com/consumer/speech/synthesize/readaloud/voices/list?trustedclienttoken=6A5AA1D4EAFF4E9FB37E23D68491D6F4&Sec-MS-GEC=9811368F1C5FE18BAD86F73BD5CC28C8CE3D9104A830C305CC317C63CEAFDCA0&Sec-MS-GEC-Version=1-132.0.2957.140
        """
        api_url = f"{self.baseurl}/{apipath}"
        rst = httpx.get(
            api_url,
            params={
                "trustedclienttoken": trustedclienttoken,
                "Sec-Ms-GEC": "9811368F1C5FE18BAD86F73BD5CC28C8CE3D9104A830C305CC317C63CEAFDCA0",
                "Sec-MS-GEC-Version": "1-132.0.2957.140"
            },
            verify=False
        )

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

    def textfile_to_speech_file(self, filepath: str, voice_type: VoiceType, show_process_bar=False, debug=False):
        asyncio.run(self.aio_textfile_to_speech_file(
            filepath, voice_type, show_process_bar, debug))

    async def aio_textfile_to_speech_file(self, filepath: str, voice_type: VoiceType, show_process_bar=False, debug=False):
        out_dirpath = os.path.dirname(os.path.abspath(filepath))
        out_filename = os.path.splitext(os.path.basename(filepath))[
            0]+f"_vt{voice_type.name_md5}"
        tts = None
        with open(filepath, "r") as f:
            tts: EdgeTTS = EdgeTTS(f.read(), voice_type)
        try:
            if show_process_bar:
                tasks = []
                async with asyncio.TaskGroup() as tg:
                    tasks.append(tg.create_task(tts.async_execute()))
                    tasks.append(tg.create_task(tts.show_process_bar()))
            else:
                await tts.async_execute()
        except Exception as ex:
            raise ex
        tts.audio_save(out_filename, out_dirpath)
        tts.subtitle_save(out_filename, out_dirpath, debug=debug)
        return
