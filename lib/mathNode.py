from importNode import node, funcDict
import builtins

name = 'math'
dependencies = ['builtins']

@node(outputs=['sum'])
def add(*args):
    return sum(args)

@node(outputs=['difference'])
def subtract(a, b):
    return a - b

@node(outputs=['product'])
def multiply(*args):
    c = 1
    for num in args:
        c *= num
    return c

@node(outputs=['quotient'])
def divide(a, b):
    return a / b

@node(outputs=['quotient'])
def intDivide(a, b):
    return a // b
