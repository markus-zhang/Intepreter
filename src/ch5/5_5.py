"""
<S> -> <S>'a'   {'a'}
<S> ->'a'       {'a'}
"""
import sys
sys.path.insert(1, "C:/Dev/Projects/Intepreter/src/util/")
import debug

# global variables
tokenindex = -1
token = ''

def S():
    consume('a')
    consume('a')
    while token == 'a':
        advance()

def A():
    if token == 'a':
        while token == 'a':
            advance()
    elif token == 'b':
        pass
    else:
        debug.debug_print(sys.argv[1], tokenindex)
        raise RuntimeError("Expecting 'a' or 'b'")
    
def B():
    if token == 'b':
        while token == 'b':
            advance()
    else:
        debug.debug_print(sys.argv[1], tokenindex)
        raise RuntimeError("Expecting 'b'")

def C():
    while token == 'c':
        advance()

def consume(token_expected: str):
    global token
    if token_expected == token:
        advance()
    else:
        debug.debug_print(sys.argv[1], tokenindex)
        raise RuntimeError(f"Token: {token} at index {tokenindex} - Expecting " + token_expected)
    
def advance():
    global token, tokenindex
    tokenindex += 1

    if len(sys.argv) < 2 or tokenindex >= len(sys.argv[1]):
        token = ''  # signal the end by returning ''
    else:
        token = sys.argv[1][tokenindex]

def parser(input: str):
    advance()
    try:
        S()
    except RuntimeError as e:
        print(f"{input} does NOT match the CFG")
        print(e)
        exit(1)
    if token == '':
        print(f"{input} matches the CFG")
    else:
        print(f"{input} does NOT match the CFG")
        exit(1)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg1 = sys.argv[1]
    else:
        arg1 = ""
        sys.argv.append("")
    parser(arg1)