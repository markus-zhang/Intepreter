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
tokenindex = 0
prevchar = '\n'     # '\n' in prevchar signals start of new line
blankline = True    # Set to False if line is not blank
symboltable = {}    # Symbol Table for the interpreter
operandstack = []   # Use a list for the stack
# For indentation and dedentation
# Setup as column 1
indentstack = [1]

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
    255:'ERROR'
}

# Keywords and their token categories
keywords = {
    'print': PRINT,
    'pass': PYPASS,
    'if': PYIF,
    'while': PYWHILE,
    'True': PYTRUE,
    'False': PYFALSE,
    'None': PYNONE
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
    '\n':   NEWLINE,
    ':':    COLON,
    ',':    COMMA,
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

def peekchar():
    global sourceindex
    if sourceindex >= len(source) - 1:
        return ''
    else:
        return source[sourceindex]

def tokenizer():
    global token
    curchar = ' '
    prevchar = ' '

    while True:
        # skip whitespace but not newlines
        while curchar != '\n' and curchar.isspace():
            curchar = getchar()

        token = Token(line, column, None, '')

        # How do we track indentation and dedentation?
        # We should start tracking once we reach a CRLC char
        # If the next char is a space of some sort, 
        # we count the number of spaces and add into the indentation
        """
        if curchar == '\n':
            # TODO: Set up a flag for the main loop
            # TODO: Move the whole following logic to a new if
            # TODO: If the flag is set, start calculate indentation
            flag_indentation = True
            # Special case for EOF, which is always after a CRLF due to our treatment
            if peekchar() == '':
                # curchar is EOF
                curchar = getchar()
                continue
            elif peekchar() == ' ':
                token.category = INDENTATION
                # As the stack, we start from column 1
                indentation_count = 1
                while True:
                    curchar = getchar()
                    if curchar != ' ':
                        # Don't forget to push the count to stack!
                        indentstack.append(indentation_count)
                        break
                    else:
                        indentation_count += 1
                        token.lexeme += curchar
            # Special case for empty line, CRLF after CRLF
            # FIXME: Still buggy as it removes one NEWLINE
            elif peekchar() == '\n':
                curchar = getchar()
                token.category = NEWLINE
                token.lexeme += curchar
        """

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

        # Single line comment
        elif curchar == '#':
            token.category = COMMENT_SINGLE
            while True:
                token.lexeme += curchar
                curchar = getchar()
                if curchar == '\n':
                    break

        # Not equal
        elif curchar == '!':
            token.lexeme += curchar
            nextchar = peekchar()
            if nextchar != '=':
                raise RuntimeError("Expecting a '=' following '!'")
            else:
                curchar = getchar()
                token.category = NOTEQUAL
                token.lexeme += curchar
                curchar = getchar()

        # ASSIGNOP (=) and EQUAL (==)
        elif curchar == '=':
            token.lexeme += curchar
            nextchar = peekchar()
            if nextchar != '=':
                # Just a simple assignment operator
                token.category = ASSIGNOP
                curchar = getchar()
            else:
                # Now it's more interesting, an EQUAL!
                curchar = getchar()
                token.category = EQUAL
                token.lexeme += curchar
                curchar = getchar()

        # LESSTHAN (<) and LESSEQUAL (<=)
        elif curchar == '<':
            token.lexeme += curchar
            nextchar = peekchar()
            if nextchar != '=':
                # Just a simple less-than operator
                token.category = LESSTHAN
                curchar = getchar()
            else:
                # Now it's more interesting, a LESSEQUAL!
                curchar = getchar()
                token.category = LESSEQUAL
                token.lexeme += curchar
                curchar = getchar()

        # GREATERTHAN (>) and GREATEREQUAL (>=)
        elif curchar == '>':
            token.lexeme += curchar
            nextchar = peekchar()
            if nextchar != '=':
                # Just a simple less-than operator
                token.category = GREATERTHAN
                curchar = getchar()
            else:
                # Now it's more interesting, a LESSEQUAL!
                curchar = getchar()
                token.category = GREATEREQUAL
                token.lexeme += curchar
                curchar = getchar()

        # Multiple line comment opening
        elif curchar == '/':
            # We want to include / into the token before it moves to check *
            token.lexeme += curchar
            # Peek, don't Get
            nextchar = peekchar()
            if nextchar != '*':
                # Must be the division token
                token.category = smalltokens[curchar]
                token.lexeme = curchar
                # Do not get a new char, we need to keep the current char
                curchar = getchar()
            else:
                token.category = COMMENT_MULTIPLE
                s_comment_multiple = True
                # Get ready for closing check, we must have */ combo
                # But it must be a new *, not the one we already met
                # So move curchar first (here we don't care about prevchar)
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
                        # Don't forget to move curchar forward. Each block must do this
                        break 
        
        # The other small tokens such as +, -, *, etc.
        elif curchar in smalltokens:
            token.category = smalltokens[curchar]
            token.lexeme = curchar
            curchar = getchar()
            # Signal to tokenizer to calculate indentations
            if token.category == NEWLINE:
                flag_indentation = True
        
        # Strings, we all love them. Only allow double quoted ones
        elif curchar == '\'':       
            token.category = STRING
            # token.lexeme += curchar
            curchar = getchar()
            while True:
                if curchar == '\'':
                    # token.lexeme += curchar
                    curchar = getchar()
                    break
                # Allow escape char
                # Just read one more and move on
                elif curchar == '\\':
                    # token.lexeme += curchar
                    # Next char is the one to be excaped
                    curchar = getchar()
                    if curchar == 'n':
                        token.lexeme += '\n'
                    elif curchar == 't':
                        token.lexeme += '\t'
                    elif curchar == '\\':
                        token.lexeme += '\\'
                    elif curchar == 'b':
                        token.lexeme += '\b'
                    else:
                        raise RuntimeError("Only allow escape chars: \\n, \\t, \\, \\b")
                    curchar = getchar()
                else:
                    token.lexeme += curchar
                    curchar = getchar()
        
        # Anything else is error
        else:
            token.category = ERROR
            token.lexeme = curchar
            raise RuntimeError('Invalid token')
        
        """
        Check for indentations AFTER a NEWLINE has been appended
        Two cases: 
            1. the first line has leading spaces, so len(tokenlist) == 0
            2. the previous appended token is NEWLINE, and now we have a new token

        What do we do? Assuming we have indentstack as [1, 4, 7, 10].
        We check the column of the new token:
            - If it's indentstack[-1] < column, we append it, and add an INDENT token
            - If it's indentstack[-1] > column, we pop indentstack until we find one matching:
                - For each indent in indentstack, if indent > column, pop and add a DEDENT token
                - If indent == column, quit without popping it
                - If indent < column, something is wrong, raise a RuntimeError
        """
        if len(tokenlist) == 0 or tokenlist[-1].category == NEWLINE:
            if indentstack[-1] < token.column:
                # Append and add an INDENT
                token_indent = Token(line, 1, INDENT, '')
                # The beauty is that INDENT is created afterwards but appended before the first "real" token of the line
                tokenlist.append(token_indent)
                indentstack.append(token.column)
                if trace:
                    print(f"{str(token_indent.line)}   {str(token_indent.column)}    {catnames[token_indent.category]}   {str(token_indent.lexeme)}")
            else:
                while True:
                    if indentstack[-1] == token.column:
                        # Do nothing, no change in indentation of dedentation
                        break
                    if indentstack[-1] > token.column:
                        # Pop and add a DEDENT
                        # Do NOT pollute the original token as it is not appended yet
                        # Same line as the following token(parsed but yet appended)
                        # I put column as 1 but this is not important
                        token_dedent = Token(line, 1, DEDENT, '')
                        # The beauty is that DEDENT is created afterwards but appended before the first "real" token of the line
                        tokenlist.append(token_dedent)
                        if trace:
                            print(f"{str(token_dedent.line)}   {str(token_dedent.column)}    {catnames[token_dedent.category]}   {str(token_dedent.lexeme)}")
                        indentstack.pop()
                    else:
                        raise RuntimeError(f"Incorrect dedentation {token.column} for {indentstack}")
        
        tokenlist.append(token)
        
        trace()

        if token.category == EOF:
            traceall()
            print(indentstack)
            break

def trace():
    if trace:
        print(f"{str(token.line)}   {str(token.column)}    {catnames[token.category]}   {str(token.lexeme)}")

def traceall():
    if trace:
        for token in tokenlist:
            print(f"{str(token.line)}   {str(token.column)}    {catnames[token.category]}   {str(token.lexeme)}")

def removecomment():
    """Remove all comments from token list
    """
    global tokenlist
    for token in tokenlist:
        if token.category == COMMENT_MULTIPLE or token.category == COMMENT_SINGLE:
            tokenlist.remove(token)

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
# <factor>          -> STRING
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
    
    # NOTE: Now we introduce strings into the picture, we need to check types
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
        # If not of the same type then we simply cannot add or subtract
        if type(left) != type(right):
            raise RuntimeError(f"Cannot add/subtract {type(left)} with {type(right)}")
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
    # <factor>          -> STRING
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
    elif token.category == STRING:
        operandstack.append(token.lexeme)
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
        removecomment()
        exit(0)
        parser()
    except RuntimeError as emsg:
        # In output, show '\n' for newline
        lexeme = token.lexeme.replace('\n', '\\n')
        print(f"\nError on '{lexeme}' ' line {str(token.line)} ' column {str(token.column)}'")
        # Added the feature to enrigh Runtime Error message:
        # Show the line with a caret pointing to the token
        sourcesplit = source.split('\n')
        print(sourcesplit[token.line - 1])
        print(' ' * (token.column - 1) + '^')
        print(emsg)
        sys.exit(1)

main()