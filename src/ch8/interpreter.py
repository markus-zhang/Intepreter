import sys

class Token:
    def __init__(self, line, column, category, lexeme) -> None:
        self.line = line
        self.column = column
        self.category = category
        self.lexeme = lexeme

# Global Variables
trace = False       # Controls token trace
source = ''         # receives entire source program
sourceindex = 0     # index into source
line = 0            # current line number
column = 0          # current column number
tokenlist = []      # list of tokens to be consumed by parser
tokenindex = 0
prevchar = '\n'     # '\n' in prevchar signals start of new line
blankline = True    # Set to False if line is not blank
symboltable = {}    # Symbol Table for the interpreter
operandstack = []          # Use a list for the stack

# Category constants
EOF                 = 0
PRINT               = 1
UNSIGNEDINT         = 2
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
ERROR               = 255   # if none of above, then error

# Displayable names for each token category, using dictionary
catnames = {
    0:  'EOF',
    1:  'PRINT',
    2:  'UNSIGNEDINT',
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
    255:'ERROR'
}

# Keywords and their token categories
keywords = {
    'print': PRINT,
    'pass': PYPASS
}

# One-character tokens and their token categories
smalltokens = {
    '=':    ASSIGNOP,
    '(':    LEFTPAREN,
    ')':    RIGHTPAREN,
    '+':    PLUS,
    '-':    MINUS,
    '*':    TIMES,
    '/':    DIVISION,
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
    prevchar = ' '
    # For multiple line comments
    s_comment_multiple = False

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

        # Single line comment
        elif curchar == '#':
            token.category = COMMENT_SINGLE
            while True:
                token.lexeme += curchar
                curchar = getchar()
                if curchar == '\n':
                    break

        # Multiple line comment opening
        elif curchar == '/':
            # We want to include / into the token before it moves to check *
            token.lexeme += curchar
            curchar = getchar()
            if curchar != '*':
                raise RuntimeError('Invalid token - multiple line comment opening: read / and expecting *')
            else:
                token.category = COMMENT_MULTIPLE
                s_comment_multiple = True
                # Get ready for closing check, we must have */ combo
                # But it must be a new *, not the one we already met
                # So move curchar first (here we don't care about prevchar)
                token.lexeme += curchar
                curchar = getchar()
                while True:
                    token.lexeme += curchar                  
                    prevchar = curchar
                    curchar = getchar()
                    # Multiple line comment closing
                    # We need to first check for / and then go back for *
                    # Because of edge cases such as /*******/
                    # if curchar == '*':
                    if curchar == '/' and prevchar == '*':
                        token.lexeme += curchar
                        curchar = getchar()
                        s_comment_multiple = False
                        # Don't forget to move curchar forward. Each block must do this
                        break 
        
        # Strings, we all love them. Only allow double quoted ones
        elif curchar == '"':       
            token.category = STRING
            token.lexeme += curchar
            curchar = getchar()
            while True:
                if curchar == '"':
                    token.lexeme += curchar
                    curchar = getchar()
                    break
                # Allow escape char
                # Just read one more and move on
                elif curchar == '\\':
                    token.lexeme += curchar
                    # Next char is the one to be excaped
                    curchar = getchar()
                    token.lexeme += curchar
                    curchar = getchar()
                else:
                    token.lexeme += curchar
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

# Parser code
# Note that parser should be called after tokenizer
# Each line of the following CFG is a rule (a Python function)
###############################################################
# <program>         -> <stmt>* EOF
# <stmt>            -> <simplestmt> NEWLINE
# <simplestmt>      -> <printstmt>
# <simplestmt>      -> <assignmentstmt>
# <simplestmt>      -> <passstmt>
# <printstmt>       -> 'print' '(' <expr> ')'
# <assignmentstmt>  -> NAME '=' <expr>
# <passstmt>        -> 'pass'
# <expr>            -> <term> ('+' <term>)*
# <expr>            -> <term> ('-' <term>)*
# <term>            -> <factor> ('*' <factor>)*
# <term>            -> <factor> ('/' <factor>)*
# <factor>          -> '+' <factor>
# <factor>          -> '-' <factor>
# <factor>          -> NAME
# <factor>          -> UNSIGNEDINT
# <factor>          -> '(' <expr> ')'
###############################################################
def program():
    # <program>         -> <stmt>* EOF
    while token.category in [PRINT, NAME]:
        stmt()
    consume(EOF)

def stmt():
    # <stmt>            -> <simplestmt> NEWLINE
    simplestmt()
    consume(NEWLINE)

def simplestmt():
    # <simplestmt>      -> <printstmt>
    # <simplestmt>      -> <assignmentstmt>
    if token.category == PRINT:
        printstmt()
    elif token.category == NAME:
        assignmentstmt()
    elif token.category == PYPASS:
        passstmt()
    else:
        raise RuntimeError("Expecting PRINT or NAME") 
    
def printstmt():
    # <printstmt>       -> 'print' '(' <expr> ')'
    # We already know the first token must be 'print' so no need to check
    advance()
    consume(LEFTPAREN)
    expr()  # Expect expr() to push the result onto the top of the operand stack
    print(operandstack.pop())
    consume(RIGHTPAREN)

def assignmentstmt():
    # <assignmentstmt>  -> NAME '=' <expr>
    # We already know the first token must be NAME so no need to check
    # Pick up the token as symbol
    left = token.lexeme
    advance()
    consume(ASSIGNOP)
    expr()
    # expr() pushes onto top of the operand stack, update symbol table
    global symboltable
    symboltable[left] = operandstack.pop()

def passstmt():
    advance()

def expr():
    # <expr>            -> <term> ('+' <term>)*
    # <expr>            -> <term> ('-' <term>)*
    # NOTE: There is no advance() at the end of the function
    # NOTE: because expr() doesn't have a terminal symbol.
    # NOTE: We will be able to find one in term() (or its functions)
    term()
    while token.category == PLUS or token.category == MINUS:
        # Now the left side was pushed onto the operand stack
        # Note that the left side must be in the loop for multiple operations
        optoken = token
        global operandstack
        left = operandstack.pop()
        advance()
        term()
        # Now the right side was pushed onto the operand stack
        right = operandstack.pop()
        if optoken.category == PLUS:
            operandstack.append(left + right)
        else:
            operandstack.append(left - right)

def term():
    # <term>            -> <factor> ('*' <factor>)*
    # <term>            -> <factor> ('/' <factor>)*
    factor()
    while token.category == TIMES or token.category == DIVISION:
        # Now the left side was pushed onto the operand stack
        # Note that the left side must be in the loop for multiple operations
        optoken = token
        global operandstack
        left = operandstack.pop()
        advance()
        factor()
        # Now the right side was pushed onto the operand stack
        right = operandstack.pop()
        if optoken.category == TIMES:
            operandstack.append(left * right)
        else:
            operandstack.append(left / right)

def factor():
    # <factor>          -> '+' <factor>
    # <factor>          -> '-' <factor>
    # <factor>          -> NAME
    # <factor>          -> UNSIGNEDINT
    # <factor>          -> '(' <expr> ')'
    global operandstack, symboltable
    if token.category == PLUS:
        advance()
        factor()
        # Now the right side must also be on the stack
        right = operandstack.pop()
        operandstack.append(right)
    elif token.category == MINUS:
        advance()
        factor()
        # Now the right side must also be on the stack
        right = operandstack.pop()
        operandstack.append(-1 * right)
    elif token.category == NAME:
        # NAME in <factor> is always on the right side, so check whether it exists
        if token.lexeme not in symboltable:
            raise RuntimeError(f"Name {token.lexeme} is not defined.")
        operandstack.append(symboltable[token.lexeme])
        advance()
    elif token.category == UNSIGNEDINT:
        operandstack.append(int(token.lexeme))
        advance()
    elif token.category == LEFTPAREN:
        advance()
        expr()
        consume(RIGHTPAREN)
    else:
        raise RuntimeError("Expecting a valid expression.")

def advance():
    """Advance the reading of a token from tokenlist.
    The variable "token" always contain the current token
    """
    global token, tokenindex
    # Move to next token
    tokenindex += 1     
    if tokenindex >= len(tokenlist):
        # I assume the script ends gracefully once encounters an EOF token
        raise RuntimeError("Unexpected end of file")    
    token = tokenlist[tokenindex]

def consume(expectedcat: int):
    """Consumes the expected category.
    Assuming we see a "print" token, we should expect a left parenthesis token immediately
    """
    if token.category != expectedcat:
        raise RuntimeError(f"Expecting {catnames[expectedcat]} but get {catnames[token.category]}")
    elif token.category == EOF:
        # We are done
        return
    else:
        advance()

def parser():
    global token, tokenindex
    token = tokenlist[0]
    tokenindex = 0
    program()
    print("End of parsing")


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
        print('Usage: python3 interpreter.py <infile>')
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
        parser()
    except RuntimeError as emsg:
        # In output, show '\n' for newline
        lexeme = token.lexeme.replace('\n', '\\n')
        # print(f"\nError on '{lexeme}' ' line {str(token.line)} ' column {str(token.column)}'")
        # Added the feature to enrigh Runtime Error message:
        # Show the line with a caret pointing to the token
        sourcesplit = source.split('\n')
        print(sourcesplit[token.line - 1])
        print(' ' * (token.column - 1) + '^')
        print(emsg)
        sys.exit(1)

main()