funcDict = {}
nodeDict = {}

def node(outputs=[], nodeType='Node'):
    def inner(f):
        global funcDict, nodeDict
        funcDict[f] = outputs
        nodeDict[f] = nodeType
        return f
    return inner
