#
# This file is part of TacspeakJP.
# (c) Copyright 2024 by Domtaro
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

import argparse
import os
import tacspeak
from tacspeak.__main__ import main as tacspeak_main
from dragonfly import get_engine
import logging
from multiprocessing import freeze_support

# import win32com
from win32com.server import util

# import keyboard, mouse for push to talk
import keyboard, mouse

def main():
    print(f"TacspeakJP version {tacspeak.__version__}")
    print_notices()

    parser = argparse.ArgumentParser(description='Start speech recognition.')
    parser.add_argument('--get_audio_sources', action='store_true',
                        help=('see a list of available input devices and their corresponding indexes and names.' 
                                + ' useful for setting `WSR_AUDIO_SOURCE_INDEX` in ./tacspeak/user_settings.py'))
    parser.add_argument('--get_key_name', action='store_true',
                        help=('check a key name you pressed.' 
                                + ' useful for setting `PTT_KEY` in ./tacspeak/user_settings.py'))
    args = parser.parse_args()
    if args.get_audio_sources:
        engine = get_engine('sapi5inproc')
        engine.connect()
        print(engine.get_audio_sources())
        input("Press enter key to exit.")
        return
    if args.get_key_name:
        print("press any keys which you want to check key name.")
        print("input ctrl + c to exit.")
        def on_press_kb(event):
            print(event.name)
        keyboard.on_press(on_press_kb)
        def on_press_mb(event):
            if isinstance(event, mouse.ButtonEvent):
                if event.event_type == "down": print(event.button)
        mouse.hook(on_press_mb)
        keyboard.wait(hotkey="ctrl+c", suppress=False, trigger_on_release=False)
        keyboard.unhook_all_hotkeys()
        mouse.unhook_all()
        return
    tacspeak_main()

def print_notices():
    text = """
    TacspeakJP - Japanese language speech recognition for gaming
    © Copyright 2024 by Domtaro

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
        """
    print(text)

if __name__ == "__main__":
    freeze_support()
    main()