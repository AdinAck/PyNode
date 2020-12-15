from pygame_textinput import TextInput # <- NOT made by me, a community plugin for pygame
import pygame as pg
from os import listdir

def export():
    usedVars = []
    count = 1
    with open('output.py', 'w') as f:
        f.write(f"from lib import {', '.join([l for l in funcLib if l in ['.'.join(f.__module__.split('.')[1:]) for f in [node.func for node in nodeList if node.func != None]]])}\n")
        f.write('\n')
        f.write(f"def func({', '.join(inputNode.outputs)}):\n")

        i = 0
        for node in nodeList:
            if type(node) not in [InputNode, OutputNode]:
                node.varNames = [chr(97+(i%26))+(str(i//26+1) if i//26 > 0 else '') for _ in node.outputs]
                i += len(node.outputs)
            elif type(node) == InputNode:
                node.varNames = node.outputs

        for node in nodeList:
            if type(node) == Node:
                node.varNames = [o if o not in usedVars else o+'_1' for o in node.varNames]
                a = ','.join(node.varNames)
                b = '.'.join(node.func.__module__.split('.')[1:])
                c = node.func.__name__
                d = ', '.join([(node.inputs[c[3]]+'=' if node.inputs[c[3]] in node.defaults else '')+c[0].varNames[c[1]]+('' if type(c[0]) == InputNode else '()') for c in connections if c[2] == node])
                if len(node.varNames) == 1:
                    f.write(f"\t{a} = lambda: {b}.{c}({d})\n")
                elif len(node.varNames) > 1:
                    f.write(f"\t_c{count} = lambda: {b}.{c}({d})\n")
                    for i, o in zip(range(len(node.varNames)), node.varNames):
                        f.write(f"\t{o} = lambda: _{count}()[{i}]\n")
                    count += 1
                usedVars.extend(node.varNames)

        f.write(f"\treturn {', '.join([c[0].varNames[c[1]]+('' if type(c[0]) == InputNode else '()') for c in connections if c[2] == outputNode])}")

def spawnFromSearch():
    global search, funcDict, nodeDict, selectedFunc, searchMousePos
    search = False
    eval(nodeDict[selectedFunc])(selectedFunc, x=searchMousePos[0], y=searchMousePos[1])

pg.init()

win = pg.display.set_mode(size=(1280,720), flags=pg.RESIZABLE)
pg.display.set_caption("PyGUI")

origin = [1280//2,720//2]
nodeList = []
fontSmall = pg.font.SysFont('Consolas', 12)
fontMedium = pg.font.SysFont('Consolas', 16)
startPin = None
endPin = None
connections = []
connectedPins = {}
search = False
options = False
optionNode = None
leftClick = False
rightClick = False
mousePos = (0,0)
mouseButtons = [0,0,0]
lineStart = [0,0]
events = None
selectedFunc = None
searchMousePos = (0,0)
spawned = False

# import node function
from pynode import funcDict, nodeDict

from nodeTypes import *

# import user defined functions
funcLib = [n[:-3] for n in listdir('lib') if '.py' in n]

funcNames = {}

for l in funcLib:
    exec(f'import lib.{l}')
    funcNames[f'lib.{l}'] = eval(f'lib.{l}.name')

inputNode = InputNode(x=-550)
outputNode = OutputNode(x=400)

def play():
    global win, funcDict, fontMedium, nodeList, startPin, endPin, connectedPins, search, options, optionNode, leftClick, rightClick, mousePos, mouseButtons, connections, lineStart, fontSmall, events, selectedFunc, searchMousePos, spawned
    previousMouse = 0,0,0
    clock = pg.time.Clock()
    run = True
    while run:
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                run = False
            if event.type == pg.VIDEORESIZE:
                win = pg.display.set_mode(size=(event.w,event.h),flags=pg.RESIZABLE)
                # displaySize = pg.display.get_surface().get_size()
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 4:
                    pass
                if event.button == 5:
                    pass

        win.fill((20,20,20))

        # grab key and mouse presses
        keys = pg.key.get_pressed()
        mouseButtons = pg.mouse.get_pressed()
        mousePos = pg.mouse.get_pos()[0]-origin[0], pg.mouse.get_pos()[1]-origin[1]

        if keys[pg.K_LCTRL] and keys[pg.K_s]:
            export()

        # get mouse leftClick not hold
        if mouseButtons[0]:
            if previousMouse[0]:
                leftClick = False
            else:
                leftClick = True

        if mouseButtons[2]:
            if previousMouse[2]:
                rightClick = False
            else:
                rightClick = True

        previousMouse = mouseButtons

        # dragging view around
        mouseRel = pg.mouse.get_rel()

        if not mouseButtons[0]:
            connectedPins = {}

        # test for illegal kwargs connection
        for i, c in zip(range(len(connections)), connections):
            if c[2].inputs[c[3]] == 'kwargs':
                connections.pop(i)


        if startPin != None:
            if mouseButtons[0]:
                color = (255,100,100)
                if endPin != None:
                    if endPin[1] != startPin[1]:
                        color = (100,255,100)
                pg.draw.line(win, color, (origin[0]+lineStart[0], origin[1]+lineStart[1]), pg.mouse.get_pos(), 4)
            else:
                if endPin != None:
                    if startPin[1] != endPin[1]:
                        if startPin[1] == 0:
                            connections.append([endPin[0], endPin[2], startPin[0], startPin[2]])
                        else:
                            connections.append([startPin[0], startPin[2], endPin[0], endPin[2]])
                    endPin = None
                lineStart = startPin[0].x+startPin[1],startPin[0].y+50+startPin[2]*25-1
                if startPin[1] == 0:
                    connectedPins['end'] = startPin
                else:
                    connectedPins['start'] = startPin

        for c in connections:
            pg.draw.line(win, (100,255,100), (origin[0]+c[0].x+c[0].w, origin[1]+c[0].y+50+c[1]*25-1), (origin[0]+c[2].x, origin[1]+c[2].y+50+c[3]*25-1), 4)

        if not mouseButtons[0]:
            startPin = None
            endPin = None
        for n in nodeList[::-1]:
            if not (origin[0]+n.x > win.get_width()+10 or origin[1]+n.y > win.get_height()+10 or origin[0]+n.x+n.w < -10 or origin[1]+n.y+n.h < -10):
                n.render()

        touchingNode = False
        for node in nodeList:
            if node.bounds[0] <= mousePos[0] <= node.bounds[1] and node.bounds[2] <= mousePos[1] <= node.bounds[3]:
                if mouseButtons[0] and startPin == None:
                    node.move(node.x + mouseRel[0], node.y + mouseRel[1])
                nodeList.remove(node)
                nodeList.insert(0,node)
                touchingNode = True
                if rightClick:
                    options = True
                    optionNode = node
                break

        if len(nodeList) > 0:
            if not touchingNode and startPin == None:
                if mouseButtons[0]:
                    origin[0] += mouseRel[0]
                    origin[1] += mouseRel[1]

        if options:
            width, height = 100, 100
            pad = 8
            if leftClick:
                if not ((optionNode.x <= mousePos[0] <= optionNode.x+width and optionNode.y-height-pad <= mousePos[1] <= optionNode.y-pad) or (touchingNode and node == optionNode)):
                    options = False

            pg.draw.rect(win, (255,255,255), (origin[0]+optionNode.x, origin[1]+optionNode.y-height-pad, width, height))

        if keys[pg.K_LCTRL] and keys[pg.K_SPACE]:
            textinput = TextInput(font_family='Consolas',font_size=16, text_color=(255,255,255), cursor_color=(255,255,255))
            searchMousePos = mousePos
            search = True
            selectedSearch = 0
            searchResults = 0
        elif keys[pg.K_LCTRL] and keys[pg.K_d] and not spawned:
            selectedFunc = nodeList[0].func
            searchMousePos = mousePos
            spawnFromSearch()
            spawned = True
        elif not (keys[pg.K_LCTRL] and keys[pg.K_d]):
            spawned = False

        if search:
            if keys[pg.K_ESCAPE]:
                search = False
            elif keys[pg.K_RETURN]:
                spawnFromSearch()
            elif not keys[pg.K_DOWN] and not keys[pg.K_UP]:
                arrowPressed = False
            if keys[pg.K_DOWN] and not arrowPressed:
                arrowPressed = True
                if selectedSearch < searchResults-1:
                    selectedSearch += 1
                else:
                    selectedSearch = 0
            elif keys[pg.K_UP] and not arrowPressed:
                arrowPressed = True
                if selectedSearch > 0:
                    selectedSearch -= 1
                else:
                    selectedSearch = searchResults-1

        if search:
            textinput.update(events)
            searchResultsList = [f for f in funcDict if textinput.get_text().lower() in funcNames[f.__module__]+'.'+f.__name__.lower()]
            searchResults = len(searchResultsList) if textinput.get_text() != "" else 0
            tmp = max(max([fontMedium.render(funcNames[f.__module__]+'.'+f.__name__, True, (0,0,0)).get_width() for f in searchResultsList] if len(searchResultsList) > 0 else [0]), textinput.get_surface().get_width()+20)
            width = tmp if tmp > 300 else 300
            pg.draw.rect(win, (0,0,0), (origin[0]+searchMousePos[0], origin[1]+searchMousePos[1], width, 40+25*searchResults))
            win.blit(textinput.get_surface(), (origin[0]+searchMousePos[0]+10, origin[1]+searchMousePos[1]+10))
            if textinput.get_text() != "":
                if searchResults > 0:
                    pg.draw.rect(win, (255,255,255), (origin[0]+searchMousePos[0]+5, origin[1]+searchMousePos[1]+45+selectedSearch*25-10, width-10, 25))
                for i, f, name in zip(range(len(searchResultsList)), searchResultsList, [funcNames[f.__module__]+'.'+f.__name__ for f in searchResultsList]):
                    color = (255,255,255)
                    if searchMousePos[0] <= mousePos[0] <= searchMousePos[0]+width and searchMousePos[1]+40+i*25 <= mousePos[1] < searchMousePos[1]+40+i*25+25:
                        if abs(mouseRel[0]) > 0 or abs(mouseRel[1]) > 0:
                            selectedSearch = i
                        if leftClick:
                            spawnFromSearch()
                    elif selectedSearch > searchResults-1:
                        selectedSearch = searchResults-1
                    if selectedSearch == i:
                        color = (0,0,0)
                        selectedFunc = f
                    win.blit(fontMedium.render(name, True, color), (origin[0]+searchMousePos[0]+10, origin[1]+searchMousePos[1]+40+i*25))
                    i += 1

            if leftClick and not (searchMousePos[0] <= mousePos[0] <= searchMousePos[0]+300 and searchMousePos[1] <= mousePos[1] <= searchMousePos[1]+40+25*searchResults):
                search = False
        # print(clock.get_fps())
        pg.display.update()
        # clock.tick()

    pg.quit()
    exit()
