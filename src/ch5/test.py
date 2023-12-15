"""
<S> -> 'a'(B|C)'d'  {'a'}
<B> -> 'b'          {'b'}
<C> -> 'c'*         {'c', 'd'}
"""
import sys

# global variables
tokenindex = -1
token = ''

def S():
    consume('a')
    if token == 'b':
        B()
    elif token == 'c' or token == 'd':
        C()
    else:
        raise RuntimeError("Expecting 'b', 'c' or 'd'")
    consume('d')

def B():
    consume('b')

def C():
    if token == 'c':
        while token == 'c':
            advance()
    if token == 'd':
        pass

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