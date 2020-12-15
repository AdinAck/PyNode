from pynode import node, funcDict
import numpy as np

name = 'np'

@node(outputs=['out'])
def array(object, dtype=None, copy=True, order='K', subok=False, ndmin=0):
    return np.array(object, dtype=dtype, copy=copy, order=order, subok=subok, ndmin=ndmin)

@node(outputs=['out'])
def zeros(shape, dtype=float, order='C'):
    return np.zeros(shape, dtype=dtype, order=order)

@node(outputs=['out'])
def ones(shape, dtype=float, order='C'):
    return np.zeros(shape, dtype=dtype, order=order)

@node(outputs=['out'])
def concatenate(*args, axis=0, out=None):
    return np.concatenate(args, axis=axis, out=out)

@node(outputs=['append'])
def append(arr, values, axis=None):
    return np.append(arr, values, axis=axis)

@node(outputs=['out'])
def insert(arr, obj, values, axis=None):
    return np.insert(arr, object, values, axis=axis)

@node(outputs=['out'])
def delete(arr, obj, axis=None):
    return np.delete(arr, obj, axis=axis)
