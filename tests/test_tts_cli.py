import pytest
from src.tts_tool.tts_cli import (
    TTSCli
)
@pytest.mark.parametrize("file_path",[
    "./tests/test.txt",
    "./tests/test2.txt"
])
def test_tts_cli(file_path):
    tts_cli = TTSCli()
    tts_cli.parse_args(("-i",file_path, "-v","Microsoft Yunjian Online (Natural) - Chinese (Mainland)"))
    tts_cli.execute(debug=True)

def test_tts_cli_show_process_bar():
    tts_cli = TTSCli()
    tts_cli.parse_args(("-i", "./tests/test.txt", "-v","Microsoft Yunjian Online (Natural) - Chinese (Mainland)"))
    tts_cli.execute(show_process_bar=True,debug=True)