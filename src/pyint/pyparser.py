#-------------------------------------------------------------#
#                                                             #
#                           parser                            #
#                                                             #
#-------------------------------------------------------------#

# Each line of the following CFG is a rule (a Python function)
###############################################################
# <program>         -> <stmt>* EOF
# <stmt>            -> <simplestmt> NEWLINE
# <stmt>            -> <compoundstmt>
# <simplestmt>      -> <printstmt>
# <simplestmt>      -> <assignmentstmt>
# <simplestmt>      -> <passstmt>
# <simplestmt>      -> <breakstmt>
# <simplestmt>      -> <globalstmt>
# <simplestmt>      -> <returnstmt>
# <simplestmt>      -> <functioncallstmt>
# <compoundstmt>    -> <whilestmt>
# <compoundstmt>    -> <ifstmt>
# <compoundstmt>    -> <defstmt> 
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
# <globalstmt>      -> 'global' NAME(',' NAME)*
# <returnstmt>      -> 'return' [<relexpr>]
# Q: For <functioncallstmt>, why is NAME'(' [<relexpr>] (',' <relexpr>)* ')' wrong? Because this would allow formats such as foo(,12) which is wrong
# <functioncallstmt>-> NAME'(' [<relexpr> (',' <relexpr>)*] ')'
# <whilestmt>       -> 'while' <relexpr> ':' <codeblock>
# <ifstmt>          -> 'if' <relexpr> ':' <codeblock> ('elif' <relexpr> ':' <codeblock>)* ['else' ':' <codeblock>]
# <defstmt>         -> 'def' NAME '(' [NAME (, NAME)*] ')'':' <codeblock>
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
# <relexpr>         -> <expr> [ ('<' | '<=' | '==' | '!=' | '>=' | '>') <expr>]*
# <expr>            -> <term> ('+' <term>)*
# <expr>            -> <term> ('-' <term>)*
# <term>            -> <factor> ('*' <factor>)*
# <term>            -> <factor> ('/' <factor>)*
# <term>            -> <factor> ('%' <factor>)*
# <factor>          -> '+' <factor>
# <factor>          -> '-' <factor>
# <factor>          -> NAME
# <factor>          -> INTEGER
# <factor>          -> FLOAT
# <factor>          -> STRING
# <factor>          -> 'True'
# <factor>          -> 'False'
# <factor>          -> 'None'
# <factor>          -> '(' <relexpr> ')'
###############################################################

from pyheader import *
from type import is_operatable

class pyparser:
    def __init__(self, tokenlist:list):
        self.tokenlist = tokenlist
        self.trace = False
        self.token = None
        self.tokenindex = 0
        self.operandstack = []

        # We need to split the symbol table into two: local and global
        self.localsymboltable = {}
        self.localsymboltablebackup = {}     # This is for function call within function call, basically this is for the caller scope while localsymboltable is for callee scope
        self.globalsymboltable = {}
        # OK now we have two symbol tables, which one do we store into/load from?
        # We track function call depth, 0 means global, positive means local, and negative means we made some mistakes in tracking
        self.functioncalldepth = 0
        # If some variables are declared global using the "global" keyword, put into this set so that we know
        self.globalvardeclared:set = set()
        # For return addresses, since function calls can be chained, a stack is the natural solution
        self.returnaddrstack = []

        # For tracking parent loop indentations so that we can break out of it, see breakstat() and codeblock() for why
        self.indentloop = []
        self.flagloop = False
        self.flagbreak = False
        self.flagbreakloop = False
    
    def parse(self):
        self.token = self.tokenlist[0]
        self.program()
        if self.trace is True:
            print("End of parsing")

    def advance(self):
        """Advance the reading of a token from tokenlist.
        The variable "token" always contain the current token
        """
        # Move to next token
        self.tokenindex += 1     
        if self.tokenindex >= len(self.tokenlist):
            # I assume the script ends gracefully once encounters an EOF token
            raise RuntimeError("Unexpected end of file")    
        self.token = self.tokenlist[self.tokenindex]

    def consume(self, expectedcat: int):
        """Consumes the expected category.
        Assuming we see a "print" token, we should expect a left parenthesis token immediately
        """
        if self.token.category != expectedcat:
            raise RuntimeError(f"Expecting {catnames[expectedcat]} but get {catnames[self.token.category]}")
        elif self.token.category == EOF:
            # We are done
            return
        else:
            self.advance()

    def program(self):
        # <program>         -> <stmt>* EOF
        # We must skip leading newlines, otherwise the while loop does not do anything and the next expecting token is EOF, which is not we want usually.
        while self.token.category == NEWLINE:
            self.advance()
        while self.token.category in stmttokens:
            self.stmt()
        self.consume(EOF)

    def stmt(self):
        # <stmt>            -> <simplestmt> NEWLINE+
        # <stmt>            -> <compoundstmt>
        if self.token.category in [PRINT, NAME, PYPASS, BREAK, GLOBAL, RETURN]:
            self.simplestmt()
            while self.token.category == NEWLINE:
                self.consume(NEWLINE)
        elif self.token.category in [PYIF, PYWHILE, DEF]:
            self.compoundstmt()
        else:
            raise RuntimeError(f"Expecting print, a name, pass, if, while, but get {self.token.category}")
        
    def simplestmt(self):
        # <simplestmt>      -> <printstmt>
        # <simplestmt>      -> <assignmentstmt>
        # <simplestmt>      -> <passstmt>
        # <simplestmt>      -> <breakstmt>
        # <simplestmt>      -> <globalstmt>
        # <simplestmt>      -> <returnstmt>
        # <simplestmt>      -> <functioncallstmt>
        if self.token.category == PRINT:
            self.printstmt()
        elif self.token.category == NAME:
            # could be assignment, or function call
            token_next = self.tokenlist[self.tokenindex + 1]
            if token_next.category == LEFTPAREN:
                self.functioncallstmt()
            else:
                self.assignmentstmt()
        elif self.token.category == PYPASS:
            self.passstmt()
        elif self.token.category == BREAK:
            self.breakstmt()
        elif self.token.category == GLOBAL:
            self.globalstmt()
        elif self.token.category == RETURN:
            self.returnstmt()
        else:
            raise RuntimeError("Expecting PRINT, NAME, PYPASS, BREAK, GLOBAL, RETURN and FUNCTION CALL") 
    
    def printstmt(self):
    # <printstmt>       -> 'print' '(' [ <relexpr> (',' <relexpr>)* [ ',' ]] ')'
        self.advance()
        self.consume(LEFTPAREN)
        if self.token.category != RIGHTPAREN:
            # Must have a <relexpr>
            self.relexpr()
            print(self.operandstack.pop(), end=' ')
            # Is there a comma?
            while self.token.category == COMMA:
                self.advance()
                # Is this the last comma before ')'?
                if self.token.category == RIGHTPAREN:
                    break
                else:
                    # Should be another relexpr
                    self.relexpr()
                    print(self.operandstack.pop(), end=' ')
        self.consume(RIGHTPAREN)
        print()

    def assignmentstmt(self):
        # <assignmentstmt>  -> NAME '=' <relexpr>
        # <assignmentstmt>  -> NAME '+=' <relexpr>
        # <assignmentstmt>  -> NAME '-=' <relexpr>
        # <assignmentstmt>  -> NAME '*=' <relexpr>
        # <assignmentstmt>  -> NAME '/=' <relexpr>
        """
        It is a lot more complicated when function call is being implemented.
        1. Check globalvardeclared, if it's within then we are in global, AND we should already have this variable defined.
            - We then proceed to check whether it exists, if not we raise.
        2. Check functioncalldepth, if it's 0 then we are in global
        """
        intermediate = None
        left = self.token.lexeme
        self.advance()

        if self.token.category == ASSIGNOP:
            self.consume(ASSIGNOP)
            self.relexpr()
            # expr() pushes onto top of the operand stack, update symbol table
            intermediate = self.operandstack.pop()
            # NOTE: Assign intermediate to proper symbol
            if left in self.globalvardeclared or self.functioncalldepth == 0:
                try:
                    self.globalsymboltable[left] = intermediate
                except KeyError:
                    raise RuntimeError(f"NAME {left} is declared as global but not defined in global scope")
            else:
                # Then it must be in local scope, even if not found - in that case we will create a new entry
                self.localsymboltable[left] = intermediate
        elif self.token.category in [ADDASSIGN, SUBASSIGN, MULASSIGN, DIVASSIGN]:
            compound_assign_op:Token = self.token
            self.advance()   # No need to check again
            self.relexpr()
            # Added type checking
            operand_right = self.operandstack.pop()
            # NOTE: Switch symboltable to one of the other two symbol tables
            # TODO: We do not need intermediate. Since we are using symbol_table_left to point to the correct symbol table
            symbol_table_left = None
            if left in self.globalvardeclared or self.functioncalldepth == 0:
                if left in self.globalsymboltable:
                    symbol_table_left = self.globalsymboltable
                else:
                    raise RuntimeError(f"NAME {left} is declared in the global scope but is not present")
            else:
                if left not in self.localsymboltable:
                    raise RuntimeError(f"NAME {left} is not present in the local scope ")
                symbol_table_left = self.localsymboltable
            
            left_type = type(symbol_table_left[left]).__name__
            right_type = type(operand_right).__name__
            if compound_assign_op.category == ADDASSIGN:
                if is_operatable(operator=ADDASSIGN, left_type=left_type, right_type=right_type):
                    symbol_table_left[left] = symbol_table_left[left] + operand_right
                    if left_type == 'int' and right_type == 'int':
                        symbol_table_left[left] = int(symbol_table_left[left])
                else:
                    raise RuntimeError(f"It is illegal to perform {left_type} {smalltokens[ADDASSIGN]} {right_type}")
            elif compound_assign_op.category == SUBASSIGN:
                if is_operatable(operator=SUBASSIGN, left_type=left_type, right_type=right_type):
                    symbol_table_left[left] = symbol_table_left[left] - operand_right
                else:
                    raise RuntimeError(f"It is illegal to perform {left_type} {smalltokens[SUBASSIGN]} {right_type}")
            elif compound_assign_op.category == MULASSIGN:
                if is_operatable(operator=MULASSIGN, left_type=left_type, right_type=right_type):
                    symbol_table_left[left] = symbol_table_left[left] * operand_right
                else:
                    raise RuntimeError(f"It is illegal to perform {left_type} {smalltokens[MULASSIGN]} {right_type}")
            elif compound_assign_op.category == DIVASSIGN:
                if is_operatable(operator=DIVASSIGN, left_type=left_type, right_type=right_type):
                    symbol_table_left[left] = symbol_table_left[left] / operand_right
                else:
                    raise RuntimeError(f"It is illegal to perform {left_type} {smalltokens[DIVASSIGN]} {right_type}")
                
    def passstmt(self):
        # <passstmt>        -> 'pass'
        self.advance()

    def breakstmt(self):
        # <breakstmt>       -> 'break'
        """
        1) if not in a loop, do nothing (check loopindex);
        2) if in a loop, just skip everything in the path until the column of the token matches loopindex[-1], which means we are getting out of the most inner loop. Don't forget to do loopindex.pop(). 
        3) Don't forget to signal "breakout" to caller which should be stmt()
        """
        if len(self.indentloop) == 0:
            # Only allow in loop
            raise RuntimeError("Only allow break in a loop")
        while True:
            self.advance()
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
            if self.token.column <= self.indentloop[-1] and self.token.category not in [INDENT, DEDENT]:
                if self.token.category == EOF:
                    # Edge case when there is no need to return to caller stmt()
                    exit(0)
                self.indentloop.pop()
                self.flagbreak = True
                break

    def globalstmt(self):
        # <globalstmt>      -> 'global' NAME(',' NAME)*
        # If we are already in global scope then we don't need it
        if self.functioncalldepth == 0:
            raise RuntimeError(f"'global' keyboard can only be used within functions.")
        
        self.advance()
        """
        We need to check whether those names were in globalsymboltable dict, and if yes, push into globalvartuple set
        """
        while True:
            symbol_name = self.token.lexeme
            if symbol_name in self.globalsymboltable:
                self.globalvardeclared.add(symbol_name)
            else:
                raise RuntimeError(f"The variable {symbol_name} has not been defined.")
            
            self.advance()
            # Is it a comma? If so then there are more symboles to be added
            if self.token.lexeme == ',':
                self.advance()
            else:
                break
            

        # Please note that the function caller need to clear globalvartuple for next use


    def returnstmt(self):
        # TODO: Complete implementation of return statement
        pass

    def functioncallstmt(self):
        # <functioncallstmt>-> NAME'(' [<relexpr> (',' <relexpr>)*] ')'
        """
        1. Locate the function in globalsymboltable
        2. Save the return address into returnaddressstack
        2. Duplicate the localsymboltable to localsymboltablebackup
        3. Populate the parameter field if applicable
            - Also populate the new localsymboltable
            - Raise error if more/less parameters are given
        4. Jump to the tokenindex of the function body
        5. Execute the function body (maybe use another function "functioncallcodeblock()")
        6. Cleanup after return
        """
        function_name = self.token.lexeme
        # Step 1: Check whether it is in global symbol table
        if function_name not in self.globalsymboltable:
            raise RuntimeError(f"Function {function_name} has not been defined yet")
        
        # Step 2: Backup local symbol table and clear the original one
        self.localsymboltablebackup = self.localsymboltable
        self.localsymboltable = {}

        # Step 3: Populate the parameter field
        """
        In globalsymboltable, each function takes the format of:
        "foo":{
            "parameters": ["a", "b", "c"],
            "entry":23
        }
        """
        self.advance()
        self.consume(LEFTPAREN)

        counter = 0
        parameter_num = len(self.globalsymboltable[function_name]["parameters"])
        while True:
            if self.token.category == RIGHTPAREN:
                break
            else:
                self.relexpr()
                # This basically says, in local symbol table, 'a': some value
                if counter >= parameter_num:
                    raise RuntimeError(f"Function {function_name} accepts {parameter_num} parameters but gets {counter}")
                
                self.localsymboltable[self.globalsymboltable[function_name]["parameters"][counter]] = self.operandstack.pop()
                counter += 1
                if self.token.category == COMMA:
                    self.advance()
        # Right now we don't accept default value for parameters so the numbers must match: for 3 parameters we must pass 3 values
        if counter < parameter_num - 1:
            raise RuntimeError(f"Function {function_name} accepts {parameter_num} parameters but gets {counter}")
        
        self.consume(RIGHTPAREN)

        # Step 4: Save the return address
        self.returnaddrstack.append(self.tokenindex)

        # Step 4: Jump to the entry token of the function
        self.tokenindex = self.globalsymboltable[function_name]["entry"]
        self.token = self.tokenlist[self.tokenindex]

        # Step 5: Execution
        # TODO: Debug this piece of code
        self.functioncalldepth += 1
        self.codeblock()

        # Step 6: Return?
        self.functioncalldepth -= 1
        self.tokenindex = self.returnaddrstack.pop()
        self.token = self.tokenlist[self.tokenindex]

    def compoundstmt(self):
        # <compoundstmt>    -> <whilestmt>
        # <compoundstmt>    -> <ifstmt>
        # <compoundstmt>    -> <defstmt>
        if self.token.category == PYIF:
            self.ifstmt()
        elif self.token.category == PYWHILE:
            self.whilestmt()
        elif self.token.category == DEF:
            self.defstmt()

    def ifstmt(self):
        # <ifstmt>          -> 'if' <relexpr> ':' <codeblock> ('elif' <relexpr> ':' <codeblock>)* ['else' ':' <codeblock>]
        self.consume(PYIF)
        self.relexpr()
        condition = self.operandstack.pop()
        self.consume(COLON)
        """
        if condition is True then execute codeblock()
        But what to do if condition is False?
        We should track INDENT - DEDENT pairs
        """
        # NOTE: I switched the code from "if condition is True:" to "if condition:", so that /tests/misc/if_01.in has the same result compared to CPython.
        if condition:
            self.codeblock()
            """
            In case codeblock() encounters a "break", the "break" statement should be able to figure out the next token to execute. We should immediately return from whilestmt (and its children statements)
            """
            if self.flagbreak is True:
                return
        else:
            # Skip over until all pairs of INDENT-DEDENT are passed
            # codeblock() runs pass the indent-dedent block, but if we choose not to execute codeblock(), we need to implement this functionality by our own
            indent_tracker = 0
            indent_start = False
            while True:
                if self.token.category == INDENT:
                    indent_tracker += 1
                    indent_start = True
                elif self.token.category == DEDENT:
                    indent_tracker -= 1
                if indent_tracker == 0 and indent_start is True:
                    # We got all those indent-dedent pairs
                    # Next token should be a statement or something close
                    # Don't forget to advance() from the DEDENT
                    self.advance()
                    break
                self.advance()
        # Now that we skipped the codeblock of "if", we should expect either "else" or "elif", or something else which means that the "if" has no "else" nor "elif". We can also have multiple "elif"s so a loop is good for this kind of stuffs (or recursively function call)
        # Hacky way to tell the "else" block that some "elif" got executed
        elif_executed = False
        while self.token.category == PYELIF:
            self.advance()
            self.relexpr()
            condition_elif = self.operandstack.pop()
            self.consume(COLON)

            # We need to make sure that the if condition is False
            # Otherwise this will be falsely triggered if the if condition is True and the elif condition is also True
            # This is rare but still can happen (think counter == 0 and counter % 2 == 0 can be both true)
            if condition_elif is True and condition is False:
                if elif_executed is False:
                    elif_executed = True
                self.codeblock()
                if self.flagbreak is True:
                    return
            else:
                # Skip over until all pairs of INDENT-DEDENT are passed
                # codeblock() runs pass the indent-dedent block, but if we choose not to execute codeblock(), we need to implement this functionality by our own
                indent_tracker = 0
                indent_start = False
                while True:
                    if self.token.category == INDENT:
                        indent_tracker += 1
                        indent_start = True
                    elif self.token.category == DEDENT:
                        indent_tracker -= 1
                    if indent_tracker == 0 and indent_start is True:
                        # We got all those indent-dedent pairs
                        # Next token should be a statement or something close
                        # Don't forget to advance() from the DEDENT
                        self.advance()
                        break
                    self.advance()
        if self.token.category == PYELSE:
            self.advance()
            self.consume(COLON)
            # if either condition is True, we need to skip this part as ELSE won't be executed
            if condition is False and elif_executed is False:
                self.codeblock()
            else:
                # codeblock() runs pass the indent-dedent block, but if we choose not to execute codeblock(), we need to implement this functionality by our own
                indent_tracker = 0
                indent_start = False
                while True:
                    if self.token.category == INDENT:
                        indent_tracker += 1
                        indent_start = True
                    elif self.token.category == DEDENT:
                        indent_tracker -= 1
                    if indent_tracker == 0 and indent_start is True:
                        # We got all those indent-dedent pairs
                        # Next token should be a statement or something close
                        # Don't forget to advance() from the DEDENT
                        self.advance()
                        break
                    self.advance()

    def whilestmt(self):
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
        self.indentloop.append(self.token.column)
        if self.trace is True:
            print(f"Loop: {self.indentloop}")

        self.consume(PYWHILE)
        # Record the position of the first token after "while" so that we can jump back
        relexpr_pos = self.tokenindex
        while True:
            self.relexpr()
            condition = self.operandstack.pop()
            self.consume(COLON)
            if condition is True:
                self.codeblock()
                """
                In case codeblock() encounters a "break", the "break" statement should be able to figure out the next token to execute. We should immediately return from whilestmt (and its children statements)
                """
                if self.flagbreak is True:
                    # Since we only allow break in while loop, this should be the caller function that should reset flagbreak
                    # TODO: Logic above is wrong, we need to figure out how to set flagbreak to False at the proper level. The fllowing is WRONG.
                    # flagbreak = False
                    # To flag that I just break out from the correct while loop, my caller should set both flags to false
                    self.flagbreakloop = True
                    return
                else:
                    self.tokenindex = relexpr_pos
                    # Manually move the token
                    # global token
                    self.token = self.tokenlist[self.tokenindex]
            else:
                # as in if, we need to skip the indent-dedent block
                indent_tracker = 0
                indent_start = False
                while True:
                    if self.token.category == INDENT:
                        indent_tracker += 1
                        indent_start = True
                    elif self.token.category == DEDENT:
                        indent_tracker -= 1
                    if indent_tracker == 0 and indent_start is True:
                        # We got all those indent-dedent pairs
                        # Next token should be a statement or something close
                        # Don't forget to advance() from the DEDENT
                        self.advance()
                        # return instead of break as we are inside of double while loop
                        # Don't forget to pop the indentloop stack as no "break" is run
                        self.indentloop.pop()
                        return
                    self.advance()

    def defstmt(self):
        # <defstmt>         -> 'def' NAME '(' [NAME (, NAME)*] ')'':' <codeblock>
        """
        Primary function execution: read README.md for more details of the whole scheme.

        In globalsymboltable, each function takes the format of:
        "foo":{
            "parameters": ["a", "b", "c"],
            "entry":23
        }
        """
        self.advance()
        function_name = self.token.lexeme
        function_parameters = []
        if function_name in self.globalsymboltable:
            # Double definition, illegal
            raise RuntimeError(f"Function {function_name} was already defined")
        else:
            self.globalsymboltable[function_name] = {"parameters": function_parameters, "entry": None}
        self.advance()

        # Parameter names
        self.consume(LEFTPAREN)
        while True:
            token_cat = self.token.category
            if token_cat == RIGHTPAREN:
                break
            elif token_cat == NAME:
                # Must be a parameter
                self.globalsymboltable[function_name]["parameters"].append(self.token.lexeme)
                self.advance()
            elif token_cat == COMMA:
                self.advance()
                if self.token.category == NAME:
                    # Must be a parameter
                    self.globalsymboltable[function_name]["parameters"].append(self.token.lexeme)
                    self.advance()
                else:
                    raise RuntimeError(f"Expecting NAME after COMMA")
            else:
                raise RuntimeError(f"Expecting COMMA and NAME but get {catnames[token_cat]}")

        self.consume(RIGHTPAREN)
        self.consume(COLON)
        # Now we need to find the entry point and then skip the rest of the function
        while True:
            if self.token.category != INDENT:
                self.advance()
            else:
                # This is the entry point, recall that <codeblock> needs an INDENT token at the beginning
                self.globalsymboltable[function_name]["entry"] = self.tokenindex
                break
        # Skip the rest of the function
        while True:
            token_col = self.token.column
            token_cat = self.token.category
            # TODO: Need to de-hardcode token_col == 1 if we want to allow multiple layers of function definition (def within a def)
            if token_col == 1 and token_cat not in [INDENT, DEDENT]:
                break
            else:
                self.advance()

    def codeblock(self):
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
        while self.token.category == NEWLINE:
            self.consume(NEWLINE)
        self.consume(INDENT)
        # TODO: We need to fix a bug regarding empty codeblocks (see below)
        """
        Consider this empty codeblock -- there is nothing in this elif except for a few comments.
        elif counter == 2:
            # Test '=='
            # No direct string comparison to float_b, as str() is not allowed
        
        We should throw a RuntimeError.
        """
        if self.token.category not in stmttokens:
            raise RuntimeError(f"Expecting a statement but get {catnames[self.token.category]}")
        while self.token.category in [PRINT, NAME, PYPASS, PYIF, PYWHILE, BREAK]:
            self.stmt()
            """
            In case codeblock() encounters a "flagbreak" signal, this means we are breaking out. If the other signal "flagbreakloop" is also True, this means we are already out of the while loop we want to break out, so we should reset the two flags.

            Why do we need the second flag "flagbreakloop"? If we don't have it, we will have no way to know whether we have broken out of the correct while loop, so we don't know where to reset flagbreak properly. Consider a very nested if-codeblock inside of a while loop, we need to skip the consume(DEDENT) command arbitrarily times - only by setting a second flag do we know when we should we skip it or not.
            """

            """
            NOTE: This is super important. The following code says, ONLY return if flagbreak is TRUE and flagbreakloop is False, why? Consider the scenario (See test4.in): 
            1) When we are in the MIDDLE of the return "chain" triggered by a break, we need to return from codeblock(), why? Because we want to find the top loop that pairs with the break statement
            2) When we are already out of the return "chain", and if we still have more statements in the parent codeblock that contains the loop that we just broke out, we do NOT want to return, because there are other statements to be executed after the loop
            """
            if self.flagbreak is True:
                if self.flagbreakloop is True:
                    self.flagbreak = False
                    self.flagbreakloop = False
                else:
                    return
        self.consume(DEDENT)

    def relexpr(self):
        # <relexpr>         -> <expr> [ ('<' | '<=' | '==' | '!=' | '>=' | '>') <expr>]*
        """
        How can we deal with the chained expressions?

        print(30 > 20 > 10 < 100 >= 30 <= 30 < 50 != 50.01)
        print(10 > 20 > 30 == 30)
        print(-30 > -20 > -10)
        """
        left_operand = None
        right_operand = None
        result = None
        self.expr()

        while True:
            if self.token.category in [LESSTHAN, LESSEQUAL, EQUAL, NOTEQUAL, GREATEREQUAL, GREATERTHAN]:
                if right_operand is None:
                    left_operand = self.operandstack.pop()
                else:
                    left_operand = right_operand

                token_op = self.token
                self.advance()
                self.expr()
                right_operand = self.operandstack.pop()

                left_type = type(left_operand).__name__
                right_type = type(right_operand).__name__
                
                if token_op.category == LESSTHAN:
                    if is_operatable(operator=token_op.category, left_type=left_type, right_type=right_type):
                        result = (left_operand < right_operand) if result is None else (result and (left_operand < right_operand))
                    else:
                        raise RuntimeError(f"{token_op.lexeme} operator is not suitable for left operand type {left_type} and right operand type {right_type}")
                elif token_op.category == LESSEQUAL:
                    if is_operatable(operator=token_op.category, left_type=left_type, right_type=right_type):
                        result = (left_operand <= right_operand) if result is None else (result and (left_operand <= right_operand))
                    else:
                        raise RuntimeError(f"{token_op.lexeme} operator is not suitable for left operand type {left_type} and right operand type {right_type}")
                elif token_op.category == EQUAL:
                    if is_operatable(operator=token_op.category, left_type=left_type, right_type=right_type):
                        result = (left_operand == right_operand) if result is None else (result and (left_operand == right_operand))
                    else:
                        # Users should be able to put anything on both ends and get either True or False
                        self.operandstack.append(False)
                elif token_op.category == NOTEQUAL:
                    if is_operatable(operator=token_op.category, left_type=left_type, right_type=right_type):
                        result = (left_operand != right_operand) if result is None else (result and (left_operand != right_operand))
                    else:
                        self.operandstack.append(True)
                elif token_op.category == GREATEREQUAL:
                    if is_operatable(operator=token_op.category, left_type=left_type, right_type=right_type):
                        result = (left_operand >= right_operand) if result is None else (result and (left_operand >= right_operand))
                    else:
                        raise RuntimeError(f"{token_op.lexeme} operator is not suitable for left operand type {left_type} and right operand type {right_type}")
                elif token_op.category == GREATERTHAN:
                    if is_operatable(operator=token_op.category, left_type=left_type, right_type=right_type):
                        result = (left_operand > right_operand) if result is None else (result and (left_operand > right_operand))
                    else:
                        raise RuntimeError(f"{token_op.lexeme} operator is not suitable for left operand type {left_type} and right operand type {right_type}")
            else:
                # We only need to push result onto the stack if there is at least one comparison
                if result is not None:
                    self.operandstack.append(result)
                break

    def expr(self):
        # <expr>            -> <term> ('+' <term>)*
        # <expr>            -> <term> ('-' <term>)*
        
        # NOTE: Now we introduce strings into the picture, we need to check types
        self.term()
        while self.token.category == PLUS or self.token.category == MINUS:
            # Now the left side was pushed onto the operand stack
            # Note that the left side must be in the loop for multiple operations
            optoken = self.token
            left = self.operandstack.pop()
            self.advance()
            self.term()
            # Now the right side was pushed onto the operand stack
            right = self.operandstack.pop()
            # If not of the same type then we simply cannot add or subtract
            if type(left) != type(right):
                raise RuntimeError(f"Cannot add/subtract {type(left)} with {type(right)}")
            if optoken.category == PLUS:
                self.operandstack.append(left + right)
            else:
                self.operandstack.append(left - right)

    def term(self):
        # <term>            -> <factor> ('*' <factor>)*
        # <term>            -> <factor> ('/' <factor>)*
        # <term>            -> <factor> ('%' <factor>)*
        self.factor()
        while self.token.category in [TIMES, DIVISION, MODULO]:
            # Now the left side was pushed onto the operand stack
            # Note that the left side must be in the loop for multiple operations
            optoken = self.token
            left = self.operandstack.pop()
            self.advance()
            self.factor()
            # Now the right side was pushed onto the operand stack
            right = self.operandstack.pop()
            if optoken.category == TIMES:
                self.operandstack.append(left * right)
            elif optoken.category == DIVISION:
                self.operandstack.append(left / right)
            elif optoken.category == MODULO:
                self.operandstack.append(left % right)

    def factor(self):
        # <factor>          -> '+' <factor>
        # <factor>          -> '-' <factor>
        # <factor>          -> NAME
        # <factor>          -> INTEGER
        # <factor>          -> FLOAT
        # <factor>          -> STRING
        # <factor>          -> 'True'
        # <factor>          -> 'False'
        # <factor>          -> 'None'
        # <factor>          -> '(' <relexpr> ')'
        if self.token.category == PLUS:
            self.advance()
            self.factor()
            # Now the right side must also be on the stack
            right = self.operandstack.pop()
            self.operandstack.append(right)
        elif self.token.category == MINUS:
            self.advance()
            self.factor()
            # Now the right side must also be on the stack
            right = self.operandstack.pop()
            self.operandstack.append(-1 * right)
        elif self.token.category == NAME:
            """
            With functional call implementation, we need to do the following checks:
            - What is the current scope? (functioncalldepth == 0 or > 0?)
            - Is variable declared to be global? (check globalvardeclared)
            - If we are in local scope and cannot find the variable, don't forget to check the global scope as well
            """
            if self.token.lexeme in self.globalvardeclared:
                if self.token.lexeme not in self.globalsymboltable:
                    raise RuntimeError(f"Name {self.token.lexeme} is decalred to be global yet not defined in global scope.")
                else:
                    self.operandstack.append(self.globalsymboltable[self.token.lexeme])
            else:
                if self.token.lexeme not in self.localsymboltable:
                    if self.token.lexeme not in self.globalsymboltable:
                        raise RuntimeError(f"Name {self.token.lexeme} is not defined in local scope, and neither is it defined in the global scope.")
                    else:
                        self.operandstack.append(self.globalsymboltable[self.token.lexeme])
                else:
                    self.operandstack.append(self.localsymboltable[self.token.lexeme])

            self.advance()
        elif self.token.category == FLOAT:
            self.operandstack.append(float(self.token.lexeme))
            self.advance()
        elif self.token.category == INTEGER:
            self.operandstack.append(int(self.token.lexeme))
            self.advance()
        elif self.token.category == STRING:
            self.operandstack.append(self.token.lexeme)
            self.advance()
        elif self.token.category == PYTRUE:
            self.operandstack.append(True)
            self.advance()
        elif self.token.category == PYFALSE:
            self.operandstack.append(False)
            self.advance()
        elif self.token.category == PYNONE:
            self.operandstack.append(None)
            self.advance()
        elif self.token.category == LEFTPAREN:
            self.advance()
            self.relexpr()
            self.consume(RIGHTPAREN)
        else:
            raise RuntimeError("Expecting a valid expression.")
