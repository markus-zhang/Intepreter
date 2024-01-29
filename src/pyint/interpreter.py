import sys
import os

class Token:
    def __init__(self, line, column, category, lexeme) -> None:
        self.line = line
        self.column = column
        self.category = category
        self.lexeme = lexeme

# Global Variables
# Section 1: Debugging and logging
trace = False           # Controls token trace
only_tokenizer = False   # If True, exit to OS after tokenizer
dump_tokenizer = True   # Should we dump the trace from the tokenizer into a local file?
token_dump_file = 'C:/Dev/Projects/Intepreter/src/pyint/token.dump'

# Section 2: Everything else
source = ''             # receives entire source program
sourceindex = 0         # index into source
line = 0                # current line number
column = 0              # current column number
tokenlist = []          # list of tokens to be consumed by parser
tokenindex = 0
prevchar = '\n'         # '\n' in prevchar signals start of new line
blankline = True        # Set to False if line is not blank
symboltable = {}        # Symbol Table for the interpreter
operandstack = []       # Use a list for the stack
# For indentation and dedentation
# Setup as column 1
indentstack = [1]
# For tracking parent loop indentations so that we can break out of it, see breakstat() and codeblock() for why
indentloop = []
flagloop = False
flagbreak = False
flagbreakloop = False

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
    'break':    BREAK
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

stmttokens = [PYIF, PYWHILE, PRINT, PYPASS, NAME, BREAK]

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

        # Start of unsigned int?
        if curchar.isdigit() or curchar == '.':
            token.category = UNSIGNEDNUM
            flag_fp = False
            if curchar == '.':
                flag_fp = True
            while True:
                token.lexeme += curchar
                curchar = getchar()
                if flag_fp:
                    if curchar == '.':
                        raise RuntimeError("A numerical value cannot have two decimal points")
                    elif not curchar.isdigit():
                        break
                else:
                    if curchar == '.':
                        flag_fp = True
                    elif not curchar.isdigit():
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

        # Compound assignment such as += and /=
        elif curchar in ['+', '-', '*', '/']:
            token.lexeme += curchar
            nextchar = peekchar()
            if nextchar != '=':
                # Just a simple arithmetic operator
                token.category = smalltokens[curchar]
                curchar = getchar()
            else:
                # Should be a compound assignment operator
                compound_type = curchar
                curchar = getchar()
                if compound_type == '+':
                    token.category = ADDASSIGN
                elif compound_type == '-':
                    token.category = SUBASSIGN
                elif compound_type == '*':
                    token.category = MULASSIGN
                elif compound_type == '/':
                    token.category = DIVASSIGN
                
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
                    elif curchar == '\'':
                        token.lexeme += "'"
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
                if trace is True:
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
                        if trace is True:
                            print(f"{str(token_dedent.line)}   {str(token_dedent.column)}    {catnames[token_dedent.category]}   {str(token_dedent.lexeme)}")
                        indentstack.pop()
                    else:
                        raise RuntimeError(f"Incorrect dedentation {token.column} for {indentstack}")
        
        tokenlist.append(token)
        
        trace_print()

        if token.category == EOF:
            if trace is True:
                traceall()
                print(indentstack)
            break

def trace_print():
    if trace is True:
        print(f"{str(token.line)}   {str(token.column)}    {catnames[token.category]}   {str(token.lexeme)}")

def traceall():
    if trace is True:
        """
        Remove the existing file even if we don't need to dump
        """
        try:
            os.remove(token_dump_file)
        except OSError:
            pass
        for token in tokenlist:
            if dump_tokenizer is False:
                print(f"{str(token.line)}   {str(token.column)}    {catnames[token.category]}   {str(token.lexeme)}")
            else:
                """
                Then dump the content
                """
                try:
                    with open(token_dump_file, 'a') as file:
                        print(f"{str(token.line)}   {str(token.column)}    {catnames[token.category]}   {str(token.lexeme)}", file=file)
                except Exception as e:
                    raise RuntimeError(e)

def removecomment():
    """Remove all comments from token list
    """
    global tokenlist
    index = 0
    while index < len(tokenlist):
        if tokenlist[index].category in [COMMENT_MULTIPLE, COMMENT_SINGLE]:
            tokenlist.pop(index)
            # If the next token is a NEWLINE, should also remove it. Imagine this piece of code snippet:
            """
            while count < number:
                # Nested while loop
                while flag == 'yes':
            
            The token stream after the first colon looks like this:
            <NEWLINE> <INDENT> <COMMENT_SINGLE> <NEWLINE> <IFWHILE> ...
            So if we remove the comment, it looks like:
            <NEWLINE> <INDENT> <NEWLINE> <IFWHILE> ...

            Now this is inside a codeblock, which correctly consumes the first <NEWLINE>, the <INDENT> following, but then checking whether the next token is in [PRINT, NAME, PYPASS, PYIF, PYWHILE, BREAK], and if not it goes forward to consume <DEDENT>.

            This is going to raise a RuntimeError in our case as our next token is <NEWLINE>
            """
            while tokenlist[index].category == NEWLINE:
                tokenlist.pop(index)
        else:
            index += 1


# Parser code
# Note that parser should be called after tokenizer
# Each line of the following CFG is a rule (a Python function)
###############################################################
# <program>         -> <stmt>* EOF
# <stmt>            -> <simplestmt> NEWLINE
# <stmt>            -> <compoundstmt>
# <simplestmt>      -> <printstmt>
# <simplestmt>      -> <assignmentstmt>
# <simplestmt>      -> <passstmt>
# <simplestmt>      -> <breakstmt>
# <compoundstmt>    -> <whilestmt>
# <compoundstmt>    -> <ifstmt>
"""
<printstmt> needs to successfully parse the following:
print()
print(abc)
print(abc, dr, fe)
print(abc, dr, fe,) # Last comma should be accepted but ignored
"""
# <printstmt>       -> 'print' '(' [ <relexpr> (',' <relexpr>)* [ ',' ]] ')'
# <assignmentstmt>  -> NAME '=' <relexpr>
# <assignmentstmt>  -> NAME '+=' <relexpr>
# <assignmentstmt>  -> NAME '-=' <relexpr>
# <assignmentstmt>  -> NAME '*=' <relexpr>
# <assignmentstmt>  -> NAME '/=' <relexpr>
# <passstmt>        -> 'pass'
# <breakstmt>       -> 'break'
# <whilestmt>       -> 'while' <relexpr> ':' <codeblock>
# <ifstmt>          -> 'if' <relexpr> ':' <codeblock> ('elif' <relexpr> ':' <codeblock>)* ['else' ':' <codeblock>]
"""
<codeblock> is not recursive, because it is not neccesarily true that every line in a while/if block needs an indent-dedent:
- Nested:
# Every line is wrapped in an indent-dedent
while a < b:
    if b == c:
        # do something could be a simple print()
        do something
- Not nested:
while a < b:
    # do something could be a simple print()
    do something
    # no indent-dedent
    do something else
"""
# <codeblock>       -> <NEWLINE> 'INDENT' <stmt>+ 'DEDENT'
# <relexpr>         -> <expr> [ ('<' | '<=' | '==' | '!=' | '>=' | '>') <expr>]
# <expr>            -> <term> ('+' <term>)*
# <expr>            -> <term> ('-' <term>)*
# <term>            -> <factor> ('*' <factor>)*
# <term>            -> <factor> ('/' <factor>)*
# <term>            -> <factor> ('%' <factor>)*
# <factor>          -> '+' <factor>
# <factor>          -> '-' <factor>
# <factor>          -> NAME
# <factor>          -> UNSIGNEDNUM
# <factor>          -> STRING
# <factor>          -> 'True'
# <factor>          -> 'False'
# <factor>          -> 'None'
# <factor>          -> '(' <relexpr> ')'
###############################################################
def program():
    # <program>         -> <stmt>* EOF
    # We must skip leading newlines, otherwise the while loop does not do anything and the next expecting token is EOF, which is not we want usually.
    while token.category == NEWLINE:
        advance()
    while token.category in stmttokens:
        stmt()
    consume(EOF)

def stmt():
    # <stmt>            -> <simplestmt> NEWLINE+
    # <stmt>            -> <compoundstmt>
    if token.category in [PRINT, NAME, PYPASS, BREAK]:
        simplestmt()
        while token.category == NEWLINE:
            consume(NEWLINE)
    elif token.category in [PYIF, PYWHILE]:
        compoundstmt()
    else:
        raise RuntimeError(f"Expecting print, a name, pass, if, while, but get {token.category}")

def simplestmt():
    # <simplestmt>      -> <printstmt>
    # <simplestmt>      -> <assignmentstmt>
    # <simplestmt>      -> <passstmt>
    if token.category == PRINT:
        printstmt()
    elif token.category == NAME:
        assignmentstmt()
    elif token.category == PYPASS:
        passstmt()
    elif token.category == BREAK:
        breakstmt()
    else:
        raise RuntimeError("Expecting PRINT, NAME, PYPASS or BREAK") 
    
def printstmt():
    # <printstmt>       -> 'print' '(' [ <relexpr> (',' <relexpr>)* [ ',' ]] ')'
    # We already know the first token must be 'print' so no need to check
    advance()
    consume(LEFTPAREN)
    if token.category != RIGHTPAREN:
        # Must have a <relexpr>
        relexpr()
        print(operandstack.pop(), end=' ')
        # Is there a comma?
        while token.category == COMMA:
            advance()
            # Is this the last comma before ')'?
            if token.category == RIGHTPAREN:
                break
            else:
                # Should be another relexpr
                relexpr()
                print(operandstack.pop(), end=' ')
    consume(RIGHTPAREN)
    print()
    """
    if token.category == RIGHTPAREN:
        # Case 0: print()
        print()
        advance()
    else:
        # Must have at least one <relexpr>
        relexpr()
        print(operandstack.pop())
        # Case 1: print('blah')
        if token.category == RIGHTPAREN:
            # Done
            advance()
            return
        while token.category == COMMA:
            advance()
            # Case 3: print(1, 2, 'Blah',)
            if token.category == RIGHTPAREN:
                # Done
                advance()
                break
            else:
                relexpr()
                print(operandstack.pop())
        # Case 2: print(1, 2, 'Blah')
        if token.category == RIGHTPAREN:
            # Done, print(1, 2, 'Blah')
            advance()
    # expr()  # Expect expr() to push the result onto the top of the operand stack
    # consume(RIGHTPAREN)
    """

def assignmentstmt():
    # <assignmentstmt>  -> NAME '=' <relexpr>
    # <assignmentstmt>  -> NAME '+=' <relexpr>
    # <assignmentstmt>  -> NAME '-=' <relexpr>
    # <assignmentstmt>  -> NAME '*=' <relexpr>
    # <assignmentstmt>  -> NAME '/=' <relexpr>
    # We already know the first token must be NAME so no need to check
    # Pick up the token as symbol
    left = token.lexeme
    advance()

    if token.category == ASSIGNOP:
        consume(ASSIGNOP)
        relexpr()
        # expr() pushes onto top of the operand stack, update symbol table
        # global symboltable
        symboltable[left] = operandstack.pop()
    elif token.category in [ADDASSIGN, SUBASSIGN, MULASSIGN, DIVASSIGN]:
        compound_assign_op = token
        advance()   # No need to check again
        relexpr()
        if compound_assign_op.category == ADDASSIGN:
            symboltable[left] = symboltable[left] + operandstack.pop()
        elif compound_assign_op.category == SUBASSIGN:
            symboltable[left] = symboltable[left] - operandstack.pop()
        elif compound_assign_op.category == MULASSIGN:
            symboltable[left] = symboltable[left] * operandstack.pop()
        elif compound_assign_op.category == DIVASSIGN:
            symboltable[left] = symboltable[left] / operandstack.pop()
        

def passstmt():
    advance()

def breakstmt():
    """
    1) if not in a loop, do nothing (check loopindex);
    2) if in a loop, just skip everything in the path until the column of the token matches loopindex[-1], which means we are getting out of the most inner loop. Don't forget to do loopindex.pop(). 
    3) Don't forget to signal "breakout" to caller which should be stmt()
    """
    if len(indentloop) == 0:
        # Only allow in loop
        raise RuntimeError("Only allow break in a loop")
        # return
    while True:
        advance()
        # DEDENT/INDENT sometimes occupy the first column so need to rule it out
        # Also, we might not see token.column == indentloop[-1] if the while loop we break out is NOT the only loop, consider the following: when we break out of the inner loop, the "else" has a column value of 5, which is smaller than the column value of the "while" (9) we just break out from.
        """
        while a < 10:
            print(a)
            if a == 5:
                while a < 50:
                    a = a + 10
                    print(a)
                    if a >= 30:
                        break
            else:
                a = a + 1
        """
        if token.column <= indentloop[-1] and token.category not in [DEDENT, INDENT]:
            if token.category == EOF:
                # Edge case when there is no need to return to caller stmt()
                exit(0)
            indentloop.pop()
            global flagbreak
            flagbreak = True
            break


def compoundstmt():
    # <compoundstmt>    -> <whilestmt>
    # <compoundstmt>    -> <ifstmt>
    if token.category == PYIF:
        ifstmt()
    elif token.category == PYWHILE:
        whilestmt()

def ifstmt():
    # <ifstmt>          -> 'if' <relexpr> ':' <codeblock> ('elif' <relexpr> ':' <codeblock>)* ['else' ':' <codeblock>]
    consume(PYIF)
    relexpr()
    condition = operandstack.pop()
    consume(COLON)
    """
    if condition is True then execute codeblock()
    But what to do if condition is False?
    We should track INDENT - DEDENT pairs
    """
    if condition is True:
        codeblock()
        """
        In case codeblock() encounters a "break", the "break" statement should be able to figure out the next token to execute. We should immediately return from whilestmt (and its children statements)
        """
        if flagbreak is True:
            return
    else:
        # Skip over until all pairs of INDENT-DEDENT are passed
        # codeblock() runs pass the indent-dedent block, but if we choose not to execute codeblock(), we need to implement this functionality by our own
        indent_tracker = 0
        indent_start = False
        while True:
            if token.category == INDENT:
                indent_tracker += 1
                indent_start = True
            elif token.category == DEDENT:
                indent_tracker -= 1
            if indent_tracker == 0 and indent_start is True:
                # We got all those indent-dedent pairs
                # Next token should be a statement or something close
                # Don't forget to advance() from the DEDENT
                advance()
                break
            advance()
    # Now that we skipped the codeblock of "if", we should expect either "else" or "elif", or something else which means that the "if" has no "else" nor "elif". We can also have multiple "elif"s so a loop is good for this kind of stuffs (or recursively function call)
    # Hacky way to tell the "else" block that some "elif" got executed
    elif_executed = False
    while token.category == PYELIF:
        advance()
        relexpr()
        condition_elif = operandstack.pop()
        consume(COLON)

        # We need to make sure that the if condition is False
        # Otherwise this will be falsely triggered if the if condition is True and the elif condition is also True
        # This is rare but still can happen (think counter == 0 and counter % 2 == 0 can be both true)
        if condition_elif is True and condition is False:
            if elif_executed is False:
                elif_executed = True
            codeblock()
            if flagbreak is True:
                return
        else:
            # Skip over until all pairs of INDENT-DEDENT are passed
            # codeblock() runs pass the indent-dedent block, but if we choose not to execute codeblock(), we need to implement this functionality by our own
            indent_tracker = 0
            indent_start = False
            while True:
                if token.category == INDENT:
                    indent_tracker += 1
                    indent_start = True
                elif token.category == DEDENT:
                    indent_tracker -= 1
                if indent_tracker == 0 and indent_start is True:
                    # We got all those indent-dedent pairs
                    # Next token should be a statement or something close
                    # Don't forget to advance() from the DEDENT
                    advance()
                    break
                advance()
    if token.category == PYELSE:
        advance()
        consume(COLON)
        # if either condition is True, we need to skip this part as ELSE won't be executed
        if condition is False and elif_executed is False:
            codeblock()
        else:
            # codeblock() runs pass the indent-dedent block, but if we choose not to execute codeblock(), we need to implement this functionality by our own
            indent_tracker = 0
            indent_start = False
            while True:
                if token.category == INDENT:
                    indent_tracker += 1
                    indent_start = True
                elif token.category == DEDENT:
                    indent_tracker -= 1
                if indent_tracker == 0 and indent_start is True:
                    # We got all those indent-dedent pairs
                    # Next token should be a statement or something close
                    # Don't forget to advance() from the DEDENT
                    advance()
                    break
                advance()

def whilestmt():
    # <whilestmt>       -> 'while' <relexpr> ':' <codeblock>
    """
    Consider the following code:

    i = 0
    while i < 10:
        print(i)
        i += 1
    
    It's easy: we check the <relexpr> for each loop and if the top of the stack is a False then we can skip everything else, as we did in the if statement
    """
    # Push indent of each while loop so that a "break" can get us out of it
    # Don't forget to manually pop once the loop is done, or "break" gets us out of it
    global indentloop, token
    indentloop.append(token.column)
    if trace is True:
        print(f"Loop: {indentloop}")

    consume(PYWHILE)
    # Record the position of the first token after "while" so that we can jump back
    global tokenindex
    relexpr_pos = tokenindex
    while True:
        relexpr()
        condition = operandstack.pop()
        consume(COLON)
        if condition is True:
            codeblock()
            """
            In case codeblock() encounters a "break", the "break" statement should be able to figure out the next token to execute. We should immediately return from whilestmt (and its children statements)
            """
            global flagbreak
            if flagbreak is True:
                # Since we only allow break in while loop, this should be the caller function that should reset flagbreak
                # TODO: Logic above is wrong, we need to figure out how to set flagbreak to False at the proper level. The fllowing is WRONG.
                # flagbreak = False
                # To flag that I just break out from the correct while loop, my caller should set both flags to false
                global flagbreakloop
                flagbreakloop = True
                return
            else:
                tokenindex = relexpr_pos
                # Manually move the token
                # global token
                token = tokenlist[tokenindex]
        else:
            # as in if, we need to skip the indent-dedent block
            indent_tracker = 0
            indent_start = False
            while True:
                if token.category == INDENT:
                    indent_tracker += 1
                    indent_start = True
                elif token.category == DEDENT:
                    indent_tracker -= 1
                if indent_tracker == 0 and indent_start is True:
                    # We got all those indent-dedent pairs
                    # Next token should be a statement or something close
                    # Don't forget to advance() from the DEDENT
                    advance()
                    # return instead of break as we are inside of double while loop
                    # Don't forget to pop the indentloop stack as no "break" is run
                    indentloop.pop()
                    return
                advance()

def codeblock():
    # <codeblock>       -> <NEWLINE> 'INDENT' <stmt>+ 'DEDENT'
    """
    Each codeblock() takes care of its own DEDENT. This is super important. Consider the following code:

    a = 2
    if a < 2:
        if a >= 1:
            print(3)
        else:
            print(2)
    
    We should expect two DEDENTs at the end before EOF. If neither of the codeblocks consumes the DEDENT, then the nested "if" branch (becuase a = 2 >= 1 so it gets executed instead of the "else") would have to skip both DEDENTs. However, this "if" has no idea how deep it itself is buried in -- how does it know how many DEDENTs to skip, unless we track the DEDENTs manually? This is too much work comparing to just asking the codeblocks to take care of their own INDENT-DEDENT pairs
    """
    # In general there is exactly one <NEWLINE> to be consumes
    # However there are cases with multiple <NEWLINE>s and 0 <NEWLINE> -- the second case results from comments and their following <NEWLINE>s been removed from the token list
    while token.category == NEWLINE:
        consume(NEWLINE)
    consume(INDENT)
    while token.category in [PRINT, NAME, PYPASS, PYIF, PYWHILE, BREAK]:
        stmt()
        """
        In case codeblock() encounters a "flagbreak" signal, this means we are breaking out. If the other signal "flagbreakloop" is also True, this means we are already out of the while loop we want to break out, so we should reset the two flags.

        Why do we need the second flag "flagbreakloop"? If we don't have it, we will have no way to know whether we have broken out of the correct while loop, so we don't know where to reset flagbreak properly. Consider a very nested if-codeblock inside of a while loop, we need to skip the consume(DEDENT) command arbitrarily times - only by setting a second flag do we know when we should we skip it or not.
        """
        global flagbreak, flagbreakloop
        """
        NOTE: This is super important. The following code says, ONLY return if flagbreak is TRUE and flagbreakloop is False, why? Consider the scenario (See test4.in): 
        1) When we are in the MIDDLE of the return "chain" triggered by a break, we need to return from codeblock(), why? Because we want to find the top loop that pairs with the break statement
        2) When we are already out of the return "chain", and if we still have more statements in the parent codeblock that contains the loop that we just broke out, we do NOT want to return, because there are other statements to be executed after the loop
        """
        if flagbreak is True:
            if flagbreakloop is True:
                flagbreak = False
                flagbreakloop = False
            else:
                return
    consume(DEDENT)

def relexpr():
    # <relexpr>         -> <expr> [ ('<' | '<=' | '==' | '!=' | '>=' | '>') <expr>]
    expr()
    if token.category in [LESSTHAN, LESSEQUAL, EQUAL, NOTEQUAL, GREATEREQUAL, GREATERTHAN]:
        # Only pop when there is a comparison operator following left side
        # Consider this:
        # a = 2
        # If we pop immediately after the previous expr(), without checking whether there is a comparison operator after a, then a would be popped in relexpr(), while in assignmentstat() we will have to pop() again, which causes error
        left = operandstack.pop()
        # Save operator token
        token_op = token
        advance()
        expr()
        right = operandstack.pop()
        if token_op.category == LESSTHAN:
            operandstack.append(left < right)
        elif token_op.category == LESSEQUAL:
            operandstack.append(left <= right)
        elif token_op.category == EQUAL:
            operandstack.append(left == right)
        elif token_op.category == NOTEQUAL:
            operandstack.append(left != right)
        elif token_op.category == GREATEREQUAL:
            operandstack.append(left >= right)
        elif token_op.category == GREATERTHAN:
            operandstack.append(left > right)

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
    # <term>            -> <factor> ('%' <factor>)*
    factor()
    while token.category in [TIMES, DIVISION, MODULO]:
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
        elif optoken.category == DIVISION:
            operandstack.append(left / right)
        elif optoken.category == MODULO:
            operandstack.append(left % right)

def factor():
    # <factor>          -> '+' <factor>
    # <factor>          -> '-' <factor>
    # <factor>          -> NAME
    # <factor>          -> UNSIGNEDNUM
    # <factor>          -> STRING
    # <factor>          -> 'True'
    # <factor>          -> 'False'
    # <factor>          -> 'None'
    # <factor>          -> '(' <relexpr> ')'
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
    elif token.category == UNSIGNEDNUM:
        operandstack.append(float(token.lexeme))
        advance()
    elif token.category == STRING:
        operandstack.append(token.lexeme)
        advance()
    elif token.category == PYTRUE:
        operandstack.append(True)
        advance()
    elif token.category == PYFALSE:
        operandstack.append(False)
        advance()
    elif token.category == PYNONE:
        operandstack.append(None)
        advance()
    elif token.category == LEFTPAREN:
        advance()
        relexpr()
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
    if trace is True:
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
        if only_tokenizer == True:
            exit()
        removecomment()
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