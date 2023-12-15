"""
<S> -> 'a'<B>'b'
<B> -> ('b''b')*['c']
"""
import sys

# global variables
tokenindex = -1
token = ''

def S():
    """This function does not deal with single-character string such as 'a' and 'b'
    """
    consume('a')
    B()
    consume('d')

def B():
    if token == 'b':
        """We have to make sure it has even numbers of 'b'
        """
        bCount = 0
        while token == 'b':
            bCount += 1
            advance()
        if bCount % 2 == 1:
            raise RuntimeError()
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
    parser(sys.argv[1])