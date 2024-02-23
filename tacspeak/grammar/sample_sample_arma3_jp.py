#
# This file is part of TacspeakJP.
# (c) Copyright 2024 by Domtaro
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

import sys
from dragonfly import (BasicRule, CompoundRule, MappingRule, RuleRef, Repetition, RecognitionObserver,
                       Function, Choice, IntegerRef, Grammar, Alternative, Literal, Text, Optional,
                       AppContext, Dictation)
from dragonfly.actions import (Key, Mouse, ActionBase, action_function)

import os
import re
import copy

# ---------------------------------------------------------------------------
# Check DEBUG_MODE (from user_settings)

try:
    DEBUG_MODE = (sys.modules["user_settings"]).DEBUG_MODE
except Exception:
    DEBUG_MODE = False

try:
    DEBUG_HEAVY_DUMP_GRAMMAR = (sys.modules["user_settings"]).DEBUG_HEAVY_DUMP_GRAMMAR
except Exception:
    DEBUG_HEAVY_DUMP_GRAMMAR = False

# whether or not to load NoiseSink rule to grammar_priority
try:
    USE_NOISE_SINK = (sys.modules["user_settings"]).USE_NOISE_SINK
except Exception:
    USE_NOISE_SINK = False

# DEBUG_MODE = True # if you want to override
# DEBUG_HEAVY_DUMP_GRAMMAR = True # if you want to override
# USE_NOISE_SINK = False # if you want to override

# ---------------------------------------------------------------------------
# Create this module's grammar and the context under which it'll be active.
if DEBUG_MODE:
    grammar_context = AppContext()
else:
    grammar_context = AppContext(executable="Arma 3")
grammar = Grammar("Arma3",
                  context=grammar_context,
                  )
grammar_priority = Grammar("Arma3_priority",
                           context=grammar_context,
                           )

# ---------------------------------------------------------------------------
# Variables used by grammar, rules, recognition observers below
# Users should be able to look here first for customisation

# Will map keybindings to print()
DEBUG_NOCMD_PRINT_ONLY = DEBUG_MODE

# the minimum time between keys state changes (e.g. pressed then released),
# it's to make sure key presses are registered in-game
# min_delay = 3.3  # 100/(30 fps) = 3.3 (/100 seconds between frames)
min_delay = 5

# map of action to in-game key bindings
# https://dragonfly.readthedocs.io/en/latest/actions.html#key-names
# https://dragonfly.readthedocs.io/en/latest/actions.html#mouse-specification-format

# default key bindings, use when failed to set automatically
ingame_key_bindings = {
    "unit_all": ("com_shift", "space",),
    "unit_1": ("f1",),
    "unit_2": ("f2",),
    "unit_3": ("f3",),
    "unit_4": ("f4",),
    "unit_5": ("f5",),
    "unit_6": ("f6",),
    "unit_7": ("f7",),
    "unit_8": ("f8",),
    "unit_9": ("f9",),
    "unit_10": ("f10",),
    "select_team_red": ("com_shift", "f1",),
    "select_team_green": ("com_shift", "f2",),
    "select_team_blue": ("com_shift", "f3",),
    "select_team_yellow": ("com_shift", "f4",),
    "select_team_white": ("com_shift", "f5",),

    "assign_team_red": ("com_ctrl", "f1",),
    "assign_team_green": ("com_ctrl", "f2",),
    "assign_team_blue": ("com_ctrl", "f3",),
    "assign_team_yellow": ("com_ctrl", "f4",),
    "assign_team_white": ("com_ctrl", "f5",),

    "menu_1": ("1",),
    "menu_2": ("2",),
    "menu_3": ("3",),
    "menu_4": ("4",),
    "menu_5": ("5",),
    "menu_6": ("6",),
    "menu_7": ("7",),
    "menu_8": ("8",),
    "menu_9": ("9",),
    "menu_10": ("0",),

    "cmd_vehicle_fire": ("com_ctrl", "mouse_left",),
    "cmd_vehicle_target": ("com_ctrl", "t",),
    "cmd_vehicle_switch_weapon": ("com_ctrl", "f",),
    "cmd_vehicle_manual_fire": ("colon",),
    "cmd_vehicle_fast": ("e",),
    "cmd_vehicle_slow": ("q",),

    "cmd_formup": ("1", "1",),
    "cmd_advance": ("1", "2",),
    "cmd_fallback": ("1", "3",),
    "cmd_flankleft": ("1", "4",),
    "cmd_flankright": ("1", "5",),
    "cmd_stop": ("1", "6",),
    "cmd_takecover": ("1", "7",),
    "cmd_notarget": ("2", "1",),
    "cmd_openfire": ("3", "1",),
    "cmd_holdfire": ("3", "2",),
    "cmd_infantryfire": ("3", "3",),
    "cmd_engage": ("3", "4",),
    "cmd_engagefree": ("3", "5",),
    "cmd_disengage": ("3", "6",),
    "cmd_scanhorizon": ("3", "7",),
    "cmd_spfire": ("3", "9",),
    "cmd_disembark": ("4", "1",),
    "cmd_injured": ("5", "4",),
    "cmd_reportstatus": ("5", "5",),
    "cmd_stealth": ("7", "1",),
    "cmd_combat": ("7", "2",),
    "cmd_aware": ("7", "3",),
    "cmd_safe": ("7", "4",),
    "cmd_standup": ("7", "6",),
    "cmd_crouch": ("7", "7",),
    "cmd_prone": ("7", "8",),
    "cmd_autostance": ("7", "9",),
    "cmd_form_column": ("8", "1",),
    "cmd_form_staggeredcol": ("8", "2",),
    "cmd_form_wedge": ("8", "3",),
    "cmd_form_echelonleft": ("8", "4",),
    "cmd_form_echelonright": ("8", "5",),
    "cmd_form_vee": ("8", "6",),
    "cmd_form_line": ("8", "7",),
    "cmd_form_file": ("8", "8",),
    "cmd_form_diamond": ("8", "9",),

    "cmd_radio_alpha": ("0", "0", "1",),
    "cmd_radio_bravo": ("0", "0", "2",),
    "cmd_radio_charlie": ("0", "0", "3",),
    "cmd_radio_delta": ("0", "0", "4",),
    "cmd_radio_echo": ("0", "0", "5",),
    "cmd_radio_foxtrot": ("0", "0", "6",),
    "cmd_radio_golf": ("0", "0", "7",),
    "cmd_radio_hotel": ("0", "0", "8",),
    "cmd_radio_india": ("0", "0", "9",),
    "cmd_radio_juliet": ("0", "0", "0",),
}

# print key bindings
print("-- Arma 3 keybindings --")
for (k, v) in ingame_key_bindings.items():
    print(f'{k}:{v}')
print("-- Arma 3 keybindings --")

# mappings of spoken phrases to values
map_all_command = {
    "none": "none",

    "いち [ばん]": "menu_1",
    "に [ばん]": "menu_2",
    "さん [ばん]": "menu_3",
    "よん [ばん]": "menu_4",
    "ご [ばん]": "menu_5",
    "ろく [ばん]": "menu_6",
    "なな [ばん]": "menu_7",
    "はち [ばん]": "menu_8",
    "きゅう [ばん]": "menu_9",
    "じゅう [ばん]": "menu_10",

    "all": "unit_all",
    "one": "unit_1",
    "two": "unit_2",
    "three": "unit_3",
    "four": "unit_4",
    "five": "unit_5",
    "six": "unit_6",
    "seven": "unit_7",
    "eight": "unit_8",
    "nine": "unit_9",
    "ten": "unit_10",
    "ぜんいん": "unit_all",
    "ぜん ちーむ": "unit_all",
    "わん": "unit_1",
    "つー": "unit_2",
    "すりー": "unit_3",
    "ふぉー": "unit_4",
    "ふぁいぶ": "unit_5",
    "しっくす": "unit_6",
    "せぶん": "unit_7",
    "えいと": "unit_8",
    "ないん": "unit_9",
    "てん": "unit_10",

    "red [team]": "select_team_red",
    "green [team]": "select_team_green",
    "blue [team]": "select_team_blue",
    "yellow [team]": "select_team_yellow",
    "white [team]": "select_team_white",
    "れっど [ちーむ]": "select_team_red",
    "ぐりーん [ちーむ]": "select_team_green",
    "ぶるー [ちーむ]": "select_team_blue",
    "いえろー [ちーむ]": "select_team_yellow",
    "ほわいと [ちーむ]": "select_team_white",

    "assign red": "assign_team_red",
    "assign green": "assign_team_green",
    "assign blue": "assign_team_blue",
    "assign yellow": "assign_team_yellow",
    "assign white": "assign_team_white",
    "れっど [ちーむ] に (へんせい | わりあて)": "assign_team_red",
    "ぐりーん [ちーむ] に (へんせい | わりあて)": "assign_team_green",
    "ぶるー [ちーむ] に (へんせい | わりあて)": "assign_team_blue",
    "いえろー [ちーむ] に (へんせい | わりあて)": "assign_team_yellow",
    "ほわいと [ちーむ] に (へんせい | わりあて)": "assign_team_white",

    "target": "cmd_vehicle_target",
    "たーげっと [(だ | せってい)]": "cmd_vehicle_target",
    "もくひょう [だ]": "cmd_vehicle_target",
    "もくひょう [に] (してい | せってい)": "cmd_vehicle_target",
    "ねらえ": "cmd_vehicle_target",
    "fire": "cmd_vehicle_fire",
    "ふぁいあ": "cmd_vehicle_fire",
    "ふぁいや": "cmd_vehicle_fire",
    "[つづけ て] うて": "cmd_vehicle_fire",
    "[つづけ て] うで": "cmd_vehicle_fire",
    "[つづけ て] うけ": "cmd_vehicle_fire",
    "[つづけ て] いて": "cmd_vehicle_fire",
    "[つづけ て] れて": "cmd_vehicle_fire",
    "[つづけ て] はっしゃ": "cmd_vehicle_fire",
    "(ぶそう | へいそう) [(きりかえ | へんこう)]": "cmd_vehicle_switch_weapon",
    "manual": "cmd_vehicle_manual_fire",
    "manual fire": "cmd_vehicle_manual_fire",
    "cancel manual fire": "cmd_vehicle_manual_fire",
    "まにゅある": "cmd_vehicle_manual_fire",
    "まにゅある ふぁいあ": "cmd_vehicle_manual_fire",
    "まにゅある ふぁいや": "cmd_vehicle_manual_fire",
    "きゃんせる まにゅある ふぁいあ": "cmd_vehicle_manual_fire",
    "きゃんせる まにゅある ふぁいや": "cmd_vehicle_manual_fire",
    "ぜんそく [りょく]": "cmd_vehicle_fast",
    "ていそく": "cmd_vehicle_slow",

    "あつま れ": "cmd_formup",
    "しゅうけつ [(しろ | せよ)]": "cmd_formup",
    "しゅうごう [(しろ | せよ)]": "cmd_formup",
    "さいへんせい [(しろ | せよ)]": "cmd_formup",
    "たいけい に もどれ": "cmd_formup",
    "ついて こい": "cmd_formup",
    "もど って こい": "cmd_formup",
    # "ぜんしん [(しろ | せよ)]": "cmd_advance", # changed to use for vehicle control but, it's your option.
    # "こうたい [(しろ | せよ)]": "cmd_fallback", # changed to use for vehicle control but, it's your option.
    "さよく に てんかい [(しろ | せよ)]": "cmd_flankleft",
    "ひだり [がわ] に てんかい [(しろ | せよ)]": "cmd_flankleft",
    "うよく に てんかい [(しろ | せよ)]": "cmd_flankright",
    "みぎ [がわ] に てんかい [(しろ | せよ)]": "cmd_flankright",
    "とまれ": "cmd_stop",
    # "ていし [しろ]": "cmd_stop", # changed to use for vehicle control but, it's your option.
    "かくれ ろ": "cmd_takecover",
    "かばー [を とれ]": "cmd_takecover",
    "もくひょう なし": "cmd_notarget",
    "うちかた はじめ": "cmd_openfire",
    "しゃげき かいし": "cmd_openfire",
    "しゃげき きょか": "cmd_openfire",
    "うちかた やめ": "cmd_holdfire",
    "しゃげき ていし": "cmd_holdfire",
    "やれ": "cmd_infantryfire",
    "こうせん [かいし]": "cmd_engage",
    "こうせん [を] きょか する": "cmd_engagefree",
    "こうせん ちゅうし": "cmd_disengage",
    "こうせん ていし": "cmd_disengage",
    "まわり を みろ": "cmd_scanhorizon",
    "せいあつしゃげき [(しろ | せよ)]": "cmd_spfire",
    "おり ろ": "cmd_disembark",
    "こうしゃ [(しろ | せよ)]": "cmd_disembark",
    "うたれた": "cmd_injured",
    "たすけ て くれ": "cmd_injured",
    "[じょうきょう] ほうこく [(しろ | せよ)]": "cmd_reportstatus",
    "すてるす": "cmd_stealth",
    "おんみつこうどう": "cmd_stealth",
    "せんとう [(たいせい | じゅんび)]": "cmd_combat",
    "けいかい [たいせい]": "cmd_aware",
    "[(せんとう | けいかい)] かいじょ": "cmd_safe",
    "やすめ": "cmd_safe",
    "たて": "cmd_standup",
    "しゃがめ": "cmd_crouch",
    "ふせろ": "cmd_prone",
    "ほふく しせい": "cmd_prone",
    "しせい [は] まかせ [る]": "cmd_autostance",
    "からむ [(たいけい | ふぉーめーしょん)]": "cmd_form_column",
    "だぶる からむ [(たいけい | ふぉーめーしょん)]": "cmd_form_staggeredcol",
    "うぇっじ [(たいけい | ふぉーめーしょん)]": "cmd_form_wedge",
    "ひだり より [(たいけい | ふぉーめーしょん)]": "cmd_form_echelonleft",
    "みぎ より [(たいけい | ふぉーめーしょん)]": "cmd_form_echelonright",
    "かくよく [(たいけい | じんけい | ふぉーめーしょん)]": "cmd_form_vee",
    "ぶいじ [(たいけい | じんけい | ふぉーめーしょん)]": "cmd_form_vee",
    "らいん [(たいけい | ふぉーめーしょん)]": "cmd_form_line",
    "おうたい [(たいけい | ふぉーめーしょん)]": "cmd_form_line",
    "いちれつ [(たいけい | じゅうたい | ふぉーめーしょん)]": "cmd_form_file",
    "(だいやもんど | だいやもんど) [(たいけい | ふぉーめーしょん)]": "cmd_form_diamond",

    "てっこう だん [そうてん]": "cmd_radio_alpha",
    "だんしゅ (てっこう | てっこう だん)": "cmd_radio_alpha",
    "じだん (てっこう | てっこう だん)": "cmd_radio_alpha",
    "(A P だん | えー ぴー だん) [そうてん]": "cmd_radio_alpha",
    "だんしゅ (A P | A P だん | えー ぴー | えー ぴー だん)": "cmd_radio_alpha",
    "じだん (A P | A P だん | えー ぴー | えー ぴー だん)": "cmd_radio_alpha",
    "(りゅうだん | りゅう だん) [そうてん]": "cmd_radio_bravo",
    "だんしゅ (りゅうだん | りゅう だん)": "cmd_radio_bravo",
    "じだん (りゅうだん | りゅう だん)": "cmd_radio_bravo",
    "(H E だん | えいち いー だん) [そうてん]": "cmd_radio_bravo",
    "だんしゅ (H E | H E だん | えいち いー | えいち いー だん)": "cmd_radio_bravo",
    "じだん (H E | H E だん | えいち いー | えいち いー だん)": "cmd_radio_bravo",

    "[つづけ て] [せんしゃ] ぜんしん [しろ | せよ | だ]": "cmd_radio_charlie",
    "[つづけ て] [せんしゃ] すすめ": "cmd_radio_charlie",
    "[つづけ て] [せんしゃ] ちょくしん [しろ | せよ | だ]": "cmd_radio_charlie",
    "[つづけ て] [せんしゃ] こうたい [しろ | せよ | だ]": "cmd_radio_delta",
    "[つづけ て] [せんしゃ] こうしん [しろ | せよ | だ]": "cmd_radio_delta",
    "[つづけ て] [せんしゃ] さがれ": "cmd_radio_delta",
    "[つづけ て] [せんしゃ] ていし [しろ | せよ | だ]": "cmd_radio_echo",
    "[つづけ て] [せんしゃ] ていしゃ [しろ | せよ | だ]": "cmd_radio_echo",
    "つづけ て [せんしゃ] とまれ": "cmd_radio_echo",
    # "[せんしゃ] とまれ": "cmd_radio_echo", # use for infantry command
    "[つづけ て] [せんしゃ] ひだりせんかい [しろ | せよ | だ]": "cmd_radio_foxtrot",
    "[つづけ て] [せんしゃ] ひだり せんかい [しろ | せよ | だ]": "cmd_radio_foxtrot",
    "[つづけ て] [せんしゃ] ひだり に (せんかい [しろ | せよ | だ] | まわれ)": "cmd_radio_foxtrot",
    "[つづけ て] [せんしゃ] みぎせんかい [しろ | せよ | だ]": "cmd_radio_golf",
    "[つづけ て] [せんしゃ] みぎ せんかい [しろ | せよ | だ]": "cmd_radio_golf",
    "[つづけ て] [せんしゃ] みぎ に (せんかい [しろ | せよ | だ] | まわれ)": "cmd_radio_golf",
}

def debug_print_key(input_key):
    print(input_key)

def convert_input_action(input_key, hold=""):
    if DEBUG_NOCMD_PRINT_ONLY:
        return Function(debug_print_key, input_key=input_key+hold)
    else:
        if "mouse_" in input_key:
            if hold == "down":
                return Mouse(f'{input_key.replace("mouse_", "")}:down/{min_delay}')
            elif hold == "up":
                return Mouse(f'{input_key.replace("mouse_", "")}:up/{min_delay}')
            else:
                return Mouse(f'{input_key.replace("mouse_", "")}:down/{min_delay}, {input_key.replace("mouse_", "")}:up/{min_delay}')
        else:
            if hold == "down":
                return Key(f'{input_key}:down/{min_delay}')
            elif hold == "up":
                return Key(f'{input_key}:up/{min_delay}')
            else:
                return Key(f'{input_key}:down/{min_delay}, {input_key}:up/{min_delay}')

# ---------------------------------------------------------------------------
# Rules which will be added to our grammar

# used to chain actions together, e.g. (NULL_ACTION + Key(...) + Mouse(...)).execute()
NULL_ACTION = Function(lambda: print("NULL_ACTION")
                       if DEBUG_NOCMD_PRINT_ONLY else None)

# ------------------------------------------------------------------

def cmd_push_key(command):
    """
    Press & release select unit(s) key
    """
    hold_keys = []
    for key in ingame_key_bindings[command]:
        if key == "none":
            continue
        if "com_" in key:
            input_key = key.replace("com_", "")
            hold_keys.append(input_key)
            if DEBUG_NOCMD_PRINT_ONLY:
                print(f"{input_key} down")
            else:
                action = convert_input_action(input_key, "down")
                action.execute()
        else:
            if DEBUG_NOCMD_PRINT_ONLY:
                print(f"{key}")
            else:
                action = convert_input_action(key)
                action.execute()
    for h_key in hold_keys:
        if DEBUG_NOCMD_PRINT_ONLY:
            print(f"{h_key} up")
        else:
            action = convert_input_action(h_key, "up")
            action.execute()

class executeCommand(CompoundRule):
    """
    Speech recognise single command
    """
    spec = "<myword>"
    extras = [
        Choice("myword", map_all_command),
    ]
    defaults = {
        "myword": "unit_all",
    }

    def _process_recognition(self, node, extras):
        command = extras["myword"]
        print(f"execute {command}")
        cmd_push_key(command)

class executeMultiCommand(CompoundRule):
    """
    Speech recognise multiple command
    """
    spec = "<myword1> <myword2> [<myword3>] [<myword4>] [<myword5>] [<myword6>] [<myword7>] [<myword8>] [<myword9>] [<myword10>] [<myword11>]"
    extras = [
        Choice("myword1", map_all_command),
        Optional(Choice("myword2_choice", map_all_command), "myword2", "none"),
        Optional(Choice("myword3_choice", map_all_command), "myword3", "none"),
        Optional(Choice("myword4_choice", map_all_command), "myword4", "none"),
        Optional(Choice("myword5_choice", map_all_command), "myword5", "none"),
        Optional(Choice("myword6_choice", map_all_command), "myword6", "none"),
        Optional(Choice("myword7_choice", map_all_command), "myword7", "none"),
        Optional(Choice("myword8_choice", map_all_command), "myword8", "none"),
        Optional(Choice("myword9_choice", map_all_command), "myword9", "none"),
        Optional(Choice("myword10_choice", map_all_command), "myword10", "none"),
        Optional(Choice("myword11_choice", map_all_command), "myword11", "none"),
    ]
    defaults = {
        "myword1": "unit_all",
        "myword2": "none",
        "myword3": "none",
        "myword4": "none",
        "myword5": "none",
        "myword6": "none",
        "myword7": "none",
        "myword8": "none",
        "myword9": "none",
        "myword10": "none",
        "myword11": "none",
    }

    def _process_recognition(self, node, extras):
        for command in (extras["myword1"], extras["myword2"], extras["myword3"], extras["myword4"], extras["myword5"], extras["myword6"], extras["myword7"], extras["myword8"], extras["myword9"], extras["myword10"], extras["myword11"], ):
            if command == "none":
                continue
            print(f"execute {command}")
            cmd_push_key(command)

# ------------------------------------------------------------------

class NoiseSink(MappingRule):
    """
    Capture any other noises or words outside of commands, and do nothing
    """
    mapping = {'<dictation>': ActionBase()}
    extras = [ Dictation("dictation") ]

# ---------------------------------------------------------------------------
# Add rules to grammar and create RecognitionObserver instances

grammar.add_rule(executeCommand())
grammar.add_rule(executeMultiCommand())

# grammar_priority.add_rule(YellFreeze())
if USE_NOISE_SINK:
    grammar_priority.add_rule(NoiseSink())

# ---------------------------------------------------------------------------
# Load the grammar instance, register RecognitionObservers, and define how
# to unload them.

grammar.load()
grammar_priority.load()

# ---------------------------------------------------------------------------
# Push to talk, mute, toggle

import keyboard, mouse

try:
    PTT_MODE = (sys.modules["user_settings"]).PTT_MODE
except Exception:
    print("Failed to get PTT_MODE, set to default mode 0 (always on)")
    PTT_MODE = 0
try:
    PTT_KEY = (sys.modules["user_settings"]).PTT_KEY
except Exception:
    PTT_KEY = None

class ListeningState(object):
    def __init__(self, init_state):
        self._state = init_state
    def get_state(self):
        return self._state
    def set_state(self, new_state):
        self._state = new_state

grammars = (grammar, grammar_priority)
label_mic_on = "Mic ON"
label_mic_off = "Mic OFF"

def setup_always_on():
    print("Mic is always ON.")

def setup_toggle_to_talk_mute(grammars, key=PTT_KEY, init_state=True):
    listening_status = ListeningState(init_state)
    def on_press(_cls, grammars):
        _new_state = not bool(_cls.get_state())
        if _new_state:
            for grm in grammars: grm.engine.activate_grammar(grm)
            print(label_mic_on)
        else:
            for grm in grammars: grm.engine.deactivate_grammar(grm)
            print(label_mic_off)
        _cls.set_state(_new_state)
    if "mouse_" in key:
        mouse.on_button(on_press, args=(listening_status, grammars), buttons=(key.replace("mouse_", ""),), types=("down",))
    else:
        keyboard.add_hotkey(keyboard.parse_hotkey(key), on_press, args=[listening_status, grammars])
    print(f"Mic mode is 'push to toggle ON/OFF' with key={key}")
    if init_state:
        print(label_mic_on)
    else:
        for grm in grammars: grm.engine.deactivate_grammar(grm)
        print(label_mic_off)

def setup_push_to_talk_mute(grammars, key=PTT_KEY, init_state=True):
    listening_status = ListeningState(init_state)
    def press_down(_cls):
        _cls = listening_status
        _is_listening = _cls.get_state()
        if init_state:
            # push to mute
            if _is_listening:
                for grm in grammars: grm.engine.deactivate_grammar(grm)
                _cls.set_state(False)
                print(label_mic_off)
        else:
            # push to talk
            if not _is_listening:
                for grm in grammars: grm.engine.activate_grammar(grm)
                _cls.set_state(True)
                print(label_mic_on)
    def press_up(_cls):
        _cls = listening_status
        if init_state:
            # push to mute
            for grm in grammars: grm.engine.activate_grammar(grm)
            _cls.set_state(True)
            print(label_mic_on)
        else:
            # push to talk
            for grm in grammars: grm.engine.deactivate_grammar(grm)
            _cls.set_state(False)
            print(label_mic_off)
    def push_to_talk_mute_kb(event):
        _key = event.name
        if keyboard.is_pressed(_key):
            press_down(listening_status)
        else:
            press_up(listening_status)
    def push_to_talk_mute_mb(event):
        if not isinstance(event, mouse.ButtonEvent): return None
        if not event.button == key.replace("mouse_", ""): return None
        if event.event_type == "down":
            press_down(listening_status)
        elif event.event_type == "up":
            press_up(listening_status)
    if "mouse_" in key:
        mouse.hook(push_to_talk_mute_mb)
    else:
        keyboard.hook_key(keyboard.parse_hotkey(key), push_to_talk_mute_kb)
    if init_state:
        print(f"Mic mode is 'push to mute' with key={key}")
        print(label_mic_on)
    else:
        for grm in grammars: grm.engine.deactivate_grammar(grm)
        print(f"Mic mode is 'push to talk' with key={key}")
        print(label_mic_off)

if PTT_MODE in (0,1,2,3,4):
    if PTT_MODE == 0:
        # always on
        setup_always_on()
    elif PTT_MODE == 1:
        # toggle, initial on
        setup_toggle_to_talk_mute(grammars, key=PTT_KEY, init_state=True)
    elif PTT_MODE == 2:
        # toggle, initial off
        setup_toggle_to_talk_mute(grammars, key=PTT_KEY, init_state=False)
    elif PTT_MODE == 3:
        # push to talk
        setup_push_to_talk_mute(grammars, key=PTT_KEY, init_state=False)
    elif PTT_MODE == 4:
        # push to mute
        setup_push_to_talk_mute(grammars, key=PTT_KEY, init_state=True)
else:
    print("Invalid PTT_MODE was given, set to default mode 0 (always on)")
    setup_always_on()

# ---------------------------------------------------------------------------
# Unload function which will be called at unload time.
def unload():
    global grammar
    global grammar_priority
    global freeze_recob
    if grammar:
        grammar.unload()
    grammar = None
    if grammar_priority:
        grammar_priority.unload()
    grammar_priority = None
    freeze_recob.unregister()
    freeze_recob = None
