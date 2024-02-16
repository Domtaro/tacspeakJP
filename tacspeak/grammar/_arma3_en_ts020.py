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
# if DEBUG_MODE:
#     print("-- Ready or Not In-Game keybindings --")
#     for (k, v) in ron_key_bindings.items():
#         print(f'{k}:{v}')
#     print("-- Ready or Not In-Game keybindings --")

# mappings of spoken phrases to values

map_all_command = {
    "none": "none",

    "first": "menu_1",
    "second": "menu_2",
    "third": "menu_3",
    "fourth": "menu_4",
    "fifth": "menu_5",
    "sixth": "menu_6",
    "seventh": "menu_7",
    "eighth": "menu_8",
    "ninth": "menu_9",
    "tenth": "menu_10",

    "all [(team | units)]": "unit_all",
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

    "red [team]": "select_team_red",
    "green [team]": "select_team_green",
    "blue [team]": "select_team_blue",
    "yellow [team]": "select_team_yellow",
    "white [team]": "select_team_white",

    "assign red": "assign_team_red",
    "assign green": "assign_team_green",
    "assign blue": "assign_team_blue",
    "assign yellow": "assign_team_yellow",
    "assign white": "assign_team_white",

    "[set] target": "cmd_vehicle_target",
    "targeting": "cmd_vehicle_target",
    "[and] fire": "cmd_vehicle_fire",
    "(change | switch) weapon": "cmd_vehicle_switch_weapon",
    "in manual": "cmd_vehicle_manual_fire",
    "manual fire": "cmd_vehicle_manual_fire",
    "cancel manual fire": "cmd_vehicle_manual_fire",
    "fast [speed]": "cmd_vehicle_fast",
    "slow [speed]": "cmd_vehicle_slow",

    "form up": "cmd_formup",
    "regroup": "cmd_formup",
    "return to formation": "cmd_formup",
     "advance": "cmd_advance",
     "fall back": "cmd_fallback",
    "flank left [side]": "cmd_flankleft",
    "flank right [side]": "cmd_flankright",
    "stop": "cmd_stop",
    "take cover": "cmd_takecover",
    "no target": "cmd_notarget",
    "open fire": "cmd_openfire",
    "hold fire": "cmd_holdfire",
    "cease fire": "cmd_holdfire",
    "shoot": "cmd_infantryfire",
    "engage": "cmd_engage",
    "free to engage": "cmd_engagefree",
    "disengage": "cmd_disengage",
    "scan horizon": "cmd_scanhorizon",
    "suppress [there]": "cmd_spfire",
    "suppressing fire": "cmd_spfire",
    "disembark": "cmd_disembark",
    "dismount": "cmd_disembark",
    "Im hit": "cmd_injured",
    "injured": "cmd_injured",
    "medic": "cmd_injured",
    "help me": "cmd_injured",
    "report [status]": "cmd_reportstatus",
    "stealth": "cmd_stealth",
    "(danger | combat)": "cmd_combat",
    "[stay] alert": "cmd_aware",
    "[stay] safe": "cmd_safe",
    "stand up": "cmd_standup",
    "[stay] crouch": "cmd_crouch",
    "[go] prone": "cmd_prone",
    "auto stance": "cmd_autostance",
    "form column": "cmd_form_column",
    "form double column": "cmd_form_staggeredcol",
    "form wedge": "cmd_form_wedge",
    "form echelon left": "cmd_form_echelonleft",
    "form echelon right": "cmd_form_echelonright",
    "form (vee | v)": "cmd_form_vee",
    "form line": "cmd_form_line",
    "form file": "cmd_form_file",
    "form diamond": "cmd_form_diamond",

    "[next] A P [round]": "cmd_radio_alpha",
    "[next] (load | round) A P": "cmd_radio_alpha",
    "[next] H E [round]": "cmd_radio_bravo",
    "[next] (load | round) H E": "cmd_radio_bravo",

    "[and] [(move | go)] (forward | front | ahead)": "cmd_radio_charlie",
    "[and] [(move | go)] (backward | back)": "cmd_radio_delta",
    "[and] halt": "cmd_radio_echo",
    "[and] turn left": "cmd_radio_foxtrot",
    "[and] [(move | go)] [turn] left [side]": "cmd_radio_foxtrot",
    "[and] turn right": "cmd_radio_golf",
    "[and] [(move | go)] [turn] right [side]": "cmd_radio_golf",
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
            action = convert_input_action(input_key, "down")
            action.execute()
        else:
            action = convert_input_action(key)
            action.execute()
    for h_key in hold_keys:
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
# grammar.add_rule(executeMultiCommand())

# grammar_priority.add_rule(YellFreeze())
if USE_NOISE_SINK:
    grammar_priority.add_rule(NoiseSink())

# ---------------------------------------------------------------------------
# Load the grammar instance, register RecognitionObservers, and define how
# to unload them.

grammar.load()
grammar_priority.load()

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
