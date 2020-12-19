from pygame_textinput import TextInput # <- NOT made by me, a community plugin for pygame
# https://github.com/Nearoo/pygame-text-input
# any code initializing or calling methods from a 'TextInput' object are utilizing the above resource

import pygame as pg # <- NOT made by a me, a large python library for displaying real time graphics and interactive elements
# https://www.pygame.org/wiki/about
# any code under 'pg.' is utilizing objects, methods, and constants from the above resource

import inspect
import main

class Node:
    def __init__(self, func, x=0, y=0):
        self.id = main.id
        main.idDict[self.id] = self
        main.id += 1
        self.func = func
        self.name = func.__name__
        self.label = main.fontMedium.render(self.name, True, (10,10,10))
        self.inputs = list(inspect.signature(func).parameters.keys())
        self.outputs = main.funcDict[func]
        signature = inspect.signature(func)
        self.defaults = list({k: v.default for k, v in signature.parameters.items() if v.default is not inspect.Parameter.empty}.keys())
        self.kwargList = []
        if 'kwargs' in self.inputs:
            self.kwargs = True
        else:
            self.kwargs = False
        self.x, self.y = x, y
        self.updateSize()
        self.bounds = [self.x, self.x+self.w, self.y, self.y+self.h]

        main.nodeList.insert(0, self)
        self.color = 255,255,255
        self.editing = -1

    def updateSize(self):
        self.w, self.h = self.label.get_width()+50, 50+25*max(len(self.outputs), len(self.inputs))
        self.bounds = [self.x, self.x+self.w, self.y, self.y+self.h]

    def move(self, x, y):
        self.x, self.y = x, y
        self.bounds = [x, x+self.w, y, y+self.h]

    def render(self):
        pg.draw.rect(main.win, (10,10,10), (main.origin[0]+self.x-2, main.origin[1]+self.y-2, self.w+4, self.h+4))
        pg.draw.rect(main.win, self.color, (main.origin[0]+self.x, main.origin[1]+self.y, self.w, self.h))

        if 'args' in self.inputs:
            if len(self.inputs)-self.inputs[::-1].index('args')-1 in [c[3] for c in main.connections if c[2] == self and self.inputs[c[3]] == 'args']:
                self.inputs.insert(len(self.inputs)-self.inputs[::-1].index('args')-1, 'args')
                self.updateSize()

        if self.kwargs and 'kwargs' not in self.inputs:
            self.inputs.append('kwargs')
            self.updateSize()
        elif self.kwargs and len([i for i in self.inputs if i == 'kwargs']) > 1:
            self.inputs.pop(len(self.inputs)-self.inputs[::-1].index('kwargs')-1)
            self.updateSize()

        for i in range(len(self.inputs)):
            # determine if args needs to be removed
            if not main.mouseButtons[0]:
                tmp = [c[3] for c in main.connections if c[2] == self and self.inputs[c[3]] == 'args']
                if self.inputs[i] == 'args' and i not in tmp and (len([i for i in self.inputs if i == 'args'])-len(tmp)) > 1:
                    self.inputs.pop(i)
                    self.updateSize()
                    main.connections = [[c[0], c[1], c[2], c[3]-1] if c[2] == self and c[3] > i else c for c in main.connections]
                    break
            # color stuff
            red = 100
            green = 250
            blue = 100
            if (self,i) not in [(c[2], c[3]) for c in main.connections]:
                if self.inputs[i] in self.defaults:
                    red = 250
                    green = 200
                elif self.inputs[i] == 'args':
                    red = 50
                    green = 150
                    blue = 250
                elif self.inputs[i] == 'kwargs':
                    red = 250
                    green = 50
                    blue = 250
                else:
                    red = 250
                    green = 100

            color = (red,green,blue)

            # general stuff
            if self.x-10 <= main.mousePos[0] <= self.x+10 and self.y+50+i*25-10 <= main.mousePos[1] <= self.y+50+i*25+10 and not main.moving:
                if main.mouseButtons[0] and main.startPin != (self,0,i) and (self,i) not in [(c[2],c[3]) for c in main.connections] and self.inputs[i] != 'kwargs':
                    main.endPin = (self,0,i)
                elif main.mouseButtons[0] and main.leftClick and (self,i) in [(c[2],c[3]) for c in main.connections]:
                    tmp = [c for c in main.connections if (c[2],c[3]) == (self,i)][0]
                    main.lineStart = tmp[0].x+tmp[0].w, tmp[0].y+50+tmp[1]*25-1
                    main.startPin = tmp[0],tmp[0].w,tmp[1]
                    main.connections.remove(tmp)
                elif main.mousePos and main.startPin == None or main.startPin[1] == 0:
                    main.startPin = (self,0,i)
            elif main.endPin == (self,0,i) and not main.moving:
                main.endPin = None
            elif (self, 0, i) not in [val for key, val in main.connectedPins.items()] or main.moving:
                color = (max(0,red-50),max(0,green-50),max(0,blue-50))

            pg.draw.rect(main.win, color, (main.origin[0]+self.x-5, main.origin[1]+self.y-5+50+i*25, 10, 10))

            text = main.fontSmall.render(self.inputs[i], True, (10,10,10))
            if self.inputs[i] == 'kwargs' or self.inputs[i] in self.kwargList:
                if not self.editing == i:
                    if self.x+10 <= main.mousePos[0] <= self.x+10+text.get_width() and self.y-5+50+i*25 <= main.mousePos[1] <= self.y-5+50+i*25+text.get_height():
                        if main.leftClick:
                            self.textinput = TextInput(font_family='Consolas',font_size=12, text_color=(0,0,0), initial_string=self.inputs[i])
                            self.editing = i
                else:
                    text = self.textinput.get_surface()
                    if self.textinput.update(main.events):
                        self.editing = -1
                        if self.textinput.get_text() == '':
                            self.inputs[i] = 'kwargs'
                        else:
                            self.inputs[i] = self.textinput.get_text()
                            self.kwargList.append(self.textinput.get_text())

            main.win.blit(text, (main.origin[0]+self.x+10, main.origin[1]+self.y-5+50+i*25))

        for i in range(len(self.outputs)):
            # color stuff
            color = (150,150,250)
            if self.x+self.w-10 <= main.mousePos[0] <= self.x+self.w+10 and self.y+50+i*25-10 <= main.mousePos[1] <= self.y+50+i*25+10 and not main.moving:
                if main.mouseButtons[0] and main.startPin != (self,self.w,i):
                    main.endPin = (self,self.w,i)
                else:
                    main.startPin = (self,self.w,i)
            elif main.endPin == (self,self.w,i) and not main.moving:
                main.endPin = None
            elif (self, self.w, i) not in [val for key, val in main.connectedPins.items()] or main.moving:
                color = (100,100,200)

            pg.draw.rect(main.win, color, (main.origin[0]+self.x+self.w-5, main.origin[1]+self.y-5+50+i*25, 10, 10))
            text = main.fontSmall.render(self.outputs[i], True, (10,10,10))
            main.win.blit(text, (main.origin[0]+self.x+self.w-10-text.get_width(), main.origin[1]+self.y-5+50+i*25))

        # general stuff
        if self.x+self.w-20 <= main.mousePos[0] <= self.x+self.w-2 and self.y+2 <= main.mousePos[1] <= self.y+18 and main.nodeList[0] == self:
            if main.leftClick and main.startPin == None:
                main.nodeList.pop(0)
                [main.connections.remove(c) for c in main.connections[::-1] if c[0] == self or c[2] == self]
            pg.draw.rect(main.win, (220,100,100), (main.origin[0]+self.x+self.w-20,main.origin[1]+self.y+2, 18,18))
            xColor = (255,255,255)
        else:
            xColor = (100,100,100)

        pg.draw.line(main.win, xColor, (main.origin[0]+self.x+self.w-16-1, main.origin[1]+self.y+6-1), (main.origin[0]+self.x+self.w-6-1, main.origin[1]+self.y+16-1), 2)
        pg.draw.line(main.win, xColor, (main.origin[0]+self.x+self.w-16-1, main.origin[1]+self.y+16-1), (main.origin[0]+self.x+self.w-6-1, main.origin[1]+self.y+6-1), 2)

        main.win.blit(self.label, (main.origin[0]+self.x+10, main.origin[1]+self.y+10))

class InputNode:
    def __init__(self, func=None, x=0, y=0):
        self.id = main.id
        main.idDict[self.id] = self
        main.id += 1
        self.name = "Inputs"
        self.label = main.fontMedium.render(self.name, True, (10,10,10))
        self.func = func
        self.inputs = []
        self.outputs = []
        self.func = None
        self.x, self.y = x, y
        self.w, self.h = self.label.get_width()+75, 50+25*len(self.outputs)
        self.bounds = [self.x, self.x+self.w, self.y, self.y+self.h]

        main.nodeList.insert(0, self)
        self.color = 255,255,255
        self.editing = -1
        self.kwargs = False

    def updateSize(self):
        self.w, self.h = self.label.get_width()+75, 50+25*max(len(self.outputs), len(self.inputs))
        self.bounds = [self.x, self.x+self.w, self.y, self.y+self.h]

    def move(self, x, y):
        self.x, self.y = x, y
        self.bounds = [x, x+self.w, y, y+self.h]

    def render(self):
        pg.draw.rect(main.win, (10,10,10), (main.origin[0]+self.x-2, main.origin[1]+self.y-2, self.w+4, self.h+4))
        pg.draw.rect(main.win, self.color, (main.origin[0]+self.x, main.origin[1]+self.y, self.w, self.h))

        for i in range(len(self.outputs)):
            color = (150,150,250)
            if self.x+self.w-10 <= main.mousePos[0] <= self.x+self.w+10 and self.y+50+i*25-10 <= main.mousePos[1] <= self.y+50+i*25+10 and not main.moving:
                if main.mouseButtons[0] and main.startPin != (self,self.w,i):
                    main.endPin = (self,self.w,i)
                else:
                    main.startPin = (self,self.w,i)
            elif main.endPin == (self,self.w,i) and not main.moving:
                main.endPin = None
            elif (self, self.w, i) not in [val for key, val in main.connectedPins.items()] or main.moving:
                color = (100,100,200)

            pg.draw.rect(main.win, color, (main.origin[0]+self.x+self.w-5, main.origin[1]+self.y-5+50+i*25, 10, 10))
            text = main.fontSmall.render(self.outputs[i], True, (10,10,10))
            if not self.editing == i:
                if self.x+self.w-10-text.get_width() <= main.mousePos[0] <= self.x+self.w-10 and self.y-5+50+i*25 <= main.mousePos[1] <= self.y-5+50+i*25+text.get_height():
                    if main.leftClick:
                        self.textinput = TextInput(font_family='Consolas',font_size=12, text_color=(0,0,0), initial_string=self.outputs[i])
                        self.editing = i
            else:
                text = self.textinput.get_surface()
                if self.textinput.update(main.events):
                    self.editing = -1
                    if self.textinput.get_text() != '':
                        self.outputs[i] = self.textinput.get_text()
            main.win.blit(text, (main.origin[0]+self.x+self.w-10-text.get_width(), main.origin[1]+self.y-5+50+i*25))

        bSize = 20
        mPos = self.x+self.w-8-bSize*2, self.y+8
        pPos = self.x+self.w-8-bSize, self.y+8


        if mPos[0] <= main.mousePos[0] < mPos[0]+bSize and mPos[1] <= main.mousePos[1] <= mPos[1]+bSize:
            color = (80,80,80)
            if main.leftClick and len(self.outputs) > 0:
                [main.connections.remove(c) for c in main.connections[::-1] if c[1] == len(self.outputs)-1 and c[0] == self]
                self.outputs.pop()
                self.w, self.h = self.label.get_width()+75, 50+25*len(self.outputs)
        else:
            color = (40,40,40)
        pg.draw.rect(main.win, color, (main.origin[0]+mPos[0], main.origin[1]+mPos[1], bSize, bSize))
        pg.draw.line(main.win, (255,255,255), (main.origin[0]+mPos[0]+4, main.origin[1]+mPos[1]+bSize//2-1), (main.origin[0]+mPos[0]+14, main.origin[1]+mPos[1]+bSize//2-1), 2)
        if pPos[0] <= main.mousePos[0] < pPos[0]+bSize and pPos[1] <= main.mousePos[1] <= pPos[1]+bSize:
            color = (80,80,80)
            if main.leftClick:
                self.outputs.append(f'i{len(self.outputs)+1}')
                self.w, self.h = self.label.get_width()+75, 50+25*len(self.outputs)
        else:
            color = (40,40,40)
        pg.draw.rect(main.win, color, (main.origin[0]+pPos[0], main.origin[1]+pPos[1], bSize, bSize))
        pg.draw.line(main.win, (255,255,255), (main.origin[0]+pPos[0]+4, main.origin[1]+pPos[1]+bSize//2-1), (main.origin[0]+pPos[0]+14, main.origin[1]+pPos[1]+bSize//2-1), 2)
        pg.draw.line(main.win, (255,255,255), (main.origin[0]+pPos[0]+bSize//2-1, main.origin[1]+pPos[1]+4), (main.origin[0]+pPos[0]+bSize//2-1, main.origin[1]+pPos[1]+14), 2)

        main.win.blit(self.label, (main.origin[0]+self.x+10, main.origin[1]+self.y+10))

class OutputNode:
    def __init__(self, func=None, x=0, y=0):
        self.id = main.id
        main.idDict[self.id] = self
        main.id += 1
        self.name = "Outputs"
        self.label = main.fontMedium.render(self.name, True, (10,10,10))
        self.func = func
        self.inputs = []
        self.outputs = []
        self.func = None
        self.x, self.y = x, y
        self.w, self.h = self.label.get_width()+75, 50+25*len(self.inputs)
        self.bounds = [self.x, self.x+self.w, self.y, self.y+self.h]

        main.nodeList.insert(0, self)
        self.color = 255,255,255
        self.editing = -1
        self.kwargs = False

    def updateSize(self):
        self.w, self.h = self.label.get_width()+75, 50+25*max(len(self.outputs), len(self.inputs))
        self.bounds = [self.x, self.x+self.w, self.y, self.y+self.h]

    def move(self, x, y):
        self.x, self.y = x, y
        self.bounds = [x, x+self.w, y, y+self.h]

    def render(self):
        pg.draw.rect(main.win, (10,10,10), (main.origin[0]+self.x-2, main.origin[1]+self.y-2, self.w+4, self.h+4))
        pg.draw.rect(main.win, self.color, (main.origin[0]+self.x, main.origin[1]+self.y, self.w, self.h))

        for i in range(len(self.inputs)):
            # color stuff
            red = 100
            green = 250
            blue = 100
            if (self,i) not in [(c[2], c[3]) for c in main.connections]:
                red = 250
                green = 100

            color = (red,green,blue)
            if self.x-10 <= main.mousePos[0] <= self.x+10 and self.y+50+i*25-10 <= main.mousePos[1] <= self.y+50+i*25+10 and not main.moving:
                if main.mouseButtons[0] and main.startPin != (self,0,i) and (self,i) not in [(c[2],c[3]) for c in main.connections]:
                    main.endPin = (self,0,i)
                elif main.mouseButtons[0] and (self,i) in [(c[2],c[3]) for c in main.connections]:
                    tmp = [c for c in main.connections if (c[2],c[3]) == (self,i)][0]
                    main.lineStart = tmp[0].x+tmp[0].w, tmp[0].y+50+tmp[1]*25-1
                    main.startPin = tmp[0],tmp[0].w,tmp[1]
                    main.connections.remove(tmp)
                else:
                    main.startPin = (self,0,i)
            elif main.endPin == (self,0,i) and not main.moving:
                main.endPin = None
            elif (self, 0, i) not in [val for key, val in main.connectedPins.items()] or main.moving:
                color = (max(0,red-50),max(0,green-50),max(0,blue-50))

            pg.draw.rect(main.win, color, (main.origin[0]+self.x-5, main.origin[1]+self.y-5+50+i*25, 10, 10))
            text = main.fontSmall.render(self.inputs[i], True, (10,10,10))
            if not self.editing == i:
                if self.x+10 <= main.mousePos[0] <= self.x+10+text.get_width() and self.y-5+50+i*25 <= main.mousePos[1] <= self.y-5+50+i*25+text.get_height():
                    if main.leftClick:
                        self.textinput = TextInput(font_family='Consolas',font_size=12, text_color=(0,0,0), initial_string=self.inputs[i])
                        self.editing = i
            else:
                text = self.textinput.get_surface()
                if self.textinput.update(main.events):
                    self.editing = -1
                    if self.textinput.get_text() != '':
                        self.inputs[i] = self.textinput.get_text()
            main.win.blit(text, (main.origin[0]+self.x+10, main.origin[1]+self.y-5+50+i*25))


        bSize = 20
        mPos = self.x+self.w-8-bSize*2, self.y+8
        pPos = self.x+self.w-8-bSize, self.y+8


        if mPos[0] <= main.mousePos[0] < mPos[0]+bSize and mPos[1] <= main.mousePos[1] <= mPos[1]+bSize:
            color = (80,80,80)
            if main.leftClick and len(self.inputs) > 0:
                [main.connections.remove(c) for c in main.connections[::-1] if c[3] == len(self.inputs)-1 and c[2] == self]
                self.inputs.pop()
                self.w, self.h = self.label.get_width()+75, 50+25*len(self.inputs)
        else:
            color = (40,40,40)
        pg.draw.rect(main.win, color, (main.origin[0]+mPos[0], main.origin[1]+mPos[1], bSize, bSize))
        pg.draw.line(main.win, (255,255,255), (main.origin[0]+mPos[0]+4, main.origin[1]+mPos[1]+bSize//2-1), (main.origin[0]+mPos[0]+14, main.origin[1]+mPos[1]+bSize//2-1), 2)
        if pPos[0] <= main.mousePos[0] < pPos[0]+bSize and pPos[1] <= main.mousePos[1] <= pPos[1]+bSize:
            color = (80,80,80)
            if main.leftClick:
                self.inputs.append(f'o{len(self.inputs)+1}')
                self.w, self.h = self.label.get_width()+75, 50+25*len(self.inputs)
        else:
            color = (40,40,40)
        pg.draw.rect(main.win, color, (main.origin[0]+pPos[0], main.origin[1]+pPos[1], bSize, bSize))
        pg.draw.line(main.win, (255,255,255), (main.origin[0]+pPos[0]+4, main.origin[1]+pPos[1]+bSize//2-1), (main.origin[0]+pPos[0]+14, main.origin[1]+pPos[1]+bSize//2-1), 2)
        pg.draw.line(main.win, (255,255,255), (main.origin[0]+pPos[0]+bSize//2-1, main.origin[1]+pPos[1]+4), (main.origin[0]+pPos[0]+bSize//2-1, main.origin[1]+pPos[1]+14), 2)

        main.win.blit(self.label, (main.origin[0]+self.x+10, main.origin[1]+self.y+10))

class ConstantNode:
    def __init__(self, func=None, x=0, y=0):
        self.id = main.id
        main.idDict[self.id] = self
        main.id += 1
        self.name = "Constant"
        self.label = main.fontMedium.render(self.name, True, (10,10,10))
        self.func = func
        self.inputs = []
        self.outputs = []
        self.values = []
        self.x, self.y = x, y
        self.w, self.h = self.label.get_width()+100, 50+25*len(self.outputs)
        self.bounds = [self.x, self.x+self.w, self.y, self.y+self.h]

        main.nodeList.insert(0, self)
        self.color = 255,255,255
        self.editing = -1
        self.entering = -1
        self.kwargs = False

    def updateSize(self, w=None):
        if w == None:
            w = self.label.get_width()+100
        self.w, self.h = w, 50+25*max(len(self.outputs), len(self.inputs))
        self.bounds = [self.x, self.x+self.w, self.y, self.y+self.h]

    def move(self, x, y):
        self.x, self.y = x, y
        self.bounds = [x, x+self.w, y, y+self.h]

    def render(self):
        pg.draw.rect(main.win, (10,10,10), (main.origin[0]+self.x-2, main.origin[1]+self.y-2, self.w+4, self.h+4))
        pg.draw.rect(main.win, self.color, (main.origin[0]+self.x, main.origin[1]+self.y, self.w, self.h))

        for i in range(len(self.outputs)):
            color = (150,150,250)
            if self.x+self.w-10 <= main.mousePos[0] <= self.x+self.w+10 and self.y+50+i*25-10 <= main.mousePos[1] <= self.y+50+i*25+10 and not main.moving:
                if main.mouseButtons[0] and main.startPin != (self,self.w,i):
                    main.endPin = (self,self.w,i)
                else:
                    main.startPin = (self,self.w,i)
            elif main.endPin == (self,self.w,i) and not main.moving:
                main.endPin = None
            elif (self, self.w, i) not in [val for key, val in main.connectedPins.items()] or main.moving:
                color = (100,100,200)

            pg.draw.rect(main.win, color, (main.origin[0]+self.x+self.w-5, main.origin[1]+self.y-5+50+i*25, 10, 10))
            text = main.fontSmall.render(self.outputs[i], True, (10,10,10))
            if not self.editing == i:
                if self.x+self.w-10-text.get_width() <= main.mousePos[0] <= self.x+self.w-10 and self.y-5+50+i*25 <= main.mousePos[1] <= self.y-5+50+i*25+text.get_height():
                    if main.leftClick:
                        self.textinput = TextInput(font_family='Consolas',font_size=12, text_color=(0,0,0), initial_string=self.outputs[i])
                        self.editing = i
            else:
                text = self.textinput.get_surface()
                if self.textinput.update(main.events):
                    self.editing = -1
                    if self.textinput.get_text() != '':
                        self.outputs[i] = self.textinput.get_text()
            main.win.blit(text, (main.origin[0]+self.x+self.w-10-text.get_width(), main.origin[1]+self.y-5+50+i*25))
            x, y = main.origin[0]+self.x+5, main.origin[1]+self.y-5+50+i*25-3
            w, h = self.w-10-text.get_width()-10, 18
            pg.draw.rect(main.win, (40, 40, 40), (x, y, w, h))
            text = main.fontSmall.render(self.values[i], True, (255,255,255))
            if main.leftClick:
                if x <= main.origin[0]+main.mousePos[0] <= x+w and y <= main.origin[1]+main.mousePos[1] <= y+h:
                    self.entering = i
                    self.textinput2 = TextInput(font_family='Consolas',
                        font_size=12,
                        text_color=(255,255,255),
                        cursor_color=(255,255,255),
                        initial_string=self.values[i]
                    )
            if self.entering == i:
                text = self.textinput2.get_surface()
                if self.textinput2.update(main.events):
                    self.updateSize(w=max(self.label.get_width()+100, text.get_width()+50))
                    if self.textinput2.get_text() != '':
                        self.values[i] = self.textinput2.get_text()
                    self.entering = -1
            main.win.blit(text, (x+w//2-text.get_width()//2, y+2))

        bSize = 20
        mPos = self.x+self.w-8-24-bSize*2, self.y+8
        pPos = self.x+self.w-8-24-bSize, self.y+8

        if mPos[0] <= main.mousePos[0] < mPos[0]+bSize and mPos[1] <= main.mousePos[1] <= mPos[1]+bSize:
            color = (80,80,80)
            if main.leftClick and len(self.outputs) > 0:
                [main.connections.remove(c) for c in main.connections[::-1] if c[1] == len(self.outputs)-1]
                self.outputs.pop()
                self.values.pop()
                self.w, self.h = self.label.get_width()+100, 50+25*len(self.outputs)
        else:
            color = (40,40,40)
        pg.draw.rect(main.win, color, (main.origin[0]+mPos[0], main.origin[1]+mPos[1], bSize, bSize))
        pg.draw.line(main.win, (255,255,255), (main.origin[0]+mPos[0]+4, main.origin[1]+mPos[1]+bSize//2-1), (main.origin[0]+mPos[0]+14, main.origin[1]+mPos[1]+bSize//2-1), 2)
        if pPos[0] <= main.mousePos[0] < pPos[0]+bSize and pPos[1] <= main.mousePos[1] <= pPos[1]+bSize:
            color = (80,80,80)
            if main.leftClick:
                self.outputs.append(f'c{len(self.outputs)+1}')
                self.values.append('0')
                self.w, self.h = self.label.get_width()+100, 50+25*len(self.outputs)
        else:
            color = (40,40,40)
        pg.draw.rect(main.win, color, (main.origin[0]+pPos[0], main.origin[1]+pPos[1], bSize, bSize))
        pg.draw.line(main.win, (255,255,255), (main.origin[0]+pPos[0]+4, main.origin[1]+pPos[1]+bSize//2-1), (main.origin[0]+pPos[0]+14, main.origin[1]+pPos[1]+bSize//2-1), 2)
        pg.draw.line(main.win, (255,255,255), (main.origin[0]+pPos[0]+bSize//2-1, main.origin[1]+pPos[1]+4), (main.origin[0]+pPos[0]+bSize//2-1, main.origin[1]+pPos[1]+14), 2)

        if self.x+self.w-20 <= main.mousePos[0] <= self.x+self.w-2 and self.y+2 <= main.mousePos[1] <= self.y+18 and main.nodeList[0] == self:
            if main.leftClick and main.startPin == None:
                main.nodeList.pop(0)
                [main.connections.remove(c) for c in main.connections[::-1] if c[0] == self or c[2] == self]
            pg.draw.rect(main.win, (220,100,100), (main.origin[0]+self.x+self.w-20,main.origin[1]+self.y+2, 18,18))
            xColor = (255,255,255)
        else:
            xColor = (100,100,100)

        pg.draw.line(main.win, xColor, (main.origin[0]+self.x+self.w-16-1, main.origin[1]+self.y+6-1), (main.origin[0]+self.x+self.w-6-1, main.origin[1]+self.y+16-1), 2)
        pg.draw.line(main.win, xColor, (main.origin[0]+self.x+self.w-16-1, main.origin[1]+self.y+16-1), (main.origin[0]+self.x+self.w-6-1, main.origin[1]+self.y+6-1), 2)

        main.win.blit(self.label, (main.origin[0]+self.x+10, main.origin[1]+self.y+10))
