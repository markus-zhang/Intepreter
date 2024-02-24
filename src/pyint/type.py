from header import *

# "Operatable" dictionary
# [LESSTHAN, LESSEQUAL, EQUAL, NOTEQUAL, GREATEREQUAL, GREATERTHAN]
operatable = {
    #--------------------------------- Plus and Minus ---------------------------------
    PLUS:           [('int', 'int'), ('float', 'float'), ('int', 'float'), ('float', 'int'), ('str', 'str')],
    MINUS:          [('int', 'int'), ('float', 'float'), ('int', 'float'), ('float', 'int')],
    TIMES:          [('int', 'int'), ('float', 'float'), ('int', 'float'), ('float', 'int')],
    DIVISION:       [('int', 'int'), ('float', 'float'), ('int', 'float'), ('float', 'int')],
    MODULO:         [('int', 'int')],
    #------------------------------ Composite Assignments ------------------------------
    ADDASSIGN:      [('int', 'int'), ('float', 'float'), ('int', 'float'), ('float', 'int'), ('str', 'str')],
    SUBASSIGN:      [('int', 'int'), ('float', 'float'), ('int', 'float'), ('float', 'int')],
    MULASSIGN:      [('int', 'int'), ('float', 'float'), ('int', 'float'), ('float', 'int'), ('str', 'int')],
    DIVASSIGN:      [('int', 'int'), ('float', 'float'), ('int', 'float'), ('float', 'int')],
    #------------------------------ Comparison Operators -------------------------------
    LESSTHAN:       [('int', 'int'), ('float', 'float'), ('int', 'float'), ('float', 'int'), ('str', 'str')],
    LESSEQUAL:      [('int', 'int'), ('float', 'float'), ('int', 'float'), ('float', 'int'), ('str', 'str')],
    # EQUAL and NOTEQUAL are a bit special, users should be able to put whatever type on both ends, but the interpreter needs to return False instead of spitting out a RuntimeError
    EQUAL:          [('int', 'int'), ('float', 'float'), ('int', 'float'), ('float', 'int'), ('str', 'str')],
    NOTEQUAL:       [('int', 'int'), ('float', 'float'), ('int', 'float'), ('float', 'int'), ('str', 'str')],
    GREATEREQUAL:   [('int', 'int'), ('float', 'float'), ('int', 'float'), ('float', 'int'), ('str', 'str')],
    GREATERTHAN:    [('int', 'int'), ('float', 'float'), ('int', 'float'), ('float', 'int'), ('str', 'str')],
}

def is_operatable(operator, left_type, right_type):
    return (left_type, right_type) in operatable[operator]

# Test
def main():
    assert(is_operatable(ADDASSIGN, 'str', 'str') == True)
    assert(is_operatable(ADDASSIGN, 'int', 'int') == True)
    assert(is_operatable(ADDASSIGN, 'int', 'str') == False)
    assert(is_operatable(ADDASSIGN, 'str', 'int') == False)
    assert(is_operatable(ADDASSIGN, 'str', 'float') == False)
    assert(is_operatable(ADDASSIGN, 'float', 'str') == False)