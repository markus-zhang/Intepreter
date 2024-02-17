class Token:
    def __init__(self, line, column, category, lexeme) -> None:
        self.line = line
        self.column = column
        self.category = category
        self.lexeme = lexeme

# Category constants
EOF                 = 0
PRINT               = 1
UNSIGNEDNUM         = 2
NAME                = 3     # identifier that is not a keyword
ASSIGNOP            = 4     # '=', assignment operator
LEFTPAREN           = 5
RIGHTPAREN          = 6
PLUS                = 7     # '+'
MINUS               = 8     # '-'
TIMES               = 9     # '*'
NEWLINE             = 10
COMMENT_SINGLE      = 11
COMMENT_MULTIPLE    = 12
STRING              = 13
PYPASS              = 14
DIVISION            = 15
PYIF                = 16
PYWHILE             = 17
PYTRUE              = 18
PYFALSE             = 19
PYNONE              = 20
EQUAL               = 21
NOTEQUAL            = 22
LESSTHAN            = 23
LESSEQUAL           = 24
GREATERTHAN         = 25
GREATEREQUAL        = 26
COMMA               = 27
COLON               = 28
INDENT              = 29
DEDENT              = 30
PYELSE              = 31
BREAK               = 32
ADDASSIGN           = 33
SUBASSIGN           = 34
MULASSIGN           = 35
DIVASSIGN           = 36
PYELIF              = 37
MODULO              = 38
INTEGER             = 39
FLOAT               = 40
DEF                 = 41
GLOBAL              = 42
RETURN              = 43
ERROR               = 255   # if none of above, then error

# Displayable names for each token category, using dictionary
catnames = {
    0:  'EOF',
    1:  'PRINT',
    2:  'UNSIGNEDNUM',
    3:  'NAME',
    4:  'ASSIGNOP',
    5:  'LEFTPAREN',
    6:  'RIGHTPAREN',
    7:  'PLUS',
    8:  'MINUS',
    9:  'TIMES',
    10: 'NEWLINE',
    11: 'COMMENT_SINGLE',
    12: 'COMMENT_MULTIPLE',
    13: 'STRING',
    14: 'PYPASS',
    15: 'DIVISION',
    16: 'PYIF',
    17: 'PYWHILE',
    18: 'PYTRUE',
    19: 'PYFALSE',
    20: 'PYNONE',
    21: 'EQUAL',
    22: 'NOTEQUAL',
    23: 'LESSTHAN',
    24: 'LESSEQUAL',
    25: 'GREATERTHAN',
    26: 'GREATEREQUAL',
    27: 'COMMA',
    28: 'COLON',
    29: 'INDENTATION',
    30: 'DEDENTATION',
    31: 'PYELSE',
    32: 'BREAK',
    33: 'ADDASSIGN',
    34: 'SUBASSIGN',
    35: 'MULASSIGN',
    36: 'DIVASSIGN',
    37: 'PYELIF',
    38: 'MODULO',
    39: 'INTEGER',
    40: 'FLOAT',
    41: 'DEF',
    42: 'GLOBAL',
    43: 'RETURN',
    255:'ERROR'
}

# Keywords and their token categories
keywords = {
    'print':    PRINT,
    'pass':     PYPASS,
    'if':       PYIF,
    'elif':     PYELIF,
    'else':     PYELSE,
    'while':    PYWHILE,
    'True':     PYTRUE,
    'False':    PYFALSE,
    'None':     PYNONE,
    'break':    BREAK,
    'def':      DEF,
    'global':   GLOBAL,
    'return':   RETURN
}

# One-character tokens and their token categories
smalltokens = {
    '=':    ASSIGNOP,
    '==':   EQUAL,
    '!=':   NOTEQUAL,
    '(':    LEFTPAREN,
    ')':    RIGHTPAREN,
    '+':    PLUS,
    '-':    MINUS,
    '*':    TIMES,
    '/':    DIVISION,
    '%':    MODULO,
    '\n':   NEWLINE,
    ':':    COLON,
    ',':    COMMA,
    '+=':   ADDASSIGN,
    '-=':   SUBASSIGN,
    '*=':   MULASSIGN,
    '/=':   DIVASSIGN,
    '':     EOF
}

stmttokens = [PYIF, PYWHILE, PRINT, PYPASS, NAME, BREAK, DEF, RETURN]