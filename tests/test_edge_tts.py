
import os
import sys
import pytest
import asyncio
import json
from src.tts_tool.edge_model import VoiceType

from src.tts_tool.edge_tts import EdgeTTS, VoiceType


current_dir = os.path.dirname(os.path.abspath(__file__))

@pytest.fixture
def edge_tts():
    content = "文字故事通过寓意理解基于定制化的基本漫画角色生成漫画。漫画的故事逻辑与文字故事匹配。很多经验和知识 被经历使用过，但是没有内化 内在的解决问题的能力，是因为在使用中或者经历中没有理解经验和知识的概念（概念需要理解，事实需要记忆,掌握需要练习）"
    voice_type = VoiceType.model_validate({
        "Name": "Microsoft Server Speech Text to Speech Voice (zh-CN, XiaoyiNeural)",
        "ShortName": "zh-CN-XiaoyiNeural",
        "Gender": "Female",
        "Locale": "zh-CN",
        "SuggestedCodec": "audio-24khz-96kbitrate-mono-mp3",#audio-24khz-48kbitrate-mono-mp3
        "FriendlyName": "Microsoft Xiaoyi Online (Natural) - Chinese (Mainland)",
        "Status": "GA",
        "VoiceTag": {
        "ContentCategories": [
            "Cartoon",
            "Novel"
        ],
        "VoicePersonalities": [
            "Lively"
        ]
        }
    })
    return EdgeTTS(content, voice_type, max_len_content_per_tts=int(len(content)/2)+1)

def test_edge_tts_parse_audio_data(edge_tts: EdgeTTS):
    r_audio_data = b'\x00\x80X-RequestId:bc293fb2a5d04da2b6f9a191ce1734fe\r\nContent-Type:audio/mpeg\r\nX-StreamId:DD0436A667194686834958FB0D692EB5\r\nPath:audio\r\n\xff\xf3d\xc4\x00\x00\x00\x03H\x00\x00\x00\x00LAMEUUU\x08\xc3\x83\x081\xde\xf4\xff\xdc\xb3\xe4\xb3\xdd\xf2\x052\x0c,]\x85\x05\x0c\x91C=9\xb8\x00\x8a\x06\x06,\x10\x00\xc8Ns\xd1\x0e\x00\x11\xa7\xd0\x05=\xce\x13\xa1\x07\x17\xfa\'\t\xf8\x97t\x10\x9c@`hN\x06\xff\xa3\x9fb!\x1e\x9c/\xf8\x88T\x0c_\x1d\xcf\xd3\xfa\xf18\x9dD\xaf\xa6 zw\xaf\xaflC#\xbe\xc6|\xd6!7\x19{\x0cf\x1e\x17D1\xae!\xf6\xf6\x0cM\x88\x10\x92u\x1d\xa22\xc9\x93\xa4\xff\xf3d\xc4|\x00\x00\x03H\x00\x00\x00\x00,\x9a\x7f\x98C9\x84\'n\xd8\xcc!\x11\x87\x93H\x04\x8d\xff\x1d\x08\x17\xe2\xe6i\x94\x06+$\x10&L \x1c\xa2\x01\xc3\xad\x94\x12\x18\xd2\x05(\x99U[\xb2\x12\xc9\x1fd\x8d\x0e=\t\x12\x15\x18q\x86\xd0\xaaa\x19\xf15\x8d\xa0!\x92\x89Da\x03)\x8f\x9f\x08%q\x9a\xa7F\xcb*\xc5V\n\'\x03$\xd2\x14\x11\x8a\x874\xe1\x95\xcd\xa8+\xc5\x8f\x9bG\x07\x08\x19B\xa1\x92\xf1\xe5\x100\xa3\xce8\xdcQ\x1d66\x91B8\xbc\xba6\xff\xf3d\xc4\xff#\xf4\t\xf8\x00@\xcd=\xc8\x1c\xb2G\x97C\r\x13\xd3\x13)\x90\' :m\x1d\x16B\x99\x11\x92\x06u\\\xc2\x85\x10\x92\x91E\x1c\x10\x17H\xf9;2`\x8eO:\x92\xa8\x0e6J0@B\xc3Sm\x10\x94\xaaA\xd89\x01\x01\xc3\xc6M\xb2lNN0\xd2\xd1\x10\xac\xb1rr\x8c.\x1f\xb7L-24m\x13\xac\xb1\xd6H\xe4F\x18WD\x05\x19\x01\xd7\x8e\xa6yG\x96`i\x0e7\xd1\xa4\x99\x02\x11\xdc\xe0\xa5\xba`(nL\xb3jM\x1f`Q\x8bZ\x0cH\xff\xf3d\xc4\xf27\xac:\x04\xa0y\x92$\x94\xbbi(\xba\xa8\xe6\xb2d\xe2\xead;h\x10\xca3\xa5\xe4P\xa7\xaa\xba \xea\x9cI\'*\x8cR\x8f\xa8h\x9e\x91\x8a\xd7@A\x93\xa9A\x08\x8e\xd0\x08\xd1\xc9\x18\x8c>\x0c i\xe5\xcf\xac]\xb2>x\xe9!"\xce\xdcUx\x10u\xdbh\xf2\x03\x91\\\xe1\xe5\xdc\x93\xce\x18\x8c\x97!.\xa1\xe6"\xe5Z\xeb\xe6 UG\xd2\x03,U.\x8d\xab^pfeO\xbb\\\xbe4e\t\x9a$:\xb6\xb0\xf5(\x9d\xe4\t\xa0\xc9\xad$zF\xff\xf3d\xc4\x962\x8c:\x10\x08\xc2R\x00\xbd\x1d\xd8\xea\x89\xb7*r\x07\xb54\x11\x9b+%1\xf4\x08\x14qE\x9aU\x00\xe9U\xd6Bm\x1e\xf5\x90*\x8e\xa0w6\x1b%TOu)\xafi\xa3G\xc4\x0c\x97N\x90U\x1a`\x07\x12x^!U\\\xd4\xf3\xe3SI\x1e\xb1b\xdemD\xa3>\xc6\xbcv4\xecL\xca{\xdf\xa5\xa1\x85=\xc7FL\xcd?\'N\xb25\xa917M\x13\xf7DaA\xc2\nH\x18\xa8\xbdC\x10\xe2\xe9\x13\xdb\xf4A\x8av#}\x86\x16\x96\x02\xe8 v'
    response_data = edge_tts.parse_byte_response_data(r_audio_data)
    assert response_data != None

def test_edge_tts(edge_tts: EdgeTTS ):
    edge_tts.execute()
    rst = edge_tts.get_rsts()
    assert rst != None
    assert edge_tts.audio_save(edge_tts.content_md5, current_dir)  != None



#@pytest.fixture
def edge_tts_long(content_file):
    content = ""
    with open(content_file, "r") as f:
        content = f.read()
    voice_type = VoiceType.model_validate({
        "Name": "Microsoft Server Speech Text to Speech Voice (zh-CN, XiaoyiNeural)",
        "ShortName": "zh-CN-XiaoyiNeural",
        "Gender": "Female",
        "Locale": "zh-CN",
        "SuggestedCodec": "audio-24khz-96kbitrate-mono-mp3",#audio-24khz-48kbitrate-mono-mp3
        "FriendlyName": "Microsoft Xiaoyi Online (Natural) - Chinese (Mainland)",
        "Status": "GA",
        "VoiceTag": {
        "ContentCategories": [
            "Cartoon",
            "Novel"
        ],
        "VoicePersonalities": [
            "Lively"
        ]
        }
    })
    return EdgeTTS(content, voice_type, max_len_content_per_tts=int(len(content)/2)+1)

@pytest.mark.parametrize("edge_tts,audiometadatas_file",[
    (edge_tts_long("./tests/test.txt"),"/audiometadatas_long.json"),
     (edge_tts_long("./tests/test2.txt"),"/audiometadatas_long2.json")
])
def test_edge_tts_deal_audio_metadata_for_subtitle_for_long(edge_tts: EdgeTTS, audiometadatas_file):

    with open(current_dir+audiometadatas_file, "r") as f:
        audio_metadatas = json.load(f)
    rsts =  edge_tts.deal_audio_metadata_for_subtitle(audio_metadatas)
    assert rsts != None

def test_edge_tts_subtitle_save(edge_tts: EdgeTTS ):
    edge_tts.execute()
    rst = edge_tts.get_rsts()
    assert rst != None
    assert edge_tts.audio_save(edge_tts.content_md5, current_dir)  != None

    assert edge_tts.subtitle_save(edge_tts.content_md5, current_dir) != None