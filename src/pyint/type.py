from header import *

# "Operatable" dictionary
operatable = {
    ADDASSIGN: [('int', 'int'), ('float', 'float'), ('int', 'float'), ('float', 'int'), ('str', 'str')],
    SUBASSIGN: [('int', 'int'), ('float', 'float'), ('int', 'float'), ('float', 'int')],
    MULASSIGN: [('int', 'int'), ('float', 'float'), ('int', 'float'), ('float', 'int'), ('str', 'int')],
    DIVASSIGN: [('int', 'int'), ('float', 'float'), ('int', 'float'), ('float', 'int')]
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