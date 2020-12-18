from pygame_textinput import TextInput # <- NOT made by me, a community plugin for pygame
# https://github.com/Nearoo/pygame-text-input
# any code initializing or calling methods from a 'TextInput' object are utilizing the above resource

import pygame as pg # <- NOT made by a me, a large python library for displaying real time graphics and interactive elements
# https://www.pygame.org/wiki/about
# any code under 'pg.' is utilizing objects, methods, and constants from the above resource

from os import listdir
from tkinter import Tk, filedialog
import pickle

Tk().withdraw()

pg.init()

win = pg.display.set_mode(size=(1280,720), flags=pg.RESIZABLE)
pg.display.set_caption("PyGUI")

origin = [1280//2,720//2]
nodeList = []
fontSmall = pg.font.SysFont('Consolas', 12)
fontMedium = pg.font.SysFont('Consolas', 16)
fontLarge = pg.font.SysFont('Consolas', 24)
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
id = 0
idDict = {}
saveName = None

# import node function
from importNode import funcDict, nodeDict

from nodeTypes import *

# import user defined functions
funcLib = [n[:-3] for n in listdir('lib') if '.py' in n]

funcNames = {}

for l in funcLib:
    exec(f'import lib.{l}')
    funcNames[f'lib.{l}'] = eval(f'lib.{l}.name')

inputNode = InputNode(x=-550)
outputNode = OutputNode(x=400)

def openPrj(fileName):
    global nodeList, connections, saveName
    nodeList = [node for node in nodeList if type(node) in [InputNode, OutputNode]]
    with open(fileName, 'rb') as p:
        load_nodeList, load_connections, saveName = pickle.load(p)
        for nodeType, func, inputs, outputs, x, y in load_nodeList[::-1]:
            if nodeType not in [InputNode, OutputNode]:
                tmp = nodeType(func)
            elif nodeType == InputNode:
                tmp = inputNode
            elif nodeType == OutputNode:
                tmp = outputNode
            tmp.x, tmp.y = x, y
            tmp.inputs = inputs
            tmp.outputs = outputs
            tmp.updateSize()
        for c in load_connections:
            connections.append([idDict[c[0]], c[1], idDict[c[2]], c[3]])

def export(fileName, funcName, standalone, exportNode):
    count = 1
    if exportNode:
        fType = 'a'
    else:
        fType = 'w'
    with open(fileName, fType) as f:
        if exportNode:
            f.write('\n')
        if standalone:
            tmp = [eval(n.func.__module__).dependencies for n in nodeList if n.func != None]
            d = set()
            for i in tmp:
                for j in i:
                    d.add(j)
            f.write('import ' + ', '.join(list(d))+'\n\n')
            for node in nodeList:
                if node.func != None:
                    f.write('\n'.join(inspect.getsource(node.func).split('\n')[1:])+'\n')
        else:
            f.write(f"from lib import {', '.join([l for l in funcLib if l in ['.'.join(f.__module__.split('.')[1:]) for f in [node.func for node in nodeList if node.func != None]]])}\n")
        f.write('# ========================================')
        f.write('\n')
        f.write('\n')
        if exportNode:
            f.write(f'@node(outputs={[i for i in outputNode.inputs]})\n')
        f.write(f"def {funcName}({', '.join(inputNode.outputs)}):\n")

        i = 0
        for node in nodeList:
            if type(node) not in [InputNode, OutputNode]:
                node.varNames = [chr(97+(i%26))+(str(i//26+1) if i//26 > 0 else '') for _ in node.outputs]
                i += len(node.outputs)
            elif type(node) == InputNode:
                node.varNames = node.outputs

        for node in nodeList:
            if type(node) == Node:
                a = ','.join(node.varNames)
                b = '.'.join(node.func.__module__.split('.')[1:])
                c = node.func.__name__
                d = ', '.join([(node.inputs[c[3]]+'=' if node.inputs[c[3]] in node.defaults else '')+c[0].varNames[c[1]]+('' if type(c[0]) == InputNode else '()') for c in connections if c[2] == node])
                if len(node.varNames) == 1:
                    f.write(f"\t{a} = lambda: {b}.{c}({d})\n")
                elif len(node.varNames) > 1:
                    f.write(f"\t_c{count} = lambda: {b}.{c}({d})\n")
                    for i, o in enumerate(node.varNames):
                        f.write(f"\t{o} = lambda: _{count}()[{i}]\n")
                    count += 1

        f.write(f"\treturn {', '.join([c[0].varNames[c[1]]+('' if type(c[0]) == InputNode else '()') for c in connections if c[2] == outputNode])}")

def spawnFromSearch():
    global search, funcDict, nodeDict, selectedFunc, searchMousePos
    search = False
    eval(nodeDict[selectedFunc])(selectedFunc, x=searchMousePos[0], y=searchMousePos[1])

def play():
    global win, origin, funcDict, fontMedium, nodeList, startPin, endPin, connectedPins, search, options, optionNode,\
        leftClick, rightClick, mousePos, mouseButtons, connections, lineStart, fontSmall, events, selectedFunc,\
        searchMousePos, spawned, id, idDict, saveName
    previousMouse = 0,0,0
    output = False
    menu = True
    winSize = win.get_size()
    clock = pg.time.Clock()
    run = True
    while run:
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                run = False
            if event.type == pg.VIDEORESIZE:
                # center align elements
                origin[0] += (event.w-winSize[0])//2
                origin[1] += (event.h-winSize[1])//2
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
        winSize = win.get_size()

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

        if menu:
            w, h = 400, 100
            x, y = winSize[0]//2-w//2, winSize[1]//2-h//2
            pg.draw.rect(win, (10,10,10), (x, y, w, h))
            # new project
            npText = fontLarge.render('New Project', True, (255,255,255))
            npw, nph = npText.get_width()+8, npText.get_height()+8
            npx, npy = winSize[0]//2-npw-20, winSize[1]//2-nph//2

            # open project
            opText = fontLarge.render('Open Project', True, (255,255,255))
            opw, oph = opText.get_width()+8, opText.get_height()+8
            opx, opy = winSize[0]//2+20, winSize[1]//2-oph//2

            for i, t, x, y, w, h in [(0, npText, npx, npy, npw, nph), (1, opText, opx, opy, opw, oph)]:
                color = (80,80,80)
                if x-4 <= origin[0]+mousePos[0] <= x-4+w and y-4 <= origin[1]+mousePos[1] <= y-4+h:
                    color = tuple(c+50 for c in color)

                    if leftClick:
                        if i == 0:
                            menu = False
                        elif i == 1:
                            tmp = filedialog.askopenfilename(filetypes=[('PyNode Files', '*.pyn')], initialdir='')
                            # prevents glitch that locks pygame window controls
                            win = pg.display.set_mode(size=winSize,flags=pg.RESIZABLE)
                            if tmp != '':
                                openPrj(tmp)
                                menu = False
                        pg.mouse.get_rel()
                pg.draw.rect(win, color, (x-4, y-4, w, h))
                win.blit(t, (x, y))
        else:
            # dragging view around
            mouseRel = pg.mouse.get_rel()

            if not mouseButtons[0]:
                connectedPins = {}

            # test for illegal kwargs connection
            # for i, c in enumerate(connections):
            #     if c[2].inputs[c[3]] == 'kwargs':
            #         connections.pop(i)


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

            if not output:
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

            if keys[pg.K_LCTRL] and keys[pg.K_SPACE] and not output: # open search
                # initialize search pop-up
                textinput = TextInput(font_family='Consolas',
                    font_size=16,
                    text_color=(255,255,255),
                    cursor_color=(255,255,255)
                )
                searchMousePos = mousePos
                search = True
                selectedSearch = 0
                searchResults = 0
            elif keys[pg.K_LCTRL] and keys[pg.K_d] and not spawned:
                selectedFunc = nodeList[0].func
                searchMousePos = mousePos
                spawnFromSearch()
                spawned = True
            elif not (keys[pg.K_LCTRL] and keys[pg.K_d]): # duplicate node
                spawned = False

            if keys[pg.K_LCTRL] and keys[pg.K_s]: # save project
                if saveName == None or keys[pg.K_LSHIFT]:
                    search = False
                    saveName = filedialog.asksaveasfilename(filetypes=[('PyNode Files', '*.pyn')], defaultextension='*.pyn')
                    # prevents glitch that locks pygame window controls
                    win = pg.display.set_mode(size=winSize,flags=pg.RESIZABLE)
                    if saveName == '':
                        continue
                prj = [(type(n), n.func, n.inputs, n.outputs, n.x, n.y) for n in nodeList], [[c[0].id, c[1], c[2].id, c[3]] for c in connections], saveName
                with open(saveName, 'wb') as p:
                    pickle.dump(prj, p)
            elif keys[pg.K_LCTRL] and keys[pg.K_o]: # export project
                # initialize output screen
                output = True
                search = False
                standalone = True
                exportNode = False

                funcName = TextInput(font_family='Consolas',
                    font_size=24,
                    text_color=(255,255,255),
                    cursor_color=(255,255,255),
                    initial_string='Function_Name',
                    max_string_length=30
                )

            if keys[pg.K_LCTRL] and keys[pg.K_m]:
                menu = True
                output = False
                search = False

            if search:
                # render
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

                # conditions
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

                if leftClick and not (searchMousePos[0] <= mousePos[0] <= searchMousePos[0]+300 and searchMousePos[1] <= mousePos[1] <= searchMousePos[1]+40+25*searchResults):
                    search = False

            if output:
                # render
                funcName.update(events)
                w, h = 600, 400
                x, y = ((winSize[0]-w)//2), ((winSize[1]-h)//2)
                pg.draw.rect(win, (10,10,10), (x, y, w, h))

                pg.draw.rect(win, (30,30,30), (x+100-4, y+100-4, w-200+8, 24+8))
                win.blit(funcName.get_surface(), (x+100, y+100))

                # standalone (define functions in file rather than importing)
                width = 2
                color = (40,40,40)
                if standalone:
                    width = 0
                    color = (40,40,200)
                pg.draw.rect(win, color, (x+50, y+150, 25, 25), width)
                sText = fontLarge.render('Standalone', True, (255,255,255))
                win.blit(sText, (x+50+35, y+150+25//2-sText.get_height()//2+1))

                if leftClick and x+50 <= origin[0]+mousePos[0] <= x+50+25 and y+150 <= origin[1]+mousePos[1] <= y+150+25:
                    if standalone:
                        standalone = False
                    else:
                        standalone = True

                # export as node (add function to node library)
                width = 2
                color = (40,40,40)
                if exportNode:
                    width = 0
                    color = (40,40,200)
                pg.draw.rect(win, color, (x+50, y+200, 25, 25), width)
                sText = fontLarge.render('Export as node', True, (255,255,255))
                win.blit(sText, (x+50+35, y+200+25//2-sText.get_height()//2+1))

                if leftClick and x+50 <= origin[0]+mousePos[0] <= x+50+25 and y+200 <= origin[1]+mousePos[1] <= y+200+25:
                    if exportNode:
                        exportNode = False
                    else:
                        exportNode = True

                # export button
                exportText = fontLarge.render('Export', True, (255,255,255))
                ex, ey = x+(w//4-exportText.get_width()//2), y+h-75
                ew, eh = exportText.get_width()+8, exportText.get_height()+8
                color = (30,30,200)
                if ex <= origin[0]+mousePos[0] <= ex+ew and ey <= origin[1]+mousePos[1] <= ey+eh:
                    color = tuple(min(255, c+50) for c in color)
                    if leftClick:
                        if exportNode:
                            name = filedialog.askopenfilename(filetypes=[('Python Files', '*.py')], initialdir='lib')
                        else:
                            name = filedialog.asksaveasfilename(filetypes=[('Python Files', '*.py')], defaultextension='*.py')
                        # prevents glitch that locks pygame window controls
                        win = pg.display.set_mode(size=winSize,flags=pg.RESIZABLE)
                        if name != '':
                            export(name, funcName.get_text(), standalone, exportNode)
                            output = False
                pg.draw.rect(win, color, (ex-4, ey-4, ew, eh))
                win.blit(exportText, (ex,ey))

                # cancel button
                cancelText = fontLarge.render('Cancel', True, (255,255,255))
                cx, cy = x+(w*3//4-cancelText.get_width()//2), y+h-75
                cw, ch = cancelText.get_width()+8, cancelText.get_height()+8
                color = (75,75,75)
                if cx <= origin[0]+mousePos[0] <= cx+cw and cy <= origin[1]+mousePos[1] <= cy+ch:
                    color = tuple(min(255, c+50) for c in color)
                    if leftClick:
                        output = False
                pg.draw.rect(win, color, (cx-4, cy-4, cw, ch))
                win.blit(cancelText, (cx,cy))

                # conditions
                if keys[pg.K_ESCAPE] or (leftClick and not (x <= origin[0]+mousePos[0] <= x+w and y <= origin[1]+mousePos[1] <= y+h)):
                    output = False

        # print(clock.get_fps())
        pg.display.update()
        # clock.tick()

    pg.quit()
    exit()
