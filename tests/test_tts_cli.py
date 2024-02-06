import pytest
from src.tts_cli import (
    TTSCli
)

def test_tts_cli():
    tts_cli = TTSCli()
    tts_cli.parse_args(("-i", "./tests/test.txt", "-v","Microsoft Yunjian Online (Natural) - Chinese (Mainland)"))
    tts_cli.execute(debug=True)