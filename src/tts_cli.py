import sys
import argparse
from tts_tool import tts
from tts_tool.edge_tts_sdk import EdgeTtsSDK


class TTSCli():

    def __init__(self):
        self.inputfile = ""
        self.parse = self.init_args()
        self.args = None
        self.tts_sdk: tts.TtsSDK = None
        self.list = False
        self.voice_types = {}
        self.voice_type = None

    def init_args(self):
        parse = argparse.ArgumentParser(description="TTS Cli")
        parse.add_argument("-l", "--list", action="store_true")
        parse.add_argument("-i", "--inputfile", metavar="I",
                           type=str, help="文本文件")
        parse.add_argument("-t", "--tts-type", metavar="T",
                           choices=["edge"], default="edge")
        parse.add_argument("-v", "--voice-type", metavar="v")
        return parse

    def parse_args(self, *args, **kwargs):
        self.args = self.parse.parse_args(*args, **kwargs)
        self.inputfile = self.args.inputfile

        if self.args.tts_type == "edge":
            self.tts_sdk = EdgeTtsSDK("https://speech.platform.bing.com")
            types = self.tts_sdk.get_voice_type()
            self.voice_types = dict([(t.friendly_name, t)for t in types])
            if self.args.voice_type:
                self.voice_type = self.voice_types.get(
                    self.args.voice_type, None)
        self.list = self.args.list

    def execute(self, show_process_bar=False, debug=False):
        if self.list:
            print("\n".join([f"{k}\t{o.name_md5}" for k,
                  o in self.voice_types.items()]))
        elif self.inputfile and self.voice_type:
            self.tts_sdk.textfile_to_speech_file(
                self.inputfile, self.voice_type, show_process_bar=show_process_bar, debug=debug)


def main():
    tts_cli = TTSCli()
    tts_cli.parse_args()
    tts_cli.execute(show_process_bar=True)


if __name__ == "__main__":
    main()
