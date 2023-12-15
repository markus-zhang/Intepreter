"""
<S> -> 'a'(<B>|<C>)['d']'e' {'a'}
<B> -> 'b'*                 {'b', 'd', 'e'}
<C> -> 'c'+                 {'c'}
"""
import sys

# global variables
tokenindex = -1
token = ''

def S():
    consume('a')

    if token == 'b':
        B()
    elif token == 'c':
        C()
    
    if token == 'd':
        advance()

    consume('e')

def B():
    while token == 'b':
        advance()

def C():
    while token == 'c':
        advance()

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
    if len(sys.argv) > 1:
        arg1 = sys.argv[1]
    else:
        arg1 = ""
    parser(arg1)