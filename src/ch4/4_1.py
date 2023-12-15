"""
<S> -> 'a'<S>'b'
<S> -> 'c'

It's tough to use a loop. We can have acb, aacbb, aaaacbbbb. The probelm is number of 'a' must agree with the number of 'b'. So recursion is a lot easier in this case.
"""
import sys

# global variables
tokenindex = -1
token = ''

def S():
    """This function does not deal with single-character string such as 'a' and 'b'
    """
    if token == 'c':
        advance()
        return
    consume('a')
    S()
    consume('b')

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