# vim: set fileencoding=utf-8
from keyevents import *

# German keyboard layout
KEY_MAP = {
        '\n': (KEY_ENTER,),
        'a': (KEY_A,),
        'b': (KEY_B,),
        'c': (KEY_C,),
        'd': (KEY_D,),
        'e': (KEY_E,),
        'f': (KEY_F,),
        'g': (KEY_G,),
        'h': (KEY_H,),
        'i': (KEY_I,),
        'j': (KEY_J,),
        'k': (KEY_K,),
        'l': (KEY_L,),
        'm': (KEY_M,),
        'n': (KEY_N,),
        'o': (KEY_O,),
        'p': (KEY_P,),
        'q': (KEY_Q,),
        'r': (KEY_R,),
        's': (KEY_S,),
        't': (KEY_T,),
        'u': (KEY_U,),
        'v': (KEY_V,),
        'w': (KEY_W,),
        'x': (KEY_X,),
        'y': (KEY_Z,),
        'z': (KEY_Y,),
        'A': (KEY_RIGHTSHIFT, KEY_A),
        'B': (KEY_RIGHTSHIFT, KEY_B),
        'C': (KEY_RIGHTSHIFT, KEY_C),
        'D': (KEY_RIGHTSHIFT, KEY_D),
        'E': (KEY_RIGHTSHIFT, KEY_E),
        'F': (KEY_RIGHTSHIFT, KEY_F),
        'G': (KEY_RIGHTSHIFT, KEY_G),
        'H': (KEY_RIGHTSHIFT, KEY_H),
        'I': (KEY_RIGHTSHIFT, KEY_I),
        'J': (KEY_RIGHTSHIFT, KEY_J),
        'K': (KEY_RIGHTSHIFT, KEY_K),
        'L': (KEY_RIGHTSHIFT, KEY_L),
        'M': (KEY_RIGHTSHIFT, KEY_M),
        'N': (KEY_RIGHTSHIFT, KEY_N),
        'O': (KEY_RIGHTSHIFT, KEY_O),
        'P': (KEY_RIGHTSHIFT, KEY_P),
        'Q': (KEY_RIGHTSHIFT, KEY_Q),
        'R': (KEY_RIGHTSHIFT, KEY_R),
        'S': (KEY_RIGHTSHIFT, KEY_S),
        'T': (KEY_RIGHTSHIFT, KEY_T),
        'U': (KEY_RIGHTSHIFT, KEY_U),
        'V': (KEY_RIGHTSHIFT, KEY_V),
        'W': (KEY_RIGHTSHIFT, KEY_W),
        'X': (KEY_RIGHTSHIFT, KEY_X),
        'Y': (KEY_RIGHTSHIFT, KEY_Z),
        'Z': (KEY_RIGHTSHIFT, KEY_Y),
        'ü': (KEY_LEFTBRACE,),
        'ö': (KEY_SEMICOLON,),
        'ä': (KEY_APOSTROPHE,),
        'Ü': (KEY_RIGHTSHIFT, KEY_LEFTBRACE),
        'Ö': (KEY_RIGHTSHIFT, KEY_SEMICOLON),
        'Ä': (KEY_RIGHTSHIFT, KEY_APOSTROPHE),
        '1': (KEY_1,),
        '2': (KEY_2,),
        '3': (KEY_3,),
        '4': (KEY_4,),
        '5': (KEY_5,),
        '6': (KEY_6,),
        '7': (KEY_7,),
        '8': (KEY_8,),
        '9': (KEY_9,),
        '0': (KEY_0,),
        '!': (KEY_RIGHTSHIFT, KEY_1),
        '"': (KEY_RIGHTSHIFT, KEY_2),
        '§': (KEY_RIGHTSHIFT, KEY_3),
        '$': (KEY_RIGHTSHIFT, KEY_4),
        '%': (KEY_RIGHTSHIFT, KEY_5),
        '&': (KEY_RIGHTSHIFT, KEY_6),
        '/': (KEY_RIGHTSHIFT, KEY_7),
        '(': (KEY_RIGHTSHIFT, KEY_8),
        ')': (KEY_RIGHTSHIFT, KEY_9),
        '=': (KEY_RIGHTSHIFT, KEY_0),
        '¹': (KEY_RIGHTALT, KEY_1),
        '²': (KEY_RIGHTALT, KEY_2),
        '³': (KEY_RIGHTALT, KEY_3),
        '¼': (KEY_RIGHTALT, KEY_4),
        '½': (KEY_RIGHTALT, KEY_5),
        '{': (KEY_RIGHTALT, KEY_7),
        '[': (KEY_RIGHTALT, KEY_8),
        ']': (KEY_RIGHTALT, KEY_9),
        '}': (KEY_RIGHTALT, KEY_0),
        '€': (KEY_RIGHTALT, KEY_E),
        'µ': (KEY_RIGHTALT, KEY_M),
        '@': (KEY_RIGHTALT, KEY_Q),
        '«': (KEY_RIGHTALT, KEY_X),
        '»': (KEY_RIGHTALT, KEY_Z),
        '„': (KEY_RIGHTALT, KEY_V),
        '“': (KEY_RIGHTALT, KEY_B),
        '”': (KEY_RIGHTALT, KEY_N),
        '·': (KEY_RIGHTALT, KEY_COMMA),
        '…': (KEY_RIGHTALT, KEY_DOT),
        ',': (KEY_COMMA,),
        ';': (KEY_RIGHTSHIFT, KEY_COMMA),
        '.': (KEY_DOT,),
        ':': (KEY_RIGHTSHIFT, KEY_DOT),
        '-': (KEY_SLASH,),
        '_': (KEY_RIGHTSHIFT, KEY_SLASH),
        '<': (KEY_102ND,),
        '>': (KEY_RIGHTSHIFT, KEY_102ND),
        '|': (KEY_RIGHTALT, KEY_102ND),
        'ß': (KEY_MINUS,),
        '?': (KEY_RIGHTSHIFT, KEY_MINUS),
        '\\': (KEY_RIGHTALT, KEY_MINUS),
        '`': (KEY_RIGHTSHIFT, KEY_EQUAL, KEY_SPACE),
        '+': (KEY_RIGHTBRACE,),
        '*': (KEY_RIGHTSHIFT, KEY_RIGHTBRACE),
        '~': (KEY_RIGHTALT, KEY_RIGHTBRACE),
        '#': (KEY_BACKSLASH,),
        '\'': (KEY_RIGHTSHIFT, KEY_BACKSLASH),
        '^': (KEY_GRAVE, KEY_SPACE),
        '°': (KEY_RIGHTSHIFT, KEY_GRAVE),
        ' ': (KEY_SPACE,),
        'ê': (KEY_GRAVE, KEY_RELEASEALL, KEY_E),
        'é': (KEY_EQUAL, KEY_RELEASEALL, KEY_E),
        'è': (KEY_RIGHTSHIFT, KEY_EQUAL, KEY_RELEASEALL, KEY_E),
        'ô': (KEY_GRAVE, KEY_RELEASEALL, KEY_O),
        'ó': (KEY_EQUAL, KEY_RELEASEALL, KEY_O),
        'ò': (KEY_RIGHTSHIFT, KEY_EQUAL, KEY_RELEASEALL, KEY_O),
        'â': (KEY_GRAVE, KEY_RELEASEALL, KEY_A),
        'á': (KEY_EQUAL, KEY_RELEASEALL, KEY_A),
        'à': (KEY_RIGHTSHIFT, KEY_EQUAL, KEY_RELEASEALL, KEY_A),
        'î': (KEY_GRAVE, KEY_RELEASEALL, KEY_I),
        'í': (KEY_EQUAL, KEY_RELEASEALL, KEY_I),
        'ì': (KEY_RIGHTSHIFT, KEY_EQUAL, KEY_RELEASEALL, KEY_I),
        'û': (KEY_GRAVE, KEY_RELEASEALL, KEY_U),
        'ú': (KEY_EQUAL, KEY_RELEASEALL, KEY_U),
        'ù': (KEY_RIGHTSHIFT, KEY_EQUAL, KEY_RELEASEALL, KEY_U),
        'Ê': (KEY_GRAVE, KEY_RELEASEALL, KEY_RIGHTSHIFT, KEY_E),
        'É': (KEY_EQUAL, KEY_RELEASEALL, KEY_RIGHTSHIFT, KEY_E),
        'È': (KEY_RIGHTSHIFT, KEY_EQUAL, KEY_RELEASEALL,
              KEY_RIGHTSHIFT, KEY_E),
        'Ô': (KEY_GRAVE, KEY_RELEASEALL, KEY_RIGHTSHIFT, KEY_O),
        'Ó': (KEY_EQUAL, KEY_RELEASEALL, KEY_RIGHTSHIFT, KEY_O),
        'Ò': (KEY_RIGHTSHIFT, KEY_EQUAL, KEY_RELEASEALL, KEY_RIGHTSHIFT,
              KEY_O),
        'Î': (KEY_GRAVE, KEY_RELEASEALL, KEY_RIGHTSHIFT, KEY_I),
        'Í': (KEY_EQUAL, KEY_RELEASEALL, KEY_RIGHTSHIFT, KEY_I),
        'Ì': (KEY_RIGHTSHIFT, KEY_EQUAL, KEY_RELEASEALL, KEY_RIGHTSHIFT,
              KEY_I),
        'Û': (KEY_GRAVE, KEY_RELEASEALL, KEY_RIGHTSHIFT, KEY_U),
        'Ú': (KEY_EQUAL, KEY_RELEASEALL, KEY_RIGHTSHIFT, KEY_U),
        'Ù': (KEY_RIGHTSHIFT, KEY_EQUAL, KEY_RELEASEALL, KEY_RIGHTSHIFT,
              KEY_U),
        'Â': (KEY_GRAVE, KEY_RELEASEALL, KEY_RIGHTSHIFT, KEY_A),
        'Á': (KEY_EQUAL, KEY_RELEASEALL, KEY_RIGHTSHIFT, KEY_A),
        'À': (KEY_RIGHTSHIFT, KEY_EQUAL, KEY_RELEASEALL, KEY_RIGHTSHIFT,
              KEY_A),
        'ẑ': (KEY_GRAVE, KEY_RELEASEALL, KEY_Y),
        'Ẑ': (KEY_GRAVE, KEY_RELEASEALL, KEY_RIGHTSHIFT, KEY_Y),
        'ź': (KEY_EQUAL, KEY_RELEASEALL, KEY_Y),
        'Ź': (KEY_EQUAL, KEY_RELEASEALL, KEY_RIGHTSHIFT, KEY_Y),
        'ĉ': (KEY_GRAVE, KEY_RELEASEALL, KEY_C),
        'Ĉ': (KEY_GRAVE, KEY_RELEASEALL, KEY_RIGHTSHIFT, KEY_C),
        'ć': (KEY_EQUAL, KEY_RELEASEALL, KEY_C),
        'Ć': (KEY_EQUAL, KEY_RELEASEALL, KEY_RIGHTSHIFT, KEY_C),
        'ŝ': (KEY_GRAVE, KEY_RELEASEALL, KEY_S),
        'Ŝ': (KEY_GRAVE, KEY_RELEASEALL, KEY_RIGHTSHIFT, KEY_S),
        'ĵ': (KEY_GRAVE, KEY_RELEASEALL, KEY_J),
        'Ĵ': (KEY_GRAVE, KEY_RELEASEALL, KEY_RIGHTSHIFT, KEY_J),
        'ĥ': (KEY_GRAVE, KEY_RELEASEALL, KEY_H),
        'Ĥ': (KEY_GRAVE, KEY_RELEASEALL, KEY_RIGHTSHIFT, KEY_H),
        'ĝ': (KEY_GRAVE, KEY_RELEASEALL, KEY_G),
        'Ĝ': (KEY_GRAVE, KEY_RELEASEALL, KEY_RIGHTSHIFT, KEY_G),
        'ŷ': (KEY_GRAVE, KEY_RELEASEALL, KEY_Z),
        'Ŷ': (KEY_GRAVE, KEY_RELEASEALL, KEY_RIGHTSHIFT, KEY_Z)
        }
