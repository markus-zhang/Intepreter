import sys

class Token:
    def __init__(self, line, column, category, lexeme) -> None:
        self.line = line
        self.column = column
        self.category = category
        self.lexeme = lexeme

# Global Variables
trace = True        # Controls token trace
source = ''         # receives entire source program
sourceindex = 0     # index into source
line = 0            # current line number
column = 0          # current column number
tokenlist = []      # list of tokens to be consumed by parser
prevchar = '\n'     # '\n' in prevchar signals start of new line
blankline = True    # Set to False if line is not blank

# Category constants
EOF         = 0
PRINT       = 1
UNSIGNEDINT = 2
NAME        = 3     # identifier that is not a keyword
ASSIGNOP    = 4     # '=', assignment operator
LEFTPAREN   = 5
RIGHTPAREN  = 6
PLUS        = 7     # '+'
MINUS       = 8
TIMES       = 9     # '*'
NEWLINE     = 10
ERROR       = 11    # if none of above, then error

# Displayable names for each token category
catnames = [
    'EOF', 'PRINT', 'UNSIGNEDINT', 'NAME', 'ASSIGNOP', 'LEFTPAREN', 'RIGHTPAREN',
    'PLUS', 'MINUS', 'TIMES', 'NEWLINE', 'ERROR'
]

# Keywords and their token categories
keywords = {
    'print': PRINT
}

# One-character tokens and their token categories
smalltokens = {
    '=':    ASSIGNOP,
    '(':    LEFTPAREN,
    ')':    RIGHTPAREN,
    '+':    PLUS,
    '-':    MINUS,
    '*':    TIMES,
    '\n':   NEWLINE,
    '':     EOF
}

# getchar() gets next char from source and adjusts line and column
def getchar():
    global sourceindex, column, line, prevchar, blankline

    # check if starting a new line
    if prevchar == '\n':
        line += 1
        column = 0
        # Reset blankline
        blankline = True

    # end of source code
    if sourceindex >= len(source):
        column = 1
        prevchar = ''
        # Return null str which signals end of source
        return ''
    
    c = source[sourceindex]
    sourceindex += 1
    column += 1
    # if c is not whitespace then the whole line is not blank
    if not c.isspace():
        blankline = False
    prevchar = c

    # if at end of blank line, return space in place of '\n'
    if c == '\n' and blankline:
        return ' '
    else:
        return c

def tokenizer():
    global token
    curchar = ' '

    while True:
        # skip whitespace but not newlines
        while curchar != '\n' and curchar.isspace():
            curchar = getchar()

        token = Token(line, column, None, '')

        # Start of unsigned int?
        if curchar.isdigit():
            token.category = UNSIGNEDINT
            while True:
                token.lexeme += curchar
                curchar = getchar()
                if not curchar.isdigit():
                    # print(token.lexeme)
                    break

        # Start of name?
        elif curchar.isalpha() or curchar == '_':
            token.category = NAME
            while True:
                token.lexeme += curchar
                curchar = getchar()
                if not (curchar.isalnum() or curchar == '_'):
                    break

            # Check if it belongs to keywords
            if token.lexeme in keywords:
                token.category = keywords[token.lexeme]

        # Small tokens such as +, -, *, etc.
        elif curchar in smalltokens:
            token.category = smalltokens[curchar]
            token.lexeme = curchar
            curchar = getchar()
        
        # Anything else is error
        else:
            token.category = ERROR
            token.lexeme = curchar
            raise RuntimeError('Invalid token')
        
        tokenlist.append(token)
        if trace:
            print(f"{str(token.line)}   {str(token.column)}    {catnames[token.category]}   {token.lexeme}")
        
        if token.category == EOF:
            break

# main() reads input file and calls tokenizer
def main():
    global source

    if len(sys.argv) == 2:
        try:
            infile = open(sys.argv[1], 'r')
            source = infile.read()
        except IOError:
            print(f'Failed to read input file {sys.argv[1]}')
            sys.exit(1)
    else:
        print('Wrong number of command line arguments')
        print('Usage: python3 tokenizer.py <infile>')
        sys.exit(1)

    # Add newline to end if missing TODO: Why does the last line need a newline?
    # (probably because the parser needs a newline to properly identify one line)
    if source[-1] != '\n':
        source = source + '\n'
    
    # For token trace
    if trace:
        print('Line Col Category            Lexeme\n')

    try:
        tokenizer()
        # print(tokenlist)
    except RuntimeError as emsg:
        # In output, show '\n' for newline
        lexeme = token.lexeme.replace('\n', '\\n')
        print(f"\nError on '{lexeme}' ' line {str(token.line)} ' column {str(token.column)}'")
        print(emsg)
        sys.exit(1)

main()