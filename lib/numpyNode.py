from pynode import node, funcDict
import numpy as np

name = 'np'

@node(outputs=['out'])
def array(object, dtype=None, copy=True, order='K', subok=False, ndmin=0):
    return np.array(object, dtype=dtype, copy=copy, order=order, subok=subok, ndmin=ndmin)

@node(outputs=['out'])
def zeros(shape, dtype=float, order='C'):
    return np.zeros(shape, dtype=dtype, order=order)
