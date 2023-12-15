"""Write a Python program that inputs a string and determines if it is in the language given in problem 8

Q: Write a CFG that defines the set of all palindromes over the alphabet {a, b}. *Hint*: Be sure to consider palindromes of odd length (e.g. `aabaa`).

A: <P> -> 'a' | 'b' | 'a'<P>'a' | 'b'<P>'b' | λ

For claritiy I'll rewrite the rule into 4 parts:
<P> -> 'a' | 'b'
<P> -> λ
<P> -> 'a'<P>'a' | 'b'<P>'b'
"""
import sys

# global variables
tokenindex = -1
token = ''

def P():
    """This function does not deal with single-character string such as 'a' and 'b'
    """
    if token == 'a':
        advance()
        P()
        consume('a')
    elif token == 'b':
        advance()
        P()
        consume('b')
    elif token == '':
        return

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
    if len(input) == 0:
        print("Zero-length strings are considered to be palindromes")
        return
    if len(input) == 1:
        print("One-char strings are always palindromes")
        return
    advance()
    P()
    if token == '':
        print(f"{input} is a palindrome")
    else:
        print(f"{input} is a NOT palindrome")

if __name__ == '__main__':
    parser(sys.argv[1])