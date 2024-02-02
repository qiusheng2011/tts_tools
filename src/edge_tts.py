from email import header, message
from email.mime import audio
import json
import uuid
from datetime import datetime
from collections import namedtuple
import logging

import re
from httpx import head
import pytz
import websockets


from .tts import (
    TTS,
    TTSStatus
)
from .edge_model import (
    VoiceTag,
    VoiceType
)

edge_wss_url = "wss://speech.platform.bing.com/consumer/speech/synthesize/readaloud/edge/v1?TrustedClientToken=6A5AA1D4EAFF4E9FB37E23D68491D6F4&ConnectionId={connection_id}"

MAX_LEN_CONTENT_PER_TTS = 742


EdgeWsJsonResponse = namedtuple(
    "EdgeWsJsonResponse", ["xrequest_id", "content_type", "path", "rst"])

EdgeWsAudioResponse = namedtuple(
    "EdgeWsAudioResponse",
    ["xrequest_id", "content_type","xstream_id", "path", "audio_data"]
)
class EdgeTTS(TTS):

    def __init__(self, content: str, voice_type: VoiceType, max_len_content_per_tts=MAX_LEN_CONTENT_PER_TTS):
        super().__init__(content)
        self.__voice_type = voice_type
        self.m_l_c = max_len_content_per_tts
        self.__content_part_num = int(len(self.content)/self.m_l_c) + 1

        self.rsts = []

    async def execute(self):
        rsts = [ None for i in range(self.__content_part_num)]
        self.__status = TTSStatus.DOING
        try:
            for i in range(self.__content_part_num):
                content_part = self.content[i*self.m_l_c:(i+1)*self.m_l_c]
                service_tag, audio_info, audio_metadata, audio_bytes = await self.deal_by_wss(content_part)
                rsts[i] = dict(
                    service_tag=service_tag,
                    audio_info=audio_info,
                    audio_metadata=audio_metadata,
                    audio_bytes=audio_bytes
                )
        except Exception as ex:
            self.__status = TTSStatus.ERROREXIT
            raise ex
        self.rsts = rsts
        self.__status = TTSStatus.COMPLETED

    def get_rsts(self):
        return self.rsts

    def get_x_timestamp(self):
        """
            X-Timestamp:Fri Feb 02 2024 13:45:54 GMT+0800 (China Standard Time)Z

        """
        now = datetime.now(pytz.timezone("Asia/ShangHai"))
        return now.strftime("%a %b %d %y %H:%m:%s GMT+0800 (China Standard Time)Z")

    def make_voice_type_content_xml(self, content):
        xml_c = f"""<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis'  xml:lang='en-US'><voice name='{
            self.__voice_type.name}'> <prosody pitch='+0Hz' rate ='+0%' volume='+0%'>{content}</prosody></voice></speak>"""
        return xml_c

    def make_voice_type_content_message(self, content: str):
        message = f"X-RequestId:{uuid.uuid4().hex}\r\n"
        message += f"X-Timestamp:{self.get_x_timestamp()}\r\n"
        message += "Content-Type:application/ssml+xml\r\n"
        message += "Path:ssml\r\n\r\n"
        message += self.make_voice_type_content_xml(content)
        return message+"\r\n"

    def make_config_message(self):
        message = f"X-RequestId:{uuid.uuid4().hex}\r\n"
        message += f"X-Timestamp:{self.get_x_timestamp()}\r\n"
        message += "Content-Type:application/json; charset=utf-8\r\n"
        message += "Path:speech.config\r\n\r\n"
        # # audio-24khz-48kbitrate-mono-mp3
        message += json.dumps({"context": {"synthesis": {"audio": {"metadataoptions": {"sentenceBoundaryEnabled": "false", "wordBoundaryEnabled": "true"}, "outputFormat": f"{self.__voice_type.suggested_codec}"}}}}, ensure_ascii=False) 

        return message+"\r\n"

    def parse_str_response_data(self, response_data: str) -> EdgeWsJsonResponse:
        data_list = re.split(r"\r\n", response_data)
        return EdgeWsJsonResponse(
            xrequest_id=data_list[0].split(":")[1],
            content_type=data_list[1].split(":")[1],
            path=data_list[2].split(":")[1],
            rst=json.loads(data_list[4])
        )

    def parse_byte_response_data(self, response_data:bytes):
        header_length = int.from_bytes(response_data[:2], "big")
        if len(response_data) <= (header_length+2):
            return None
        data_list = re.split(br"\r\n", response_data[2:])
        return EdgeWsAudioResponse(
            xrequest_id=data_list[0].decode("utf8").split(":")[1],
            content_type=data_list[1].decode("utf8").split(":")[1],
            xstream_id=data_list[2].decode("utf8").split(":")[1],
            path=data_list[3].decode("utf8").split(":")[1],
            audio_data=response_data[header_length+2:]
        )

    def get_ws_connect_header(self):
        headers = {
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "Origin": "chrome-extension://jdiccldimpdaibmpdkjnbmckianbfold",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.41",
        }
        return headers

    async def deal_by_wss(self, content: str):
        service_tag = ""
        audio_metadata = []
        audio_info = {}
        audio_bytes = bytearray()
        try:
            async with websockets.connect(edge_wss_url.format(connection_id=uuid.uuid4().hex), extra_headers=self.get_ws_connect_header()) as websocket:

                await websocket.send(self.make_config_message())
                await websocket.send(self.make_voice_type_content_message(content))
                while True:
                    response_data = await websocket.recv()
                    if isinstance(response_data, str):
                        response = self.parse_str_response_data(response_data)
                        logging.info(response)
                        if response.path == "turn.start":
                            service_tag = response.rst["context"]["serviceTag"]
                        elif response.path == "response":
                            audio_info = response.rst
                        elif response.path == "audio.metadata":
                            audio_metadata.append(response.rst)
                        elif response.path == "turn.end":
                            await websocket.close()
                            break
                        else:
                            pass
                    else:
                        response = self.parse_byte_response_data(response_data)
                        if response and response.path == "audio":
                            audio_bytes.extend(response.audio_data)
        except Exception as ex:
            raise ex
        return service_tag, audio_info, audio_metadata, audio_bytes
