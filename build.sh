#!/bin/bash
pyinstaller  --clean -F ./src/tts_cli.py --paths=src --add-data "src/tts_tool:tts_tool" --hidden-import=tts_tool