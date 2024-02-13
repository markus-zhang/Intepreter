#-------------------------------------------------------------#
#                                                             #
#                          tokenizer                          #
#                                                             #
#-------------------------------------------------------------#
from pyheader import *
import os

class tokenizer:
    def __init__(self, source:str, tokenlist:list):
        self.source = source
        self.tokenlist = tokenlist
        self.token = None
        self.line = 0
        self.column = 0
        self.prevchar = '\n'
        self.blankline = True
        self.sourceindex = 0
        self.indentstack = [1]
        self.trace = True
        self.dump_tokenizer = False
        self.token_dump_file = 'C:/Dev/Projects/Intepreter/src/pyint/token.dump'

    def getchar(self):
        # global sourceindex, column, line, prevchar, blankline

        # check if starting a new line
        if self.prevchar == '\n':
            self.line += 1
            self.column = 0
            # Reset blankline
            self.blankline = True

        # end of source code
        if self.sourceindex >= len(self.source):
            self.column = 1
            self.prevchar = ''
            # Return null str which signals end of source
            return ''
        
        c = self.source[self.sourceindex]
        self.sourceindex += 1
        self.column += 1
        # if c is not whitespace then the whole line is not blank
        if not c.isspace():
            self.blankline = False
        self.prevchar = c

        # if at end of blank line, return space in place of '\n'
        if c == '\n' and self.blankline:
            return ' '
        else:
            return c

    def peekchar(self):
        if self.sourceindex >= len(self.source) - 1:
            return ''
        else:
            return self.source[self.sourceindex]

    def run(self):
        cur_char = ' '
        prev_char = ' '

        while True:
            # skip whitespace but not newlines
            while cur_char != '\n' and cur_char.isspace():
                cur_char = self.getchar()

            self.token = Token(self.line, self.column, None, '')

            # Start of unsigned num?
            # UNSIGNEDNUM is a placeholder, eventually it is either an INTEGER or a FLOAT
            if cur_char.isdigit() or cur_char == '.':
                self.token.category = UNSIGNEDNUM
                flag_fp = False
                if cur_char == '.':
                    flag_fp = True
                while True:
                    self.token.lexeme += cur_char
                    cur_char = self.getchar()
                    if flag_fp:
                        if cur_char == '.':
                            raise RuntimeError("A numerical value cannot have two decimal points")
                        elif not cur_char.isdigit():
                            break
                    else:
                        if cur_char == '.':
                            flag_fp = True
                        elif not cur_char.isdigit():
                            break
                if flag_fp is False:
                    self.token.category = INTEGER
                else:
                    self.token.category = FLOAT

            # Start of name?
            elif cur_char.isalpha() or cur_char == '_':
                self.token.category = NAME
                while True:
                    self.token.lexeme += cur_char
                    cur_char = self.getchar()
                    if not (cur_char.isalnum() or cur_char == '_'):
                        break

                # Check if it belongs to keywords
                if self.token.lexeme in keywords:
                    self.token.category = keywords[self.token.lexeme]

            # Single line comment
            elif cur_char == '#':
                self.token.category = COMMENT_SINGLE
                while True:
                    self.token.lexeme += cur_char
                    cur_char = self.getchar()
                    if cur_char == '\n':
                        break

            # Not equal
            elif cur_char == '!':
                self.token.lexeme += cur_char
                next_char = self.peekchar()
                if next_char != '=':
                    raise RuntimeError("Expecting a '=' following '!'")
                else:
                    cur_char = self.getchar()
                    self.token.category = NOTEQUAL
                    self.token.lexeme += cur_char
                    cur_char = self.getchar()

            # ASSIGNOP (=) and EQUAL (==)
            elif cur_char == '=':
                self.token.lexeme += cur_char
                next_char = self.peekchar()
                if next_char != '=':
                    # Just a simple assignment operator
                    self.token.category = ASSIGNOP
                    cur_char = self.getchar()
                else:
                    # Now it's more interesting, an EQUAL!
                    cur_char = self.getchar()
                    self.token.category = EQUAL
                    self.token.lexeme += cur_char
                    cur_char = self.getchar()

            # Compound assignment such as += and /=
            elif cur_char in ['+', '-', '*', '/']:
                self.token.lexeme += cur_char
                next_char = self.peekchar()
                if next_char != '=':
                    # Just a simple arithmetic operator
                    self.token.category = smalltokens[cur_char]
                    cur_char = self.getchar()
                else:
                    # Should be a compound assignment operator
                    compound_type = cur_char
                    cur_char = self.getchar()
                    if compound_type == '+':
                        self.token.category = ADDASSIGN
                    elif compound_type == '-':
                        self.token.category = SUBASSIGN
                    elif compound_type == '*':
                        self.token.category = MULASSIGN
                    elif compound_type == '/':
                        self.token.category = DIVASSIGN
                    
                    self.token.lexeme += cur_char
                    cur_char = self.getchar()


            # LESSTHAN (<) and LESSEQUAL (<=)
            elif cur_char == '<':
                self.token.lexeme += cur_char
                next_char = self.peekchar()
                if next_char != '=':
                    # Just a simple less-than operator
                    self.token.category = LESSTHAN
                    cur_char = self.getchar()
                else:
                    # Now it's more interesting, a LESSEQUAL!
                    cur_char = self.getchar()
                    self.token.category = LESSEQUAL
                    self.token.lexeme += cur_char
                    cur_char = self.getchar()

            # GREATERTHAN (>) and GREATEREQUAL (>=)
            elif cur_char == '>':
                self.token.lexeme += cur_char
                next_char = self.peekchar()
                if next_char != '=':
                    # Just a simple less-than operator
                    self.token.category = GREATERTHAN
                    cur_char = self.getchar()
                else:
                    # Now it's more interesting, a LESSEQUAL!
                    cur_char = self.getchar()
                    self.token.category = GREATEREQUAL
                    self.token.lexeme += cur_char
                    cur_char = self.getchar()

            # Multiple line comment opening
            elif cur_char == '/':
                # We want to include / into the self.token before it moves to check *
                self.token.lexeme += cur_char
                # Peek, don't Get
                next_char = self.peekchar()
                if next_char != '*':
                    # Must be the division self.token
                    self.token.category = smalltokens[cur_char]
                    self.token.lexeme = cur_char
                    # Do not get a new char, we need to keep the current char
                    cur_char = self.getchar()
                else:
                    self.token.category = COMMENT_MULTIPLE
                    # Get ready for closing check, we must have */ combo
                    # But it must be a new *, not the one we already met
                    # So move cur_char first (here we don't care about prevchar)
                    cur_char = self.getchar()
                    while True:
                        self.token.lexeme += cur_char
                        prev_char = cur_char
                        cur_char = self.getchar()
                        # Multiple line comment closing
                        # We need to first check for / and then go back for *
                        # Because of edge cases such as /*******/
                        # if cur_char == '*':
                        if cur_char == '/' and prev_char == '*':
                            self.token.lexeme += cur_char
                            cur_char = self.getchar()
                            # Don't forget to move cur_char forward. Each block must do this
                            break 
            
            # The other small self.tokens such as +, -, *, etc.
            elif cur_char in smalltokens:
                self.token.category = smalltokens[cur_char]
                self.token.lexeme = cur_char
                cur_char = self.getchar()
            
            # Strings, we all love them. Only allow double quoted ones
            elif cur_char == '\'':       
                self.token.category = STRING
                # self.token.lexeme += cur_char
                cur_char = self.getchar()
                while True:
                    if cur_char == '\'':
                        # self.token.lexeme += cur_char
                        cur_char = self.getchar()
                        break
                    # Allow escape char
                    # Just read one more and move on
                    elif cur_char == '\\':
                        # self.token.lexeme += cur_char
                        # Next char is the one to be excaped
                        cur_char = self.getchar()
                        if cur_char == 'n':
                            self.token.lexeme += '\n'
                        elif cur_char == 't':
                            self.token.lexeme += '\t'
                        elif cur_char == '\\':
                            self.token.lexeme += '\\'
                        elif cur_char == 'b':
                            self.token.lexeme += '\b'
                        elif cur_char == '\'':
                            self.token.lexeme += "'"
                        else:
                            raise RuntimeError("Only allow escape chars: \\n, \\t, \\, \\b")
                        cur_char = self.getchar()
                    else:
                        self.token.lexeme += cur_char
                        cur_char = self.getchar()
            
            # Anything else is error
            else:
                self.token.category = ERROR
                self.token.lexeme = cur_char
                raise RuntimeError('Invalid self.token')
            
            """
            Check for indentations AFTER a NEWLINE has been appended
            Two cases: 
                1. the first line has leading spaces, so len(self.tokenlist) == 0
                2. the previous appended self.token is NEWLINE, and now we have a new self.token

            What do we do? Assuming we have indentstack as [1, 4, 7, 10].
            We check the column of the new self.token:
                - If it's indentstack[-1] < column, we append it, and add an INDENT self.token
                - If it's indentstack[-1] > column, we pop indentstack until we find one matching:
                    - For each indent in indentstack, if indent > column, pop and add a DEDENT self.token
                    - If indent == column, quit without popping it
                    - If indent < column, something is wrong, raise a RuntimeError
            """
            if len(self.tokenlist) == 0 or self.tokenlist[-1].category == NEWLINE:
                if self.indentstack[-1] < self.token.column:
                    # Append and add an INDENT
                    self.token_indent = Token(self.line, self.indentstack[-1], INDENT, '')
                    # The beauty is that INDENT is created afterwards but appended before the first "real" self.token of the line
                    self.tokenlist.append(self.token_indent)
                    self.indentstack.append(self.token.column)
                    if self.trace is True:
                        print(f"{str(self.token_indent.line)}   {str(self.token_indent.column)}    {catnames[self.token_indent.category]}   {str(self.token_indent.lexeme)}")
                else:
                    while True:
                        if self.indentstack[-1] == self.token.column:
                            # Do nothing, no change in indentation of dedentation
                            break
                        if self.indentstack[-1] > self.token.column:
                            # Pop and add a DEDENT
                            # Do NOT pollute the original self.token as it is not appended yet
                            # Same line as the following self.token(parsed but yet appended)
                            # I put column as 1 but this is not important

                            # Must pop first, otherwise DEDENT gets the wrong position plus indentstack will never be depleted as it has an initial element 1
                            self.indentstack.pop()
                            self.token_dedent = Token(self.line, self.indentstack[-1], DEDENT, '')
                            # The beauty is that DEDENT is created afterwards but appended before the first "real" self.token of the line
                            self.tokenlist.append(self.token_dedent)
                            if self.trace is True:
                                print(f"{str(self.token_dedent.line)}   {str(self.token_dedent.column)}    {catnames[self.token_dedent.category]}   {str(self.token_dedent.lexeme)}")
                            # self.indentstack.pop()
                        else:
                            raise RuntimeError(f"Incorrect dedentation {self.token.column} for {self.indentstack}")
            
            self.tokenlist.append(self.token)
            
            self.trace_print()

            if self.token.category == EOF:
                if self.trace is True:
                    self.traceall()
                    print(self.indentstack)
                break

    def trace_print(self):
        if self.trace is True:
            print(f"{str(self.token.line)}   {str(self.token.column)}    {catnames[self.token.category]}   {str(self.token.lexeme)}")

    def traceall(self):
        if self.trace is True:
            """
            Remove the existing file even if we don't need to dump
            """
            try:
                os.remove(self.token_dump_file)
            except OSError:
                pass
            print('Line Col Category            Lexeme\n')
            for self.token in self.tokenlist:
                if self.dump_tokenizer is False:
                    print(f"{str(self.token.line)}   {str(self.token.column)}    {catnames[self.token.category]}   {str(self.token.lexeme)}")
                else:
                    """
                    Then dump the content
                    """
                    try:
                        with open(self.token_dump_file, 'a') as file:
                            print(f"{str(self.token.line)}   {str(self.token.column)}    {catnames[self.token.category]}   {str(self.token.lexeme)}", file=file)
                    except Exception as e:
                        raise RuntimeError(e)
                    
    def removecomment(self):
        """Remove all comments from token list
        """
        index = 0
        while index < len(self.tokenlist):
            if self.tokenlist[index].category in [COMMENT_MULTIPLE, COMMENT_SINGLE]:
                self.tokenlist.pop(index)
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
                while self.tokenlist[index].category == NEWLINE:
                    self.tokenlist.pop(index)
            else:
                index += 1

    #TODO: Add the functionality of spitting out one token at a time
    def nexttoken(self):
        pass
    
    def dump(self):
        # In output, show '\n' for newline
        lexeme = self.token.lexeme.replace('\n', '\\n')
        print(f"\nError on '{lexeme}' ' line {str(self.token.line)} ' column {str(self.token.column)}'")
        # Added the feature to enrigh Runtime Error message:
        # Show the line with a caret pointing to the token
        sourcesplit = self.source.split('\n')
        print(sourcesplit[self.token.line - 1])
        print(' ' * (self.token.column - 1) + '^')