import sys
import asyncio
import json
from tkinter import OFF
import uuid
from datetime import datetime
from collections import namedtuple
import logging
import re
import time

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
    ["xrequest_id", "content_type", "xstream_id", "path", "audio_data"]
)


class EdgeTTS(TTS):
    """ 微软Edge文本转语音任务器
    根据文本分段并发执行转音

    属性：
        m_l_c: int, 文本分段的长度 

    """

    def __init__(self,
                 content: str,
                 voice_type: VoiceType,
                 max_len_content_per_tts=MAX_LEN_CONTENT_PER_TTS,
                 word_boundary_onoff=False,
                 sentence_boundary_onff=True,
                 ):
        super().__init__(content)
        self.__voice_type = voice_type
        self.m_l_c = max_len_content_per_tts
        self.content_parts = super().partoff_content(self.content, self.m_l_c)
        self.__content_part_num = len(self.content_parts)
        self.rsts = []
        self.execute_process_info = {"process": 0.0}
        self.word_boundary_onoff = word_boundary_onoff
        self.sentence_boundary_onoff = sentence_boundary_onff

    def execute(self):
        """执行文本转语音的任务
        """
        asyncio.run(self.async_execute())

    def execute_process(self) -> float:
        return self.execute_process_info["process"]

    async def show_process_bar(self):
        start_time = time.time()
        print("\n")
        while self.execute_process_info["process"] < 1.0:
            await asyncio.sleep(0.2)
            sys.stdout.write("\r")  # 将光标移动到行首
            p_str = "处理中:"+"#"*int(1+50*self.execute_process_info['process'])+f"%{
                self.execute_process_info['process']*100:.4}"
            sys.stdout.write(p_str)  # 使用空格覆盖当前行的内容
            sys.stdout.write("\r")  # 将光标移动到行首
            sys.stdout.flush()
            diff_time = time.time() - start_time
            if diff_time > 3600:
                return
        sys.stdout.write("\n")
        sys.stdout.write("完成\n")
        sys.stdout.flush()

    async def async_execute(self):
        """切片并发 执行tts 任务
        """
        rsts = [{} for i in range(self.__content_part_num)]
        self.status = TTSStatus.DOING
        try:
            tts_wss_tasks = []
            async with asyncio.TaskGroup() as tg, asyncio.timeout(1200):
                for i in range(self.__content_part_num):
                    content_part = self.content_parts[i]
                    rsts[i].setdefault("origin_content", content_part)
                    tts_wss_task = tg.create_task(
                        self.deal_by_wss(content_part, self.execute_process_info, 1.0/self.__content_part_num), name=i)
                    asyncio.shield(tts_wss_task)
                    tts_wss_tasks.append(tts_wss_task)

            for tts_wss_task in tts_wss_tasks:
                service_tag, audio_info, audio_metadata, audio_bytes = tts_wss_task.result()
                rsts[int(tts_wss_task.get_name())].update(dict(
                    service_tag=service_tag,
                    audio_info=audio_info,
                    audio_metadata=audio_metadata,
                    audio_bytes=audio_bytes
                ))
            self.execute_process_info["process"] = 1.0
        except TimeoutError as ex:
            self.status = TTSStatus.ERROREXIT
            logging.error("TTS 总耗时超时了")
            raise ex
        except Exception as ex:
            self.status = TTSStatus.ERROREXIT
            raise ex
        finally:
            #
            pass
        self.rsts = rsts
        self.status = TTSStatus.COMPLETED if self.status == TTSStatus.DOING else self.status

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
        """ 生成转录内容的消息
        """
        message = f"X-RequestId:{uuid.uuid4().hex}\r\n"
        message += f"X-Timestamp:{self.get_x_timestamp()}\r\n"
        message += "Content-Type:application/ssml+xml\r\n"
        message += "Path:ssml\r\n\r\n"
        message += self.make_voice_type_content_xml(content)
        return message+"\r\n"

    def make_config_message(self, sentence_boundary_onoff=False, word_boundary_onoff=True):
        """ 生成语音配置格式消息
        """
        message = f"X-RequestId:{uuid.uuid4().hex}\r\n"
        message += f"X-Timestamp:{self.get_x_timestamp()}\r\n"
        message += "Content-Type:application/json; charset=utf-8\r\n"
        message += "Path:speech.config\r\n\r\n"
        # # audio-24khz-48kbitrate-mono-mp3
        message += json.dumps({"context": {"synthesis": {"audio": {"metadataoptions": {"sentenceBoundaryEnabled": f"{sentence_boundary_onoff}",
                              "wordBoundaryEnabled": f"{word_boundary_onoff}"}, "outputFormat": f"{self.__voice_type.suggested_codec}"}}}}, ensure_ascii=False)

        return message+"\r\n"

    def parse_str_response_data(self, response_data: str) -> EdgeWsJsonResponse:
        """解析str类型的消息
        """
        data_list = re.split(r"\r\n", response_data)
        return EdgeWsJsonResponse(
            xrequest_id=data_list[0].split(":")[1],
            content_type=data_list[1].split(":")[1],
            path=data_list[2].split(":")[1],
            rst=json.loads(data_list[4])
        )

    def parse_byte_response_data(self, response_data: bytes):
        """解析字节流类型的消息
        """
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

    def make_ws_connect_header(self):
        """ 生成websocket 标头信息
        """

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

    async def deal_by_wss(self, content: str, process_info: dict, process_ratio: float):
        """ 内容转录成语音
        """
        service_tag = ""
        audio_metadata = []
        audio_info = {}
        audio_bytes = bytearray()
        try:
            async with websockets.connect(edge_wss_url.format(connection_id=uuid.uuid4().hex), extra_headers=self.make_ws_connect_header()) as websocket:

                await websocket.send(self.make_config_message(sentence_boundary_onoff=self.sentence_boundary_onoff, word_boundary_onoff=self.word_boundary_onoff))
                await websocket.send(self.make_voice_type_content_message(content))
                while True:
                    response_data = await websocket.recv()
                    if isinstance(response_data, str):
                        response = self.parse_str_response_data(response_data)
                        logging.info(response)
                        if response.path == "turn.start":
                            service_tag = response.rst["context"]["serviceTag"]
                            process_info["process"] += 0.1 * process_ratio
                        elif response.path == "response":
                            audio_info = response.rst
                            process_info["process"] += 0.2 * process_ratio
                        elif response.path == "audio.metadata":
                            audio_metadata.append(response.rst)
                        elif response.path == "turn.end":
                            process_info["process"] += 0.7 * process_ratio
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

    def audio_save(self, filename, filepath, filetype=None):
        """存储音频

        Args:
            filename: str , 文件名称
            filepath: str, 文件路径
            filetype: str=None, 文件类型, 内部自动转换格式,为None 就为原声格式
        """
        super().audio_save(filename, filepath, filetype)
        if not filetype:
            filetype = self.__voice_type.suggested_codec_audio_type
        path_file = f"{filepath}/{filename}.{filetype}"

        with open(path_file, "wb+") as bf:
            for rst in self.rsts:
                if rst.get("audio_bytes", None):
                    bf.write(rst["audio_bytes"])

        return path_file

    def subtitle_save(self, filename, filepath, subtile_type="srt", debug=False):
        """ 存储字幕文件
        """
        super().subtitle_save(filename, filepath, subtile_type)
        path_file = f"{filepath}/{filename}.{subtile_type}"
        audio_metadatas = []
        off_set = 0

        # DEBUG-START debug 模式存储 原始文件
        if debug:
            with open(path_file+".rsts", "w+") as f:
                f.write(json.dumps([rst["audio_metadata"]
                        for rst in self.rsts], ensure_ascii=False, indent=2))
        # DEBUG-END ---------------------

        for rst in self.rsts:
            if rst.get("audio_metadata", None):
                for audio_metadata in rst["audio_metadata"]:
                    for metadata in audio_metadata["Metadata"]:
                        metadata["Data"]["Offset"] += off_set
                    audio_metadatas.extend(audio_metadata["Metadata"])
                off_set = rst["audio_metadata"][-1]["Metadata"][-1]["Data"]["Offset"] + \
                    rst["audio_metadata"][-1]["Metadata"][-1]["Data"]["Duration"]

        # DEBUG-START debug 模式存储处理后的字幕信息
        if debug:
            with open(path_file+".audiometadatas", "w+") as f:
                f.write(json.dumps(audio_metadatas,
                        ensure_ascii=False, indent=2))
        # DEBUG-END ---------------------
        audio_subtile_rsts = self.deal_audio_metadata_for_subtitle(
            audio_metadatas)
        sub_c = ""
        if subtile_type == "srt":
            sub_c = self.srt_converter(audio_subtile_rsts)
        with open(path_file, "w+") as f:
            f.write(sub_c)

        return filepath

    def srt_converter(self, subtile_aduio_metadatas: list[dict]) -> str:
        """SRT 格式转换器
            ^1$
            ^00:00:00,599 --> 00:00:04,160$
            ^>> 爱丽丝：大家好，我叫爱丽丝·米勒。这是约翰·布朗$
        """
        tmps = []
        for i, s in enumerate(subtile_aduio_metadatas, start=1):
            tmp = f"{i}\n{self.mktimestamp(s['aduio_start_timestamp'])}-->{self.mktimestamp(
                s['aduio_end_timestamp'])}\n{s['sentence'].strip(r"\r|\n")}"
            tmps.append(tmp)

        return "\n\n".join(tmps)

    def deal_audio_metadata_for_subtitle(self, audio_metadatas):
        """ 音频元文字处理成元字幕
            {
                "Type": "SentenceBoundary",
                "Data": {
                    "Offset": 91500000,
                    "Duration": 158875000,
                    "text": {
                    "Text": "管理经理的能力：我的理解,掌控自己的精力分配，再需要百分百的精力（全身心投入）投入的时候，就能百分百投入，让自己的做有意义的事情， 什么是有意义，重要且长期有利的事情",
                    "Length": 0,
                    "BoundaryType": "SentenceBoundary"
                        }
                }
            }
        """
        rst = []
        for audio_metadata in audio_metadatas:
            if audio_metadata["Type"] == "SentenceBoundary":
                sentence_start_time = audio_metadata["Data"]["Offset"]
                sentence_end_time = audio_metadata["Data"]["Offset"] + \
                    audio_metadata["Data"]["Duration"]
                sentence = audio_metadata["Data"]["text"]["Text"]
                rst.append({
                    "sentence": sentence,
                    "aduio_start_timestamp": sentence_start_time,
                    "aduio_end_timestamp": sentence_end_time

                })
        return rst
