import sys
from cx_Freeze import setup, Executable


build_options = {
    "excludes":["pytest"],
} 

setup(
    name="tts_tool",
    version="0.1",
    description="tts tool",
    options={"build_exe": build_options},
    executables=[Executable("./src/tts_cli.py")],
)