DEBUG_MODE = False                              # enables additional logging, and if properly setup in the grammar module:
                                                # - enables module without needing the app in focus, i.e. AppContext()
                                                # - actions only print to console, they don't press virtual keys
DEBUG_HEAVY_DUMP_GRAMMAR = False                # expensive on memory, don't set this to True unless you're sure
                                                # if properly setup in the grammar module:
                                                # - generates a .debug_grammar_*.txt that describes the spec of the active commands
USE_NOISE_SINK = True                           # load NoiseSink rule(s), if it's setup in the grammar module.
                                                # - it should partially capture other noises and words outside of commands, and do nothing.

def my_retain_func(audio_store):
    """Used in retain_approval_func"""
    return not 'NoiseSink' in audio_store.rule_name

# =======================================================
# Index of microphone using.
# You can see the mic list by:
# tacspeakJP.exe --get_audio_sources
#WSR_AUDIO_SOURCE_INDEX = 0

# =======================================================
# Push to talk, mute, toggle setting. Each Modes means:
# 0 - always on (ignore PTT_KEY setting)
# 1 - toggle, initial on
# 2 - toggle, initial off
# 3 - push to talk (mic is opened while pressing key)
# 4 - push to mute (mic is clesed while pressing key)
PTT_MODE = 0
# =======================================================
# Key to use on push to talk.
# You can check keys name which you want to know by:
#     tacspeakJP.exe --get_key_name
# You can identify numpad keys with 'num' e.g. 'num 0', 'num enter'
# You can identify mouse button with 'mouse_' e.g. 'mouse_right', 'mouse_x2'
# Inputs from Tacspeak command is also detected. Pay attension like 1,2,3... or mouse_middle
PTT_KEY = "left shift"
