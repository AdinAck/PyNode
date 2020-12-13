from lib import builtin, listComp, logic

def func(text, func):
	a = lambda: builtin.lenArr(arr=text)
	b = lambda: logic.eq(a=c(), b=a())
	c = lambda: builtin.lenArr(arr=d())
	d = lambda: listComp.strip(arr=text, func=func)
	return b()

print(func('32123124', lambda x: x.isdigit()))
