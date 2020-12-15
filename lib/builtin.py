from pynode import node, funcDict
import builtins

name = 'builtin'

@node(outputs=['0'], nodeType='ValueNode')
def Value(val=0):
    return val

@node(outputs=['len'])
def lenArr(arr):
    return len(arr)

@node(outputs=['list'])
def split(text, splitter):
    return text.split(splitter)

@node(outputs=['range'])
def range(end, start=0, step=1):
    return builtins.range(start, end, step)

@node(outputs=['list'])
def list(*args):
    return args

@node(outputs=['str'])
def join(joiner, *args):
    return joiner.join(args)

@node()
def test(a, *args, **kwargs):
    return
