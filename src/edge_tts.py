from email.mime import audio
import json
import uuid
from datetime import datetime
from collections import namedtuple

import re
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


EdgeWsJsonResponse = namedtuple("EdgeWsJsonResponse",["xrequest_id", "content_type", "path", "rst"])

class EdgeTTS(TTS):

    def __init__(self, content: str, voice_type: VoiceType, max_len_content_per_tts=MAX_LEN_CONTENT_PER_TTS):
        super().__init__(content)
        self.__voice_type = voice_type
        self.m_l_c = max_len_content_per_tts
        self.__content_part_num = len(self.__content)%self.m_l_c +1
        self.rst = {}

    async def execute(self):
        rst = {}
        self.__status = TTSStatus.DOING
        try:
            for i in range(self.__content_part_num):
                content_part = self.__content[i*self.m_l_c:(i+1)*self.m_l_c]
                service_tag, audio_info, audio_metadata, audio_bytes = self.deal_by_wss(content_part)
                rst[i] = dict(
                    service_tag=service_tag,
                    audio_info=audio_info,
                    audio_metadata=audio_metadata,
                    audio_bytes=audio_bytes
                )
        except Exception as ex:
            self.__status = TTSStatus.ERROREXIT
            print(ex)
        self.rst = rst
        self.__status = TTSStatus.COMPLETED

    def get_rst(self):
        return self.rst

    def get_x_timestamp(self):
        """
            X-Timestamp:Fri Feb 02 2024 13:45:54 GMT+0800 (China Standard Time)Z

        """
        now = datetime.now(pytz.timezone("Asia/ShangHai"))
        return now.strftime("%a %b %d %y %H:%m:%s GMT+0800 (China Standard Time)Z")

    
    def make_voice_type_content_xml(self, content):
        xml_c = f"<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis'  xml:lang='en-US'><voice name='{self.__voice_type.name}'><prosody pitch='+0Hz' rate ='+0%' volume='+0%'>{content}</prosody></voice></speak>"
        return xml_c
    
    def make_voice_type_content_message(self, content:str):
        message = f"X-Timestamp:{self.get_x_timestamp()}\n"
        message += "Content-Type:application/ssml+xml\n"
        message += "Path:ssml\n"
        message += self.make_voice_type_content_xml(content)
        return message
    
    def make_config_message(self):
        message = f"X-Timestamp:{self.get_x_timestamp()}\n"
        message += "Content-Type:application/json; charset=utf-8\n"
        message += "Path:speech.config\n"
        message += json.dumps({"context": {"synthesis": {"audio": {"metadataoptions": {"sentenceBoundaryEnabled": "false",
                              "wordBoundaryEnabled": "true"}, "outputFormat": "webm-24khz-16bit-mono-opus"}}}})
        return message

    def parse_str_response_data(self, response_data:str) -> EdgeWsJsonResponse:
        data_list = re.split(r"\r\n", response_data)
        return EdgeWsJsonResponse(
            xrequest_id=data_list[0],
            content_type=data_list[1],
            path=data_list[2],
            rst=json.loads(data_list[3])
        )
    
    async def deal_by_wss(self, content: str):
        service_tag = ""
        audio_metadata = []
        audio_info = {}
        audio_bytes = bytearray()
        async with websockets.connect(edge_wss_url.format(connection_id=uuid.uuid4().hex)) as websocket:
            
            await websocket.send(self.make_config_message())
            await websocket.send(self.make_voice_type_content_message(content))
            while True:
                response_data  = await websocket.recv()
                if isinstance(response_data, str):
                    response = self.parse_str_response_data(response_data)
                    if response.path == "start":
                        service_tag = response.rst["context"]["serviceTag"]
                    elif response.path == "response":
                        audio_info = response.rst
                    elif response.path == "metadata":
                        audio_metadata.append(response.rst)
                    elif response.path == "end":
                        await websocket.close()
                        break
                    else:
                        pass
                else:
                    audio_bytes.append(response_data)
            return service_tag, audio_info, audio_metadata, audio_bytes



