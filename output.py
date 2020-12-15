from lib import builtin

def func(i1, i2, i3):
	a = lambda: builtin.list(i1, i2, i3)
	return a()