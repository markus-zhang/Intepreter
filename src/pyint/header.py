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

# globals
# Global Variables
# Section 1: Debugging and logging
trace = False           # Controls token trace
only_tokenizer = False   # If True, exit to OS after tokenizer
dump_tokenizer = True   # Should we dump the trace from the tokenizer into a local file?
token_dump_file = 'C:/Dev/Projects/Intepreter/src/pyint/token.dump'

# Section 2: Lexing
source = ''             # receives entire source program
sourceindex = 0         # index into source
line = 0                # current line number
column = 0              # current column number
tokenlist = []          # list of tokens to be consumed by parser
tokenindex = 0
prevchar = '\n'         # '\n' in prevchar signals start of new line
blankline = True        # Set to False if line is not blank

# Section 3: Parsing
# For function calls
# Symbol Table:
# symboltable = {}                # Symbol Table for the interpreter
# We need to split the symbol table into two: local and global
localsymboltable = {}
localsymboltablebackup = {}     # This is for function call within function call, basically this is for the caller scope while localsymboltable is for callee scope
globalsymboltable = {}
# OK now we have two symbol tables, which one do we store into/load from?
# We track function call depth, 0 means global, positive means local, and negative means we made some mistakes in tracking
functioncalldepth = 0
# If some variables are declared global using the "global" keyword, put into this set so that we know
globalvardeclared:set = set()
# For return addresses, since function calls can be chained, a stack is the natural solution
returnaddrstack = []

# For expression evaulation and fetch
operandstack = []               # Use a list for the stack

# For indentation and dedentation
# Setup as column 1
indentstack = [1]

# For tracking parent loop indentations so that we can break out of it, see breakstat() and codeblock() for why
indentloop = []
flagloop = False
flagbreak = False
flagbreakloop = False