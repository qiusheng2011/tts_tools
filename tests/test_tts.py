import pytest
from src.tts import (
    TTS
)
import re

@pytest.mark.parametrize('m_l_c,content_file',
[
    (100, "./tests/test.txt"),
    (1000, "./tests/test.txt"),
     (1000, "./tests/test2.txt")
]                         
)
def test_partoff_content(m_l_c:int, content_file:str):
    with open(content_file, "r") as f:
        content = f.read()
        rsts = TTS.partoff_content(content, m_l_c)
        assert rsts != None
        assert "".join(rsts) == content
