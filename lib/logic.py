from importNode import node, funcDict

name = 'logic'
dependencies = []

@node(outputs=['o'])
def NOT(a):
    return not a

@node(outputs=['o'])
def AND(a, b):
    return a and b

@node(outputs=['o'])
def OR(a, b):
    return a or b

@node(outputs=['o'])
def NAND(a, b):
    return not (a and b)

@node(outputs=['o'])
def NOR(a, b):
    return not (a or b)

@node(outputs=['o'])
def XOR(a, b):
    return a ^ b

@node(outputs=['o'])
def eq(a, b):
    return a == b
