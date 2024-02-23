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

import keyboard, mouse

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
    grammar_context = AppContext(executable="ReadyOrNot")
grammar = Grammar("ReadyOrNot",
                  context=grammar_context,
                  )
grammar_priority = Grammar("ReadyOrNot_priority",
                           context=grammar_context,
                           )

# ---------------------------------------------------------------------------
# Variables used by grammar, rules, recognition observers below
# Users should be able to look here first for customisation

# Will map keybindings to print()
DEBUG_NOCMD_PRINT_ONLY = DEBUG_MODE

# the minimum time between keys state changes (e.g. pressed then released),
# it's to make sure key presses are registered in-game
min_delay = 3.3  # 100/(30 fps) = 3.3 (/100 seconds between frames)

# map of action to in-game key bindings
# https://dragonfly.readthedocs.io/en/latest/actions.html#key-names
# https://dragonfly.readthedocs.io/en/latest/actions.html#mouse-specification-format

# map of key name RoN to Dragonfly except for case-difference only pattern
map_ron_dragonfly_keynames = {
    "None": "",
    "LeftMouseButton": "mouse_left",
    "MiddleMouseButton": "mouse_middle",
    "RightMouseButton": "mouse_right",
    "ThumbMouseButton": "mouse_four",
    "ThumbMouseButton2": "mouse_five",
    "MouseScrollUp": "mouse_wheelup",
    "MouseScrollDown": "mouse_wheeldown",
    "Zero": "0",
    "One": "1",
    "Two": "2",
    "Three": "3",
    "Four": "4",
    "Five": "5",
    "Six": "6",
    "Seven": "7",
    "Eight": "8",
    "Nine": "9",
    "Zero": "0",
    "NumPadOne": "numpad1",
    "NumPadTwo": "numpad2",
    "NumPadThree": "numpad3",
    "NumPadFour": "numpad4",
    "NumPadFive": "numpad5",
    "NumPadSix": "numpad6",
    "NumPadSeven": "numpad7",
    "NumPadEight": "numpad8",
    "NumPadNine": "numpad9",
    "Divide": "slash",
    "SpaceBar": "space",
    "LeftShift": "shift",
    "LeftControl": "ctrl",
    "LeftAlt": "alt",
    "RightShift": "rshift",
    "RightControl": "rctrl",
    "RightAlt": "ralt",
}

# map of action name Tacspeak to RoN
map_tacspeak_ron_actionnames = {
    "gold" : "SelectElementGold",
    "blue": "SelectElementBlue",
    "red": "SelectElementRed",
    "cmd_1": "SwatInputKeyOne",
    "cmd_2": "SwatInputKeyTwo",
    "cmd_3": "SwatInputKeyThree",
    "cmd_4": "SwatInputKeyFour",
    "cmd_5": "SwatInputKeyFive",
    "cmd_6": "SwatInputKeySix",
    "cmd_7": "SwatInputKeySeven",
    "cmd_8": "SwatInputKeyEight",
    "cmd_9": "SwatInputKeyNine",
    "cmd_back": "SwatInputKeyBack",
    "cmd_hold": "HoldGoCode",
    "cmd_default": "IssueDefaultCommand",
    "cmd_menu": "OpenSwatCommand",
    "interact": "UseOnly",
    "yell": "Yell",
}

# default key bindings, use when failed to set automatically
ingame_key_bindings = {
    "gold": "f5",
    "blue": "f6",
    "red": "f7",
    "alpha": "f13",
    "bravo": "f14",
    "charlie": "f15",
    "delta": "f16",
    "cmd_1": "1",
    "cmd_2": "2",
    "cmd_3": "3",
    "cmd_4": "4",
    "cmd_5": "5",
    "cmd_6": "6",
    "cmd_7": "7",
    "cmd_8": "8",
    "cmd_9": "9",
    "cmd_back": "tab",
    "cmd_hold": "shift",
    "cmd_default": "z",
    "cmd_menu": "mouse_middle",
    "interact": "f",
    "yell": "f",
}

# get list of RoN in-game key settings from ini file, and make action-keyname map
# edit the path if it's not along with your environment
inifile_name = os.path.expandvars(r"%LOCALAPPDATA%\ReadyOrNot\Saved\Config\WindowsNoEditor\Input.ini")
if os.path.isfile(inifile_name):
    with open(inifile_name, "rt", encoding="utf-8") as inifile:
        try:
            ron_key_bindings = {}
            key_setting_pattern = re.compile(r'^ActionMappings=\(ActionName="(\w+)".+Key=(\w+)')
            for inifile_line in inifile:
                match_result = re.match(key_setting_pattern, inifile_line)
                if match_result:
                    ron_action_name = match_result.group(1)
                    ron_key_name = match_result.group(2)
                    # convert specific key name to Dragonfly key names
                    if ron_key_name in map_ron_dragonfly_keynames:
                        ron_key_bindings[ron_action_name] = map_ron_dragonfly_keynames[ron_key_name]
                    else:
                        ron_key_bindings[ron_action_name] = ron_key_name.lower()

            # make ingame_key_bindings automatically
            for tacspeak_action in map_tacspeak_ron_actionnames.keys():
                ron_action = map_tacspeak_ron_actionnames[tacspeak_action]
                if ron_action in ron_key_bindings:
                    ingame_key_bindings[tacspeak_action] = copy.deepcopy(ron_key_bindings[ron_action])
                else:
                    continue

        except Exception:
            print(f"Failed to open `{inifile_name}`. Using default key-bindings")
else:
    print(f"Invalid File name `{inifile_name}` was ignored. Using default key-bindings")

# override key-bindings manually if you need
ingame_key_bindings.update({
    # "gold": "f5",
    # "blue": "f6",
    # "red": "f7",
    "alpha": "f13",
    "bravo": "f14",
    "charlie": "f15",
    "delta": "f16",
    # "cmd_1": "1",
    # "cmd_2": "2",
    # "cmd_3": "3",
    # "cmd_4": "4",
    # "cmd_5": "5",
    # "cmd_6": "6",
    # "cmd_7": "7",
    # "cmd_8": "8",
    # "cmd_9": "9",
    # "cmd_back": "tab",
    # "cmd_hold": "shift",
    # "cmd_default": "z",
    # "cmd_menu": "mouse_middle",
    # "interact": "f",
    # "yell": "f",
})

def debug_print_key(device, key):
    print(f'({device}_{key})')

if DEBUG_NOCMD_PRINT_ONLY:
    map_ingame_key_bindings = {k: Function(debug_print_key, device='m', key=v.replace("mouse_", "")) if "mouse_" in v
                               else Function(debug_print_key, device='kb', key=v)
                               for k, v in ingame_key_bindings.items()}
else:
    map_ingame_key_bindings = {k: Mouse(f'{v.replace("mouse_", "")}:down/{min_delay}, {v.replace("mouse_", "")}:up') if "mouse_" in v
                               else Key(f'{v}:down/{min_delay}, {v}:up')
                               for k, v in ingame_key_bindings.items()}

# print key bindings
print("-- Ready or Not keybindings --")
for (k, v) in map_ingame_key_bindings.items():
    print(f'{k}:{v}')
print("-- Ready or Not keybindings --")
if DEBUG_MODE:
    print("-- Ready or Not In-Game keybindings --")
    for (k, v) in ron_key_bindings.items():
        print(f'{k}:{v}')
    print("-- Ready or Not In-Game keybindings --")

# mappings of spoken phrases to values
map_hold = {
    "on my (mark | order | command)": "hold",
    "[おれ の] (あいず | あいづ) (で | したら | を まって)": "hold",
}
map_execute_or_cancels = {
    "execute": "execute", 
    "cancel": "cancel", 
    "go [go go]": "execute",
    "いけ いけ [いけ]": "execute",
    "やれ": "execute",
    "じっこう [しろ]": "execute", 
    "やめろ": "cancel",
    "きゃんせる [(だ | しろ)]": "cancel",
    "ちゅうし [(だ | しろ)]": "cancel",
}
map_colors = {
    "gold": "gold",
    "blue": "blue",
    "red": "red",
    "ごーるど": "gold",
    "ぜんいん": "gold",
    "れっど": "red",
    "ぶるー": "blue",
}
map_door_options = {
    # note: stackup, breach & clear, open & clear, scan are separate options
    "mirror [under]": "mirror",
    "wand [under]": "mirror",
    "disarm": "disarm", # todo! this inserts itself in the middle of the list and messes up other keybinds, update when Void updates
    "wedge": "wedge", # "remove the wedge" has its own recognition. can specify if door is "trapped door" to use correct keybinds.
    "block": "wedge",
    "cover": "cover", # can specify if door is "trapped door" to use correct keybinds.
    "open": "open", # can specify if door is "trapped door" to use correct keybinds.
    "close": "close", # can specify if door is "trapped door" to use correct keybinds.
    "みらー": "mirror",
    "みらーがん": "mirror",
    "わんど": "mirror",
    "おぷてぃわんど": "mirror",
    "うぇっじ": "wedge",
    "じゃまー": "wedge",
    "かばー": "cover",
    "えんご": "cover",
    "あけ ろ": "open",
    "ひらけ": "open",
    "あけ て みろ": "open",
    "ひらいて みろ": "open",
    "とじ ろ": "close",
    "しめ ろ": "close",
}
map_door_trapped = {
    "trapped": "trapped",
    "とらっぷ の": "trapped",
    "あの": "trapped",
    "その": "trapped",
}
map_door_stack_sides = { 
    # todo! in 1.0 some doors don't have all stack options available, update when Void updates
    "split": "split",
    "left": "left",
    "right": "right",
    "auto": "auto", 
    "さゆう": "split",
    "りょうがわ": "split",
    "りょう がわ": "split",
    "りょうわき": "split",
    "りょうほう": "split",
    "ひだり [がわ]": "left",
    "みぎ [がわ]": "right",
    "まかせ る": "auto",
}
map_door_breach_tools = {
    "open": "open",
    "move in": "open",
    "kick [it] [down]": "kick",
    "kick the door down": "kick",
    "(shotgun | shot e)": "shotgun",
    "c two": "c2",
    "[battering] ram [it]": "ram",
    "((leader | lead) will | wait for (my | me to)) (open | breach)": "leader",
    "あけ ろ": "open",
    "あけ て": "open",
    "ひらけ": "open",
    "ひら いて": "open",
    "はい れ": "open",
    "はいって": "open",
    "すすめ": "open",
    "とつにゅう": "open",
    "けやぶれ": "kick",
    "けやぶって": "kick",
    "しーつー": "c2",
    "ちゃーじ": "c2",
    "ばくやく": "c2",
    "はじょうつい": "ram",
    "らむ": "ram",
    "りーだー": "leader",
    "おれ [に] [(つづいて | つづけて)]": "leader",
    "[おれ が] あけ たら": "leader",
}
map_door_grenades = {
    "(bang | flash bang | flash)": "flashbang",
    "stinger": "stinger",
    "(cs | gas | cs gas)": "gas",
    "[the] (fourty mil | launcher)": "launcher",
    "((leader | lead) will | wait for (my | me to)) (grenade | flash bang | bang | flash | stinger | cs | gas | cs gas | fourty mil | launcher)": "leader",
    "(ばん | ふらっしゅ ばん | ふらっしゅ)": "flashbang",
    "せんこう [しゅりゅうだん]": "flashbang",
    "(しーえす | がす | しーえす がす)": "gas",
    "さいるい がす": "gas",
    "らんちゃー": "launcher",
    "りーだー": "leader",
    "[おれ] [(の | を)] あいず [(で | を まて)]": "leader",
    "[おれ] [(の | を)] あいづ [(で | を まて)]": "leader",
}
map_door_scan = {
    # todo! in 1.0 some doors don't have all scan options available, update when Void updates
    "scan": "pie",
    "slide": "slide",
    "pie": "pie",
    "peek": "peek",
    "すらいど": "slide",
    "すきゃん": "pie",
    "ぱい": "pie",
    "かってぃんぐぱい": "pie",
    "ぴーく": "peek",
    "のぞけ": "peek",
    "のぞ け": "peek",
}
map_ground_options = {
    # note: deploy and fall in are separate options
    "move ([over] (here | there) | [to] that (location | position))": "move",
    "cover ([over] (here | there) | that (location | position))": "cover",
    "(hold | halt | stop) [(position | movement)]": "halt",
    "resume [movement]": "resume",
    "(secure | search) [the] (area | room)": "search",
    "(search for | collect | secure) evidence": "search",
    "(そこ | あそこ) (に | へ) いけ": "move",
    # "いけ": "move", # using for default order now (but your option)
    # "[(そこ を| あそこ を)] かばー [しろ]": "cover", # using for door option now (but your option)
    "[(そこ を| あそこ を)] みて いろ": "cover",
    "[(そこ を| あそこ を)] みはって いろ": "cover",
    "[(そこ を| あそこ を)] かんし しろ": "cover",
    "とまれ": "halt",
    "とまる": "halt",
    "まて": "halt",
    "そうさく [しろ]": "search",
    "かくほ [しろ]": "search",
}
map_ground_fallin_formations = {
    "single file": "single",
    "double file": "double",
    "diamond [formation]": "diamond",
    "wedge [formation]": "wedge",
    "いちれつ": "single",
    "しんぐる": "single",
    "にれつ": "double",
    "だぶる": "double",
    "だいあもんど": "diamond",
    "だいやもんど": "diamond",
    "うぇっじ": "wedge",
    "くさびがた": "wedge",
    "くさび": "wedge",
}
map_ground_deployables = {
    "(bang | flash bang | flash)": "flashbang",
    "stinger": "stinger",
    "(cs | gas | cs gas)": "gas",
    "chem light": "chemlight",
    "shield": "shield",
    "(ばん | ふらっしゅ ばん | ふらっしゅ)": "flashbang",
    "せんこう [しゅりゅうだん]": "flashbang",
    "(しーえす | がす | しーえす がす)": "gas",
    "けみらいと": "chemlight",
    "らいと すてぃっく": "chemlight",
    "らいと": "chemlight",
    "たて": "shield",
    "しーるど": "shield",
}
map_npc_player_interacts = {
    "move [(here | there)]": "move here",
    "(move | come) to (me | my position)": "move my position",
    "come here": "move my position",
    "stop [(there | moving | movement)]": "move stop",
    "turn around": "turn around",
    "move to [the] exit": "move to exit",
    "get out of here": "move to exit",
    "(get | move) outside": "move to exit",
    "(そこ | そっち) (に | へ) うごけ": "move here",
    "(おれ の ほう | こっち) (に | へ) (こい | うごけ)": "move my position",
    # "こい": "move my position", # using for default order now (but your option)
    "[そこ で] とまれ": "move stop",
    "[そこ で] とまる": "move stop",
    "まわれ": "turn around",
    "まわる": "turn around",
    "ふりむけ": "turn around",
    "うしろ を むけ": "turn around",
    "ここ (を | から) (でろ | でる)": "move to exit",
    "(でぐち | そと) (に | へ | まで) (いけ | でろ | にげろ | はしれ)": "move to exit",
    "だっしゅつ しろ": "move to exit",
}
map_npc_team_restrain = {
    "restrain": "restrain",
    "arrest": "restrain",
    "たいほ": "restrain",
    "こうそく": "restrain",
    "しばれ": "restrain",
    "てじょう": "restrain",
}
map_npc_team_deployables = {
    "taser": "taser",
    "tase": "taser",
    "pepper spray": "pepperspray",
    "pepper ball": "pepperball",
    "bean [bag]": "beanbag",
    "melee": "melee",
    "violence": "melee",
    "てーざー": "taser",
    "てーざー がん": "taser",
    "ぺっぱー すぷれー": "pepperspray",
    "ぺっぱー ぼーる": "pepperball",
    "びーんばっぐ": "beanbag",
    "なぐれ": "melee",
    "めれー": "melee",
}
map_team_members = {
    "alpha": "alpha",
    "bravo": "bravo",
    "charlie": "charlie",
    "delta": "delta",
    "あるふぁ": "alpha",
    "ぶらぼー": "bravo",
    "ちゃーりー": "charlie",
    "でるた": "delta",
}
map_team_member_options = {
    "move": "move",
    "(focus | watch)": "focus",
    "(un | release) (focus | watch)" : "unfocus",
    "stop (focusing | watching)" : "unfocus",
    "swap with": "swap",
    "(search | secure) [the] (room | area)": "search",
    "うごけ": "move",
    "みろ": "focus",
    "みるな" : "unfocus",
    "かわれ": "swap",
    "そうさく [しろ]": "search",
    "かくほ [しろ]": "search",
}
map_team_member_move = {
    "([over] (here | there) | [to] that (location | position))": "here",
    "[over] ((here | there) | [to] that (location | position)) then back": "here then back",
    "(そこ | ここ | あそこ) (に | へ) いけ": "here",
    "(そこ | ここ | あそこ) (に | へ) いって もどれ": "here then back",
}
map_team_member_focus = {
    "([over] (here | there) | [on] that (location | position))": "here",
    "([on] my position | on me)": "my position",
    "[on] [(the | that)] door [way]": "door",
    "[on] (em | them | him | her | [the] target)": "target",
    "(un focus | release)": "unfocus",
    "ここ [(を | だ)]": "here",
    "おれ [を]": "my position",
    "どあ [を]": "door",
    "もくひょう [を]": "target",
    "みるな": "unfocus",}

def invert_squash_map(my_map):
    """
    Returns an inverted map, where keys are the original values, 
    and values are the concatenation of the original keys as 
    alternative choices. For example:
        {'a':1,'b':1,'c':1} => {1: '(a | b | c)'}
    """
    inv_map = {}
    for k, v in my_map.items():
        inv_map[v] = inv_map.get(v, []) + [k]
    for k, v in inv_map.items():
        inv_map[k] = '(' + ' | '.join('(' + v + ')') + ')' if len(v) > 1 else ''.join(v)
    return inv_map

# ---------------------------------------------------------------------------
# Rules which will be added to our grammar

# used to chain actions together, e.g. (NULL_ACTION + Key(...) + Mouse(...)).execute()
NULL_ACTION = Function(lambda: print("NULL_ACTION")
                       if DEBUG_NOCMD_PRINT_ONLY else None)

def action_hold(direction):
    """
    press "down" or release "up" the hold command key (on execution)
    - direction="up"|"down"
    """
    if DEBUG_NOCMD_PRINT_ONLY:
        device = 'm' if 'mouse_' in ingame_key_bindings["cmd_hold"] else 'kb'
        return Function(debug_print_key, device=device, key=f'{ingame_key_bindings["cmd_hold"]}:{direction}')
    else:
        return Key(f'{ingame_key_bindings["cmd_hold"]}:{direction}')

# ------------------------------------------------------------------

def cmd_execute_or_cancel_held_order(color, execute_or_cancel):
    """
    Press & release command keys for team to execute held order
    """
    actions = cmd_select_team(color)
    actions += map_ingame_key_bindings["cmd_menu"]
    match execute_or_cancel:
        case "execute":
            actions += map_ingame_key_bindings["cmd_1"]
        case "cancel":
            actions += map_ingame_key_bindings["cmd_2"]
    return actions

class ExecuteOrCancelHeldOrder(CompoundRule):
    """
    Speech recognise team execute or cancel a held order
    """
    # spec = "<color> [team] <execute_or_cancel> [([that] [held] order | that [order])]"
    spec = "<color> [ちーむ] <execute_or_cancel>"
    extras = [
        Optional(Choice("color_choice", map_colors), "color", "current"),
        Choice("execute_or_cancel", map_execute_or_cancels),
    ]
    defaults = {
        "color": "current",
        "execute_or_cancel": "execute",
    }

    def _process_recognition(self, node, extras):
        color = extras["color"]
        execute_or_cancel = extras["execute_or_cancel"]
        print(f"{color} team {execute_or_cancel} held order")
        cmd_execute_or_cancel_held_order(color, execute_or_cancel).execute()

# ------------------------------------------------------------------

def cmd_select_team(color):
    """
    Press & release select color team key (on execution), or return NULL_ACTION
    """
    if color != "current":
        return map_ingame_key_bindings[color]
    else:
        return NULL_ACTION

class SelectTeam(CompoundRule):
    """
    Speech recognise select color team
    """
    # spec = "<color> team"
    spec = "<color> ちーむ"
    extras = [Optional(Choice("color_choice", map_colors), "color", "current")]
    defaults = {"color": "current"}

    def _process_recognition(self, node, extras):
        color = extras["color"]
        print(f"Select {color}")
        cmd_select_team(color).execute()

class SelectColor(CompoundRule):
    """
    Speech recognise select color team
    """
    spec = "<color>"
    extras = [Choice("color", ["blue", "red", "gold"])]

    def _process_recognition(self, node, extras):
        color = extras["color"]
        print(f"Select {color}")
        cmd_select_team(color).execute()

# ------------------------------------------------------------------

def cmd_default_action(color, hold):
    """
    Press & release command keys for team to do default action (on execution)
    """
    actions = cmd_select_team(color)
    actions += map_ingame_key_bindings["cmd_menu"]
    # start hold for command
    if hold == "hold":
        actions += action_hold("down")
    actions += map_ingame_key_bindings["cmd_default"]
    # end hold for command
    if hold == "hold":
        actions += action_hold("up")
    return actions

class ExecuteDefault(CompoundRule):
    """
    Speech recognise default order
    """
    # spec = "<color> [ちーむ] <hold> (でふぉると | おい | あれ だ | それ だ | これ だ | たいおう しろ)"
    spec_start = "<color> [ちーむ] <hold> "
    spec1 = "(でふぉると | おい | たいおう | いけ | こい)"
    spec2 = "(あれ | それ | これ) [(だ | を | が)]"
    spec_end = "(しろ | や れ)"
    spec = f"{spec_start} ({spec1} | {spec2}) [{spec_end}]"
    extras = [
        Optional(Choice("color_choice", map_colors), "color", "current"),
        Optional(Choice("hold_choice", map_hold), "hold", "go"),
    ]
    defaults = {
        "color": "current",
        "hold": "go",
    }

    def _process_recognition(self, node, extras):
        color = extras["color"]
        hold = extras["hold"]
        print(f"{color} team {hold} execute default order")
        cmd_default_action(color, hold).execute()

# ------------------------------------------------------------------

def cmd_door_options(color, hold, door_option, trapped):
    """
    Press & release command keys for team to mirror under, wedge, cover, open, 
    # close the door (on execution)
    """
    actions = cmd_select_team(color)
    actions += map_ingame_key_bindings["cmd_menu"]
    # start hold for command
    if hold == "hold":
        actions += action_hold("down")
    match door_option:
        case "slide":
            actions += map_ingame_key_bindings["cmd_4"]
            actions += map_ingame_key_bindings["cmd_1"]
        case "pie":
            actions += map_ingame_key_bindings["cmd_4"]
            actions += map_ingame_key_bindings["cmd_2"]
        case "peek":
            actions += map_ingame_key_bindings["cmd_4"]
            actions += map_ingame_key_bindings["cmd_3"]
        case "mirror":
            actions += map_ingame_key_bindings["cmd_5"]
        case "disarm":
            actions += map_ingame_key_bindings["cmd_6"]
        case "wedge":
            if trapped == "trapped":
                actions += map_ingame_key_bindings["cmd_7"]
            else:
                actions += map_ingame_key_bindings["cmd_6"]
        case "cover":
            if trapped == "trapped":
                actions += map_ingame_key_bindings["cmd_8"]
            else:
                actions += map_ingame_key_bindings["cmd_7"]
        case "open":
            if trapped == "trapped":
                actions += map_ingame_key_bindings["cmd_9"]
            else:
                actions += map_ingame_key_bindings["cmd_8"]
        case "close":
            if trapped == "trapped":
                actions += map_ingame_key_bindings["cmd_9"]
            else:
                actions += map_ingame_key_bindings["cmd_8"]
    # end hold for command
    if hold == "hold":
        actions += action_hold("up")
    return actions

class DoorOptions(CompoundRule):
    """
    Speech recognise team mirror under, wedge, cover, open, close the door
    """
    # spec = "<color> [team] <hold> <door_option> [(the | that)] <trapped> (door [way] | opening | room)"
    spec = "<color> [ちーむ] <hold> <trapped> [(どあ | つうろ| へや | そこ)] [(に | を)] <door_option> [(を つかえ | しろ)]"
    extras = [
        Optional(Choice("color_choice", map_colors), "color", "current"),
        Optional(Choice("hold_choice", map_hold), "hold", "go"),
        Choice("door_option", map_door_options | map_door_scan),
        Optional(Choice("trapped_choice", map_door_trapped), "trapped", "not trapped"),
    ]
    defaults = {
        "color": "current",
        "hold": "go",
        "door_option": "open",
        "trapped": "not trapped",
    }

    def _process_recognition(self, node, extras):
        color = extras["color"]
        hold = extras["hold"]
        door_option = extras["door_option"]
        trapped = extras["trapped"]
        print(f"{color} team {hold} {door_option} {trapped} the door")
        cmd_door_options(color, hold, door_option, trapped).execute()

class WedgeIt(CompoundRule):
    """
    Speech recognise team wedge it
    """
    # spec = "<color> [team] <hold> (wedge | block) it [(the | that)] <trapped> [door] [way]"
    spec = "<color> [ちーむ] <hold> <trapped> [(どあ | つうろ)] [(を | の | に)] (うぇっじ | じゃまー | へいさ | ふうさ | ふさげ | ぶろっく) [(しろ | を つかえ)]"
    extras = [
        Optional(Choice("color_choice", map_colors), "color", "current"),
        Optional(Choice("hold_choice", map_hold), "hold", "go"),
        Optional(Choice("trapped_choice", map_door_trapped), "trapped", "not trapped"),
    ]
    defaults = {
        "color": "current",
        "hold": "go",
        "trapped": "not trapped",
    }

    def _process_recognition(self, node, extras):
        color = extras["color"]
        hold = extras["hold"]
        trapped = extras["trapped"]
        print(f"{color} team {hold} wedge the {trapped} door")
        cmd_door_options(color, hold, "wedge", trapped).execute()

class RemoveTheWedge(CompoundRule):
    """
    Speech recognise team remove the wedge
    """
    # spec = "<color> [team] <hold> remove [the] (wedge | block) [from] [(the | that)] <trapped> [door] [way]"
    spec = "<color> [ちーむ] <hold> <trapped> [(どあ | つうろ)] [の] (うぇっじ | じゃまー | ブロック) [を] (はずせ | かいじょ しろ)"
    extras = [
        Optional(Choice("color_choice", map_colors), "color", "current"),
        Optional(Choice("hold_choice", map_hold), "hold", "go"),
        Optional(Choice("trapped_choice", map_door_trapped), "trapped", "not trapped"),
    ]
    defaults = {
        "color": "current",
        "hold": "go",
        "trapped": "not trapped",
    }

    def _process_recognition(self, node, extras):
        color = extras["color"]
        hold = extras["hold"]
        trapped = extras["trapped"]
        print(f"{color} team {hold} remove the wedge from the {trapped} door")
        cmd_door_options(color, hold, "wedge", trapped).execute()

class UseTheWand(CompoundRule):
    """
    Speech recognise team use the wand
    """
    # spec = "<color> [team] <hold> use the (mirror | wand) [on] [(the | that)] <trapped> [(door [way] | opening | room)]"
    spec = "<color> [ちーむ] <hold> <trapped> [(どあ | つうろ | へや)] [(に | を)] (みらー | みらーがん | わんど | おぷてぃわんど) (を つかえ | しろ)"
    extras = [
        Optional(Choice("color_choice", map_colors), "color", "current"),
        Optional(Choice("hold_choice", map_hold), "hold", "go"),
        Optional(Choice("trapped_choice", map_door_trapped), "trapped", "not trapped"),
    ]
    defaults = {
        "color": "current",
        "hold": "go",
        "trapped": "not trapped",
    }

    def _process_recognition(self, node, extras):
        color = extras["color"]
        hold = extras["hold"]
        trapped = extras["trapped"]
        print(f"{color} team {hold} use the wand on the {trapped} door")
        cmd_door_options(color, hold, "mirror", trapped).execute()

# ------------------------------------------------------------------

def cmd_stack_up(color, hold, side):
    """
    Press & release command keys for team to stack up (on execution)
    """
    actions = cmd_select_team(color)
    actions += map_ingame_key_bindings["cmd_menu"]
    actions += map_ingame_key_bindings["cmd_1"]
    # start hold for command
    if hold == "hold":
        actions += action_hold("down")
    # todo! in 1.0 some doors don't have all stack options available, update if/when Void update
    match side: 
        case "split":
            actions += map_ingame_key_bindings["cmd_1"]
        case "left":
            actions += map_ingame_key_bindings["cmd_2"]
        case "right":
            actions += map_ingame_key_bindings["cmd_3"]
        case "auto":
            actions += map_ingame_key_bindings["cmd_4"]
    # end hold for command
    if hold == "hold":
        actions += action_hold("up")
    return actions

class StackUp(CompoundRule):
    """
    Speech recognise team stack up on door
    """
    # spec_start = "<color> [team] <hold>"
    # spec_1 = "stack <side>"
    # spec_2 = "stack [up] [<side>]"
    # spec_3 = "<side> stack"
    # spec_end = "[(on (the | that) door [way] | there | here)]"
    # spec = f"{spec_start} ({spec_1} | {spec_2} | {spec_3}) {spec_end}"
    spec_start = "<color> [ちーむ] <hold>"
    spec_1 = "<side> [(に | へ) つけ]"
    spec_2 = "<side> [(に | へ)] (てんかい | はいち | すたっく) [しろ]"
    spec_3 = "(てんかい | はいち | いち | すたっく [あっぷ]) [しろ | に つけ]"
    spec = f"{spec_start} ({spec_1} | {spec_2} | {spec_3})"
    extras = [
        Optional(Choice("color_choice", map_colors), "color", "current"),
        Optional(Choice("hold_choice", map_hold), "hold", "go"),
        Choice("side", map_door_stack_sides),
    ]
    defaults = {
        "color": "current",
        "hold": "go",
        # todo! in 1.0 some doors don't have all stack options available, change to "auto" if/when Void update
        # keeping as "split" for now because it's cmd_1 and don't want to swap off primary weapon if stack options 
        # aren't available
        # "side": "split", 
        "side": "auto",
    }

    def _process_recognition(self, node, extras):
        color = extras["color"]
        hold = extras["hold"]
        side = extras["side"]
        print(f"{color} team {hold} stack up {side}")
        cmd_stack_up(color, hold, side).execute()

# ------------------------------------------------------------------

def cmd_breach_and_clear(color, hold, tool, grenade):
    """
    Press & release command keys for team to breach & clear (on execution)
    """
    actions = cmd_select_team(color)
    actions += map_ingame_key_bindings["cmd_menu"]
    if tool == "open":
        actions += map_ingame_key_bindings["cmd_2"]
    else:
        actions += map_ingame_key_bindings["cmd_3"]
        match tool:
            case "kick":
                actions += map_ingame_key_bindings["cmd_1"]
            case "shotgun":
                actions += map_ingame_key_bindings["cmd_2"]
            case "c2":
                actions += map_ingame_key_bindings["cmd_3"]
            case "ram":
                actions += map_ingame_key_bindings["cmd_4"]
            case "leader":
                actions += map_ingame_key_bindings["cmd_5"]
    # start hold for command
    if hold == "hold":
        actions += action_hold("down")
    match grenade:
        case "none":
            actions += map_ingame_key_bindings["cmd_1"]
        case "flashbang":
            actions += map_ingame_key_bindings["cmd_2"]
        case "stinger":
            actions += map_ingame_key_bindings["cmd_3"]
        case "gas":
            actions += map_ingame_key_bindings["cmd_4"]
        case "launcher":
            actions += map_ingame_key_bindings["cmd_5"]
        case "leader":
            actions += map_ingame_key_bindings["cmd_6"]
    # end hold for command
    if hold == "hold":
        actions += action_hold("up")
    return actions

class BreachAndClear(CompoundRule):
    """
    Speech recognise team breach and clear
    """

    # "blue team on my command wait for my breach then clear it use flashbangs"
    # "red on my order c2 the door use the fourty mil then breach and clear"
    # "red team kick down the door breach and clear use cs"
    # "gold open the door use flashbangs breach and clear"
    # "blue flash and clear it"
    # "red flash and clear"
    # "kick it down clear it"
    # "gold on my command c2 the door wait for my flash then breach and clear"
    # "gold on my command shotgun the door lead will gas then clear it"
    # "gold breach and clear use the fourty mil"
    # "blue move in and clear it"

    # spec_start = "<color> [team] <hold>"
    # spec_tool = "[<tool>] [the door]"
    # spec_grenade = "[(throw | deploy | use)] <grenade> [grenade]"
    # spec_clear = "([then] breach and clear | (then | and) clear | [(then | and)] clear it | [then] move in and clear [it])"
    spec_start = "<color> [ちーむ] <hold>"
    spec_tool = "[<tool>] [(を | で)] [(つか え | つかって | やぶ れ | やぶって | あけ て | あけ ろ | とっぱ しろ | とっぱ して | して)]"
    spec_grenade = "<grenade> [(を | で)] [(つかって | なげ て | てんかい して)]"
    spec_clear = "[そして] (とっぱ して くりあ | くりあ | くりあ りんぐ | せいあつ | とつにゅう | しんにゅう) [(しろ | だ)]"

    spec = f"{spec_start} {spec_tool} ({spec_grenade} {spec_clear} | {spec_clear} {spec_grenade} | {spec_clear})"
    extras = [
        Optional(Choice("color_choice", map_colors), "color", "current"),
        Optional(Choice("hold_choice", map_hold), "hold", "go"),
        Choice("tool", map_door_breach_tools),
        Optional(Choice("grenade_choice", map_door_grenades), "grenade", "none"),
    ]
    defaults = {
        "color": "current",
        "hold": "go",
        "tool": "open",
        "grenade": "none",
    }

    def _process_recognition(self, node, extras):
        color = extras["color"]
        hold = extras["hold"]
        tool = extras["tool"]
        grenade = extras["grenade"]
        print(f"{color} team {hold} {tool} the door {grenade} breach and clear")
        cmd_breach_and_clear(color, hold, tool, grenade).execute()

# ------------------------------------------------------------------

def cmd_pick_lock(color, hold):
    """
    Press & release command keys for the team to move to location
    - assumes player is looking at door
    """
    actions = cmd_select_team(color)
    actions += map_ingame_key_bindings["cmd_menu"]
    # start hold for command
    if hold == "hold":
        actions += action_hold("down")
    # todo! check in 1.0
    actions += map_ingame_key_bindings["cmd_2"]
    # end hold for command
    if hold == "hold":
        actions += action_hold("up")
    return actions

class PickLock(CompoundRule):
    """
    Speech recognise team pick the lock
    """
    # spec = "<color> [team] <hold> pick ([the] door | [the] lock | it)"
    spec = "<color> [ちーむ] <hold> [(どあ | かぎ) を] (ぴっきんぐ | ぴっく | かいじょう) [(しろ | だ)]"
    extras = [
        Optional(Choice("color_choice", map_colors), "color", "current"),
        Optional(Choice("hold_choice", map_hold), "hold", "go"),
    ]
    defaults = {
        "color": "current",
        "hold": "go",
    }

    def _process_recognition(self, node, extras):
        color = extras["color"]
        hold = extras["hold"]
        print(f"{color} team {hold} pick the lock")
        cmd_pick_lock(color, hold).execute()

# ------------------------------------------------------------------

def cmd_ground_options(color, hold, ground_option):
    """
    Press & release command keys for the team to move, cover, halt (hold), search area
    - assumes player is not looking at person or door
    """
    actions = cmd_select_team(color)
    actions += map_ingame_key_bindings["cmd_menu"]
    # start hold for command
    if hold == "hold":
        actions += action_hold("down")
    match ground_option:
        case "move":
            actions += map_ingame_key_bindings["cmd_1"]
        case "cover":
            actions += map_ingame_key_bindings["cmd_3"]
        case "halt":
            actions += map_ingame_key_bindings["cmd_4"]
        case "resume":
            actions += map_ingame_key_bindings["cmd_4"]
        case "search":
            actions += map_ingame_key_bindings["cmd_6"]
    # end hold for command
    if hold == "hold":
        actions += action_hold("up")
    return actions

class GroundOptions(CompoundRule):
    """
    Speech recognise team move, cover, halt (hold), search area
    """
    # spec = "<color> [team] <hold> <ground_option>"
    spec = "<color> [ちーむ] <hold> <ground_option>"
    extras = [
        Optional(Choice("color_choice", map_colors), "color", "current"),
        Optional(Choice("hold_choice", map_hold), "hold", "go"),
        Choice("ground_option", map_ground_options),
    ]
    defaults = {
        "color": "current",
        "hold": "go",
        "ground_option": "move"
    }

    def _process_recognition(self, node, extras):
        color = extras["color"]
        hold = extras["hold"]
        ground_option = extras["ground_option"]
        print(f"{color} team {hold} {ground_option}")
        cmd_ground_options(color, hold, ground_option).execute()

# ------------------------------------------------------------------

def cmd_fallin(color, hold, formation):
    """
    Press & release command keys for team to fall in (on execution) 
    - assumes player is not looking at person or door
    """
    actions = cmd_select_team(color)
    actions += map_ingame_key_bindings["cmd_menu"]
    # start hold for command
    if hold == "hold":
        actions += action_hold("down")
    actions += map_ingame_key_bindings["cmd_2"]
    match formation:
        case "single":
            actions += map_ingame_key_bindings["cmd_1"]
        case "double":
            actions += map_ingame_key_bindings["cmd_2"]
        case "diamond":
            actions += map_ingame_key_bindings["cmd_3"]
        case "wedge":
            actions += map_ingame_key_bindings["cmd_4"]
    # end hold for command
    if hold == "hold":
        actions += action_hold("up")
    return actions

class FallIn(CompoundRule):
    """
    Speech recognise team fall in
    """
    # spec_1 = "<color> [team] <hold> (fall in | regroup | form up) [on me] [<formation>]"
    # spec_2 = "<color> [team] <hold> on me [<formation>]"
    # spec = f"({spec_1} | {spec_2})"
    spec_1 = "<color> [ちーむ] <hold> [<formation> [(たいけい | ふぉーめーしょん | ふぉーむ)] [(に | だ | で)]] (さいへんせい | しゅうけつ | さいしゅうけつ | しゅうごう) [しろ]"
    spec_2 = "<color> [ちーむ] <hold> [<formation> [(たいけい | ふぉーめーしょん | ふぉーむ)] [(に | だ | で)]] (あつま れ | あつま る | もど れ | もど る | もどって こい | ついて こい)"
    spec_3 = "<color> [ちーむ] <hold> [<formation> [(たいけい | ふぉーめーしょん | ふぉーむ)] [(に | だ | で)]] (うしろ | あと) に (つけ | つづけ | こい)"
    spec = f"({spec_1} | {spec_2} | {spec_3})"
    extras = [
        Optional(Choice("color_choice", map_colors), "color", "current"),
        Optional(Choice("hold_choice", map_hold), "hold", "go"),
        Choice("formation", map_ground_fallin_formations),
    ]
    defaults = {
        "color": "current",
        "hold": "go",
        "formation": "single",
    }

    def _process_recognition(self, node, extras):
        color = extras["color"]
        hold = extras["hold"]
        formation = extras["formation"]
        print(f"{color} team {hold} fall in {formation}")
        cmd_fallin(color, hold, formation).execute()

# ------------------------------------------------------------------

def cmd_use_deployable(color, hold, deployable):
    """
    Press & release command keys for the team to use deployable (on execution) 
    - assumes player is not looking at person or door
    """
    actions = cmd_select_team(color)
    actions += map_ingame_key_bindings["cmd_menu"]
    actions += map_ingame_key_bindings["cmd_5"]
    # start hold for command
    if hold == "hold":
        actions += action_hold("down")
    match deployable:
        case "flashbang":
            actions += map_ingame_key_bindings["cmd_1"]
        case "stinger":
            actions += map_ingame_key_bindings["cmd_2"]
        case "gas":
            actions += map_ingame_key_bindings["cmd_3"]
        case "chemlight":
            actions += map_ingame_key_bindings["cmd_4"]
        case "shield":
            actions += map_ingame_key_bindings["cmd_5"]
    # end hold for command
    if hold == "hold":
        actions += action_hold("up")
    return actions

class UseDeployable(CompoundRule):
    """
    Speech recognise command team to use a deployable at a location
    """
    # spec = "<color> [team] <hold> deploy <deployable>"
    spec = "<color> [ちーむ] <hold> <deployable> [を] (つかえ | てんかい [しろ] | おとせ | しまえ)"
    extras = [
        Optional(Choice("color_choice", map_colors), "color", "current"),
        Optional(Choice("hold_choice", map_hold), "hold", "go"),
        Choice("deployable", map_ground_deployables),
    ]
    defaults = {
        "color": "current",
        "hold": "go",
        "deployable": "flashbang",
    }

    def _process_recognition(self, node, extras):
        color = extras["color"]
        hold = extras["hold"]
        deployable = extras["deployable"]
        print(f"{color} team {hold} deploy {deployable}")
        cmd_use_deployable(color, hold, deployable).execute()

# ------------------------------------------------------------------

def cmd_npc_player_interact(interaction):
    """
    Press & release command keys for player to interact with target (on execution) 
    - assumes player is looking at person
    """
    actions = map_ingame_key_bindings["cmd_menu"]
    match interaction:
        case "move here":
            actions += map_ingame_key_bindings["cmd_2"]
        case "move my position":
            actions += map_ingame_key_bindings["cmd_2"]
            actions += map_ingame_key_bindings["cmd_2"]
        case "move stop":
            actions += map_ingame_key_bindings["cmd_2"]
            actions += map_ingame_key_bindings["cmd_3"]
        case "turn around":
            actions += map_ingame_key_bindings["cmd_4"]
        case "move to exit":
            actions += map_ingame_key_bindings["cmd_5"]
    return actions

class NpcPlayerInteract(CompoundRule):
    """
    Speech recognise command an NPC (not team)
    """
    # spec = "you <interaction>"
    spec = "[(おまえ | きみ | あんた | そこ で)] <interaction>"
    extras = [
        Choice("interaction", map_npc_player_interacts),
    ]

    def _process_recognition(self, node, extras):
        interaction = extras["interaction"]
        print(f"player to NPC {interaction}")
        cmd_npc_player_interact(interaction).execute()

# ------------------------------------------------------------------

def cmd_npc_team_restrain(color):
    """
    Press & release command keys for team to restrain NPC target (on execution) 
    - assumes player is looking at person
    """
    actions = cmd_select_team(color)
    actions += map_ingame_key_bindings["cmd_menu"]
    actions += map_ingame_key_bindings["cmd_1"]
    return actions

class NpcTeamRestrain(CompoundRule):
    """
    Speech recognise command team to restrain NPC target
    """
    # spec_start = "<color> [team]"
    # spec_1 = "<restrain> (em | them | him | her | [the] target)"
    # spec_2 = "<restrain>"
    spec_start = "<color> [ちーむ]"
    spec_1 = "(かれ | かのじょ | やつ | あいつ | もくひょう) [(を | に)] <restrain> [(しろ | だ | を かけろ)]"
    spec_2 = "<restrain> [(しろ | だ | を かけろ)]"
    spec = f"{spec_start} ({spec_1} | {spec_2})"
    extras = [
        Optional(Choice("color_choice", map_colors), "color", "current"),
        Choice("restrain", map_npc_team_restrain),
    ]
    defaults = {
        "color": "current",
        "restrain": "restrain",
    }

    def _process_recognition(self, node, extras):
        color = extras["color"]
        print(f"{color} team restrain target")
        cmd_npc_team_restrain(color).execute()

# ------------------------------------------------------------------

def cmd_npc_team_deploy(color, deployable):
    """
    Press & release command keys for team to use deployable on NPC target (on execution) 
    - assumes player is looking at person
    """
    actions = cmd_select_team(color)
    actions += map_ingame_key_bindings["cmd_menu"]
    actions += map_ingame_key_bindings["cmd_3"]
    match deployable:
        case "taser":
            actions += map_ingame_key_bindings["cmd_1"]
        case "pepperspray":
            actions += map_ingame_key_bindings["cmd_2"]
        case "pepperball":
            actions += map_ingame_key_bindings["cmd_3"]
        case "beanbag":
            actions += map_ingame_key_bindings["cmd_4"]
        case "melee":
            actions += map_ingame_key_bindings["cmd_5"]
    return actions

class NpcTeamDeploy(CompoundRule):
    """
    Speech recognise command team to use deployable on NPC target
    """
    # spec_start = "<color> [team]"
    # spec_target = "(em | them | him | her | [the] target)"
    # spec_1 = f"subdue {spec_target} [(use | with)] [<deployable>]"
    # spec_2 = f"<deployable> {spec_target}"
    # spec_3 = f"make {spec_target} compliant [(use | with)] [<deployable>]"
    # spec = f"{spec_start} ({spec_1} | {spec_2} | {spec_3})"
    spec_start = "<color> [ちーむ]"
    spec_target = "(かれ | かのじょ | やつ | あいつ | こいつ | もくひょう)"
    spec_1 = f"{spec_target} (に | を) <deployable> [を つかえ]"
    spec_2 = f"<deployable> [を] {spec_target} [に] [つかえ]"
    spec = f"{spec_start} ({spec_1} | {spec_2})"
    extras = [
        Optional(Choice("color_choice", map_colors), "color", "current"),
        Choice("deployable", map_npc_team_deployables),
    ]
    defaults = {
        "color": "current",
        "deployable": "melee",
    }

    def _process_recognition(self, node, extras):
        color = extras["color"]
        deployable = extras["deployable"]
        print(f"{color} team {deployable} target")
        cmd_npc_team_deploy(color, deployable).execute()

# ------------------------------------------------------------------

def cmd_select_team_member(team_member):
    """
    Press & release select team member key (on execution)
    """
    return map_ingame_key_bindings[team_member]

class SelectTeamMember(CompoundRule):
    """
    Speech recognise commands to individual team member
    """
    spec = "<team_member>"
    extras=[
        Choice("team_member", map_team_members),
    ]

    def _process_recognition(self, node, extras):
        team_member = extras["team_member"]
        print(f"Select {team_member}")
        cmd_select_team_member(team_member).execute()

# ------------------------------------------------------------------

def cmd_team_member_options(team_member, option, additional_option):
    """
    Press & release command keys for interacting with individual team member (on execution) 
    """
    actions = map_ingame_key_bindings[team_member]
    actions += map_ingame_key_bindings["cmd_menu"]
    match option:
        case "move":
            actions += map_ingame_key_bindings["cmd_1"]
            match additional_option:
                case "here":
                    actions += map_ingame_key_bindings["cmd_1"]
                case "here then back":
                    actions += map_ingame_key_bindings["cmd_2"]
        case "focus":
            actions += map_ingame_key_bindings["cmd_2"]
            match additional_option:
                case "here":
                    actions += map_ingame_key_bindings["cmd_1"]
                case "my position":
                    actions += map_ingame_key_bindings["cmd_2"]
                case "door":
                    actions += map_ingame_key_bindings["cmd_3"]
                case "target":
                    actions += map_ingame_key_bindings["cmd_4"]
                case "unfocus":
                    actions += map_ingame_key_bindings["cmd_5"]
        case "unfocus":
            actions += map_ingame_key_bindings["cmd_2"]
            actions += map_ingame_key_bindings["cmd_5"]
        case "swap":
            actions += map_ingame_key_bindings["cmd_3"]
            match additional_option:
                case "alpha":
                    actions += map_ingame_key_bindings["cmd_1"]
                case "bravo":
                    actions += map_ingame_key_bindings["cmd_2"]
                case "charlie":
                    actions += map_ingame_key_bindings["cmd_3"]
                case "delta":
                    actions += map_ingame_key_bindings["cmd_4"]
        case "search":
            actions += map_ingame_key_bindings["cmd_4"]
    return actions

class TeamMemberOptions(CompoundRule):
    """
    Speech recognise commands to individual team member
    """
    spec = "<team_member> <option> [(<move_option> | <focus_option> | <other_team_member>)]"
    extras=[
        Choice("team_member", map_team_members),
        Choice("option", map_team_member_options),
        Choice("move_option", map_team_member_move),
        Choice("focus_option", map_team_member_focus),
        Choice("other_team_member", map_team_members),
    ]

    def _process_recognition(self, node, extras):
        team_member = extras["team_member"]
        option = extras["option"]
        move_option = extras.get("move_option")
        focus_option = extras.get("focus_option")
        other_team_member = extras.get("other_team_member")
        additional_option = ((move_option if move_option is not None else "") 
            + (focus_option if focus_option is not None else "")
            + (other_team_member if other_team_member is not None else ""))
        print(f"{team_member} {option} {additional_option}")
        cmd_team_member_options(team_member, option, additional_option).execute()

# ------------------------------------------------------------------

def cmd_yell():
    """
    Press & release yell key (on execution)
    """
    return map_ingame_key_bindings["yell"]

class YellFreeze(BasicRule):
    """
    Speech recognise yell at NPC
    """
    element = Alternative((
        Literal("freeze"),
        Literal("hands"),
        Literal("drop"),
        Literal("drop it"),
        Literal("police"),
        Literal("うごくな"),
        Literal("けいさつだ"),
        Literal("えるえすぴーでぃー だ"),
        Literal("ぶきをすてろ"),
        Literal("てをあげろ"),
        Literal("ひざをつけ"),
        Literal("ひざまずけ"),
        Literal("ふせろ"),
    ))

    def _process_recognition(self, node, extras):
        print("Freeze!")
        cmd_yell().execute()

# ------------------------------------------------------------------

class NoiseSink(MappingRule):
    """
    Capture any other noises or words outside of commands, and do nothing
    """
    mapping = {'<dictation>': ActionBase()}
    extras = [ Dictation("dictation") ]

# ---------------------------------------------------------------------------
# Add rules to grammar and create RecognitionObserver instances

grammar.add_rule(ExecuteOrCancelHeldOrder())
grammar.add_rule(SelectTeam())
grammar.add_rule(SelectColor())
grammar.add_rule(DoorOptions())
grammar.add_rule(WedgeIt())
grammar.add_rule(RemoveTheWedge())
grammar.add_rule(UseTheWand())
grammar.add_rule(StackUp())
grammar.add_rule(BreachAndClear())
grammar.add_rule(PickLock())
grammar.add_rule(GroundOptions())
grammar.add_rule(FallIn())
grammar.add_rule(UseDeployable())
grammar.add_rule(NpcPlayerInteract())
grammar.add_rule(NpcTeamRestrain())
grammar.add_rule(NpcTeamDeploy())
grammar.add_rule(ExecuteDefault())
# grammar.add_rule(TeamMemberOptions()) # needs key bindings for alpha-delta in-game
# grammar.add_rule(SelectTeamMember()) # needs key bindings for alpha-delta in-game

grammar_priority.add_rule(YellFreeze())
if USE_NOISE_SINK:
    grammar_priority.add_rule(NoiseSink())

# ---------------------------------------------------------------------------
# Load the grammar instance, register RecognitionObservers, and define how
# to unload them.

grammar.load()
grammar_priority.load()

# ---------------------------------------------------------------------------
# Push to talk, mute, toggle

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
if DEBUG_MODE:
    from lark import Lark, Token
    import itertools
    grammar_string = r"""
?start: alternative

// ? means that the rule will be inlined iff there is a single child
?alternative: sequence ("|" sequence)*
?sequence: single*
         | sequence "{" WORD "}"  -> special

?single: WORD+               -> literal
      | "<" WORD ">"         -> reference
      | "[" alternative "]"  -> optional
      | "(" alternative ")"

// Match anything which is not whitespace or a control character,
// we will let the engine handle invalid words
WORD: /[^\s\[\]<>|(){}]+/

%import common.WS_INLINE
%ignore WS_INLINE
"""

    def do_on_tree_item(tree_item):
        elements = []
        if tree_item.data == "literal":
            literal_children = []
            for child in tree_item.children:
                literal_children.append(child)
            elements.append(' '.join(literal_children))
            literal_children = None
            return elements
        if tree_item.data == "optional": 
            elements.append("")
            for child in tree_item.children:
                if child is None: 
                    continue
                elements.extend(do_on_tree_item(child))
            return elements
        if tree_item.data == "alternative": 
            for child in tree_item.children:
                if child is None: 
                    continue
                elements.extend(do_on_tree_item(child))
            return elements
        if tree_item.data == "sequence": 
            for child in tree_item.children:
                if child is None: 
                    continue
                elements.append(do_on_tree_item(child))
            product_iter = itertools.product(*elements)
            product_list = [' '.join((' '.join(i)).split()) for i in product_iter]
            product_set = set(product_list)
            product_list = list(product_set)
            product_set = None
            return product_list

    with open(".debug_grammar_readyornot.txt", "w") as file:
        file.write(grammar.get_complexity_string())
        file.write(f"\n{grammar_priority.get_complexity_string()}\n")

        for rule in grammar.rules:
            file.write(f"\n\n---{rule.name}---")
            file.write(f"\n{rule.element.gstring()}")
            file.write(f"\n---")

            # file.write(f"\n{rule._element.element_tree_string()}")
            # file.write(f"\n---")

            spec_parser = Lark(grammar_string, parser="lalr")
            tree = spec_parser.parse(rule.element.gstring())
            # file.write(f"\n{tree.pretty()}")
            
            if DEBUG_HEAVY_DUMP_GRAMMAR: 
                # do_on_tree_item() can be expensive on memory, so we don't do this for 
                # just DEBUG_MODE
                for tree_item in tree.children:
                    tree_item_options = do_on_tree_item(tree_item)
                    file.write(f"\n{tree_item_options}")
                file.write(f"\n---")
            try:
                if hasattr(rule, 'spec'):
                    file.write(f"\n{rule.spec}")
                if hasattr(rule, 'extras'):
                    for extra in rule.extras:
                        if isinstance(extra, Choice):
                            choice_name = extra.name
                            choice_keys = list(extra._choices.keys())
                            file.write(f"\n{choice_name}={choice_keys}")
                        elif isinstance(extra, Optional):
                            if isinstance(extra._child, Choice):
                                el_name = extra.name
                                choice_keys = list(extra._child._choices.keys())
                                file.write(f"\n{el_name}=Optional({choice_keys})")
                        else:
                            el_name = extra.name
                            el_tree = extra.element_tree_string()
                            file.write(f"\n{el_name}={el_tree}")
            except Exception: 
                # it doesn't matter if we can't dump the grammar into a file & it may fail
                # if rules are added that don't only use CompoundRule and Choice
                print(f"Unable to grammar dump all of {rule.name}")
                pass
            file.write(f"\n------------")

        for rule in grammar_priority.rules:
            file.write(f"\n\n{rule.element.gstring()}")

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
