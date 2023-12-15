"""
<S> -> <S>'a'
<S> -> 'b'

Since this is left recursion, I modified with +:
<S> -> 'b'+'a'
"""
import sys

# global variables
tokenindex = -1
token = ''

def S():
    if token != 'b':
        raise RuntimeError("S must start with b")
    while token == 'b':
        advance()
    consume('a')

def consume(token_expected: str):
    global token
    if token_expected == token:
        advance()
    else:
        raise RuntimeError("Expecting " + token_expected)
    
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
    except RuntimeError:
        print(f"{input} does NOT match the CFG")
        exit(1)
    if token == '':
        print(f"{input} matches the CFG")
    else:
        print(f"{input} does NOT match the CFG")

if __name__ == '__main__':
    parser(sys.argv[1])