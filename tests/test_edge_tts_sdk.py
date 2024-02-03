
import pytest
import sys, os

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from src.edge_tts_sdk import (
    EdgeTtsSDK,
    VoiceTag,
    VoiceType
)

@pytest.fixture()
def edgesdk() -> EdgeTtsSDK:
    return EdgeTtsSDK(baseurl="https://speech.platform.bing.com")

def test_edge_tts_sdk(edgesdk:EdgeTtsSDK):

    rst = edgesdk.get_voice_type()
    assert rst != None



