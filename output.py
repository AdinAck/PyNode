from lib import numpyNode

def func(i1, i2, i3):
	a = lambda: numpyNode.concatenate(i1, i2, i3)
	return a()
