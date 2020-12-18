from lib import numpyNode

def oh_yeah(i1, i2):
	a = lambda: numpyNode.array(i1, dtype=i2)
	return a()