from pynode import node, funcDict
import builtins

name = 'listComp'

@node(outputs=['out'])
def map(func, arr):
    return list(builtins.map(func, arr))

@node(outputs=['out'])
def strip(arr, func):
    return [i for i in arr if func(i)]

@node(outputs=['out'])
def slice(arr, a=None, b=None):
    assert a != None or b != None, 'Only one bound can be None.'
    if a == None:
        return arr[:b]
    else:
        return arr[a:]
