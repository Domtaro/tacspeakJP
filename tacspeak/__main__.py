#
# This file is part of TacspeakJP.
# (c) Copyright 2024 by Domtaro
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Command-module loader for Tacspeak.

It scans the ``./tacspeak/grammar/`` folder and loads any ``_*.py``.
It also loads ``./tacspeak/user_settings.py`` for engine settings.
"""

from __future__ import print_function

import logging
import os.path
import sys

from dragonfly import get_engine
from dragonfly.loader import CommandModuleDirectory, CommandModule
from dragonfly.log import default_levels

# --------------------------------------------------------------------------
# Main event driving loop.

def main():
    user_settings_path = os.path.join(os.getcwd(), os.path.relpath("tacspeak/user_settings.py"))
    user_settings = CommandModule(user_settings_path)
    user_settings.load()
    try:
        DEBUG_MODE = (sys.modules["user_settings"]).DEBUG_MODE
    except Exception:
        print("Failed to load `tacspeak/user_settings.py` DEBUG_MODE. Using default settings as fallback.")
        DEBUG_MODE = False
    try:
        DEBUG_HEAVY_DUMP_GRAMMAR = (sys.modules["user_settings"]).DEBUG_HEAVY_DUMP_GRAMMAR
    except Exception:
        print("Failed to load `tacspeak/user_settings.py` DEBUG_HEAVY_DUMP_GRAMMAR. Using default settings as fallback.")
        DEBUG_HEAVY_DUMP_GRAMMAR = False
    try:
        WSR_AUDIO_SOURCE_INDEX = (sys.modules["user_settings"]).WSR_AUDIO_SOURCE_INDEX
    except Exception:
        if DEBUG_MODE:
            print("Not defined or Failed to load `tacspeak/user_settings.py` WSR_AUDIO_SOURCE_INDEX. keeping mic setting default.")

        WSR_AUDIO_SOURCE_INDEX = None

    def log_handlers():
        log_file_path = os.path.join(os.getcwd(), ".tacspeak.log")
        log_file_handler = logging.FileHandler(log_file_path)
        log_file_formatter = logging.Formatter("%(asctime)s %(name)s (%(levelname)s): %(message)s")
        log_file_handler.setFormatter(log_file_formatter)

        log_stream_handler = logging.StreamHandler()
        log_stream_formatter = logging.Formatter("%(name)s (%(levelname)s): %(message)s")
        log_stream_handler.setFormatter(log_stream_formatter)
        return [log_stream_handler, log_file_handler]
    
    def setup_loggers(use_default_levels=True):
        for name, levels in default_levels.items():
            stderr_level, file_level = levels
            handlers = log_handlers()
            if use_default_levels:
                handlers[0].setLevel(stderr_level)
                handlers[1].setLevel(file_level)
            logger = logging.getLogger(name)
            logger.addHandler(handlers[0])
            logger.addHandler(handlers[1])
            logger.setLevel(min(stderr_level, file_level))
            logger.propagate = False
    
    if DEBUG_MODE:
        setup_loggers(False)
        logging.getLogger('grammar.decode').setLevel(20)
        logging.getLogger('grammar.begin').setLevel(20)
        logging.getLogger('compound').setLevel(20)
        logging.getLogger('engine').setLevel(15)
        logging.getLogger('action.exec').setLevel(10)
    else:
        setup_loggers()

    # Set any configuration options here as keyword arguments.
    engine = get_engine('sapi5inproc')

    # Call connect() now that the engine configuration is set.
    engine.connect()

    # set audio source.
    if WSR_AUDIO_SOURCE_INDEX is not None:
        engine.select_audio_source(WSR_AUDIO_SOURCE_INDEX)

    # Load grammars.
    grammar_path = os.path.join(os.getcwd(), os.path.relpath("tacspeak/grammar/"))
    directory = CommandModuleDirectory(grammar_path)
    directory.load()

    handlers = log_handlers()
    log_recognition = logging.getLogger('on_recognition')
    log_recognition.addHandler(handlers[0])
    log_recognition.addHandler(handlers[1])
    log_recognition.setLevel(20)

    # Define recognition callback functions.
    def on_begin():
        pass

    def on_recognition(words):
        log_recognition.log(20, words)

    def on_failure():
        pass

    def on_end():
        pass

    # Start the engine's main recognition loop
    try:
        print("Ready to listen...")
        engine.do_recognition(on_begin, on_recognition, on_failure, on_end)
    except KeyboardInterrupt:
        print("exit")
        pass

    # Disconnect from the engine, freeing its resources.
    engine.disconnect()


if __name__ == "__main__":
    main()