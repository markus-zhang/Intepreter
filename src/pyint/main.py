import sys
from tokenizer import tokenizer
from pyparser import pyparser

# Control switches
only_tokenizer = False

def main():
    source = ''
    tokenlist = []

    if len(sys.argv) == 2:
        try:
            infile = open(sys.argv[1], 'r')
            source = infile.read()
        except IOError:
            print(f'Failed to read input file {sys.argv[1]}')
            sys.exit(1)
    else:
        print('Wrong number of command line arguments')
        print('Usage: python3 interpreter.py <infile>')
        sys.exit(1)

    # Add newline to end if missing TODO: Why does the last line need a newline?
    # (probably because the parser needs a newline to properly identify one line)
    if source[-1] != '\n':
        source = source + '\n'

    T = tokenizer(source=source, tokenlist=tokenlist)

    try:
        T.run()
        if only_tokenizer == True:
            exit()
        T.traceall()
        T.removecomment()
        P = pyparser(tokenlist=tokenlist, source=source)
        P.parse()
    except RuntimeError as emsg:
        T.dump()
        P.dump()
        print(emsg)
        sys.exit(1)

main()