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

#WSR_AUDIO_SOURCE_INDEX = 0                      # index of microphone using. You can see the mic list by:
#                                                # tacspeakJP.exe --get_audio_sources
