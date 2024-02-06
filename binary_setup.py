import sys
from cx_Freeze import setup, Executable


build_options = {
    "excludes":["pytest"],
} 
base = "Win32GUI" if sys.platform == "win32" else None

setup(
    name="tts_tool",
    version="0.1",
    description="tts tool",
    options={"build_exe": build_options},
    executables=[Executable("tts_cli.py", base=base)],
)