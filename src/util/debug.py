"""A bunch of utilities to help debugging
"""

def debug_print(input: str, index: int):
    """Prints the input string as first line
    And print a ^ char at index i as second line

    Args:
        input (str): the input string
        index (i): index of the ^, starting from 0
    """

    # (index >= len(input) and len(input) > 0) to make sure that empty string also works
    # otherwise it raises the error when index = 0 and string is empty
    if index < 0:
        raise ValueError("Wrong index")
    else:
        print(input)
        print(' ' * index + '^')