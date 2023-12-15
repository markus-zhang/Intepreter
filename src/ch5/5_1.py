"""
<S> -> <A><B><C>    {'a', 'b', 'c', EOF}
<A> -> 'a'          {'a'}
<A> -> λ            {'b', 'c', EOF}
<B> -> 'b'          {'b'}
<B> -> λ            {'c', EOF}
<C> -> 'c'          {'c'}
<C> -> λ            {EOF}
"""
import sys

# global variables
tokenindex = -1
token = ''

def S():
    A()
    B()
    C()

def A():
    if token == 'a':
        advance()

def B():
    if token == 'b':
        advance()

def C():
    if token == 'c':
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