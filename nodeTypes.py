from pygame_textinput import TextInput # <- NOT made by me, a community plugin for pygame
import pygame as pg
import inspect
import main

class Node:
    def __init__(self, func, x=0, y=0):
        self.func = func
        self.name = func.__name__
        self.label = main.fontMedium.render(self.name, True, (10,10,10))
        self.inputs = [i for i in func.__code__.co_varnames]
        self.outputs = main.funcDict[func]
        signature = inspect.signature(func)
        self.defaults = list({k: v.default for k, v in signature.parameters.items() if v.default is not inspect.Parameter.empty}.keys())
        self.x, self.y = x, y
        self.w, self.h = self.label.get_width()+50, 50+25*max(len(self.outputs), len(self.inputs))
        self.bounds = [self.x, self.x+self.w, self.y, self.y+self.h]

        main.nodeList.insert(0, self)
        self.color = 255,255,255

    def move(self, x, y):
        self.x, self.y = x, y
        self.bounds = [x, x+self.w, y, y+self.h]

    def render(self):
        pg.draw.rect(main.win, (10,10,10), (main.origin[0]+self.x-2, main.origin[1]+self.y-2, self.w+4, self.h+4))
        pg.draw.rect(main.win, self.color, (main.origin[0]+self.x, main.origin[1]+self.y, self.w, self.h))

        for i in range(len(self.inputs)):
            red = 150
            green = 150
            if (self,i) not in [(c[2], c[3]) for c in main.connections]:
                if self.inputs[i] in self.defaults:
                    red = 250
                    green = 200
                else:
                    red = 250
                    green = 150
            else:
                green = 200

            color = (red,green,150)
            if self.x-10 <= main.mousePos[0] <= self.x+10 and self.y+50+i*25-10 <= main.mousePos[1] <= self.y+50+i*25+10:
                if main.mouseButtons[0] and main.startPin != (self,0,i) and (self,i) not in [(c[2],c[3]) for c in main.connections]:
                    main.endPin = (self,0,i)
                elif main.mouseButtons[0] and (self,i) in [(c[2],c[3]) for c in main.connections]:
                    tmp = [c for c in main.connections if (c[2],c[3]) == (self,i)][0]
                    main.lineStart = tmp[0].x+tmp[0].w, tmp[0].y+50+tmp[1]*25-1
                    main.startPin = tmp[0],tmp[0].w,tmp[1]
                    main.connections.remove(tmp)
                else:
                    main.startPin = (self,0,i)
            elif main.endPin == (self,0,i):
                main.endPin = None
            elif (self, 0, i) not in [val for key, val in main.connectedPins.items()]:
                color = (red-50,green-50,100)

            pg.draw.rect(main.win, color, (main.origin[0]+self.x-5, main.origin[1]+self.y-5+50+i*25, 10, 10))
            main.win.blit(main.fontSmall.render(self.inputs[i], True, (10,10,10)), (main.origin[0]+self.x+10, main.origin[1]+self.y-5+50+i*25))

        for i in range(len(self.outputs)):
            color = (150,150,250)
            if self.x+self.w-10 <= main.mousePos[0] <= self.x+self.w+10 and self.y+50+i*25-10 <= main.mousePos[1] <= self.y+50+i*25+10:
                if main.mouseButtons[0] and main.startPin != (self,self.w,i):
                    main.endPin = (self,self.w,i)
                else:
                    main.startPin = (self,self.w,i)
            elif main.endPin == (self,self.w,i):
                main.endPin = None
            elif (self, self.w, i) not in [val for key, val in main.connectedPins.items()]:
                color = (100,100,200)

            pg.draw.rect(main.win, color, (main.origin[0]+self.x+self.w-5, main.origin[1]+self.y-5+50+i*25, 10, 10))
            text = main.fontSmall.render(self.outputs[i], True, (10,10,10))
            main.win.blit(text, (main.origin[0]+self.x+self.w-10-text.get_width(), main.origin[1]+self.y-5+50+i*25))

        if self.x+self.w-20 <= main.mousePos[0] <= self.x+self.w-2 and self.y+2 <= main.mousePos[1] <= self.y+18:
            if main.leftClick and main.startPin == None and main.nodeList[0] == self:
                main.nodeList.pop(0)
                [main.connections.remove(c) for c in main.connections[::-1] if c[0] == self or c[2] == self]
            pg.draw.rect(main.win, (220,100,100), (main.origin[0]+self.x+self.w-20,main.origin[1]+self.y+2, 18,18))
            xColor = (255,255,255)
        else:
            xColor = (100,100,100)

        main.win.blit(self.label, (main.origin[0]+self.x+10, main.origin[1]+self.y+10))

        pg.draw.line(main.win, xColor, (main.origin[0]+self.x+self.w-16-1, main.origin[1]+self.y+6-1), (main.origin[0]+self.x+self.w-6-1, main.origin[1]+self.y+16-1), 2)
        pg.draw.line(main.win, xColor, (main.origin[0]+self.x+self.w-16-1, main.origin[1]+self.y+16-1), (main.origin[0]+self.x+self.w-6-1, main.origin[1]+self.y+6-1), 2)

class InputNode:
    def __init__(self, x=0, y=0):
        self.name = "Inputs"
        self.label = main.fontMedium.render(self.name, True, (10,10,10))
        # self.inputs = []
        self.outputs = []
        self.func = None
        self.x, self.y = x, y
        self.w, self.h = self.label.get_width()+75, 50+25*len(self.outputs)
        self.bounds = [self.x, self.x+self.w, self.y, self.y+self.h]

        main.nodeList.insert(0, self)
        self.color = 255,255,255
        self.editing = -1

    def move(self, x, y):
        self.x, self.y = x, y
        self.bounds = [x, x+self.w, y, y+self.h]

    def render(self):
        pg.draw.rect(main.win, (10,10,10), (main.origin[0]+self.x-2, main.origin[1]+self.y-2, self.w+4, self.h+4))
        pg.draw.rect(main.win, self.color, (main.origin[0]+self.x, main.origin[1]+self.y, self.w, self.h))

        for i in range(len(self.outputs)):
            color = (150,150,250)
            if self.x+self.w-10 <= main.mousePos[0] <= self.x+self.w+10 and self.y+50+i*25-10 <= main.mousePos[1] <= self.y+50+i*25+10:
                if main.mouseButtons[0] and main.startPin != (self,self.w,i):
                    main.endPin = (self,self.w,i)
                else:
                    main.startPin = (self,self.w,i)
            elif main.endPin == (self,self.w,i):
                main.endPin = None
            elif (self, self.w, i) not in [val for key, val in main.connectedPins.items()]:
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
                [main.connections.remove(c) for c in main.connections[::-1] if c[1] == len(self.outputs)-1]
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
    def __init__(self, x=0, y=0):
        self.name = "Outputs"
        self.label = main.fontMedium.render(self.name, True, (10,10,10))
        self.inputs = []
        self.func = None
        self.x, self.y = x, y
        self.w, self.h = self.label.get_width()+75, 50+25*len(self.inputs)
        self.bounds = [self.x, self.x+self.w, self.y, self.y+self.h]

        main.nodeList.insert(0, self)
        self.color = 255,255,255
        self.editing = -1

    def move(self, x, y):
        self.x, self.y = x, y
        self.bounds = [x, x+self.w, y, y+self.h]

    def render(self):
        pg.draw.rect(main.win, (10,10,10), (main.origin[0]+self.x-2, main.origin[1]+self.y-2, self.w+4, self.h+4))
        pg.draw.rect(main.win, self.color, (main.origin[0]+self.x, main.origin[1]+self.y, self.w, self.h))

        for i in range(len(self.inputs)):
            red = 150
            green = 150
            if (self,i) not in [(c[2], c[3]) for c in main.connections]:
                red = 250
                green = 150
            else:
                green = 200

            color = (red,green,150)
            if self.x-10 <= main.mousePos[0] <= self.x+10 and self.y+50+i*25-10 <= main.mousePos[1] <= self.y+50+i*25+10:
                if main.mouseButtons[0] and main.startPin != (self,0,i) and (self,i) not in [(c[2],c[3]) for c in main.connections]:
                    main.endPin = (self,0,i)
                elif main.mouseButtons[0] and (self,i) in [(c[2],c[3]) for c in main.connections]:
                    tmp = [c for c in main.connections if (c[2],c[3]) == (self,i)][0]
                    main.lineStart = tmp[0].x+tmp[0].w, tmp[0].y+50+tmp[1]*25-1
                    main.startPin = tmp[0],tmp[0].w,tmp[1]
                    main.connections.remove(tmp)
                else:
                    main.startPin = (self,0,i)
            elif main.endPin == (self,0,i):
                main.endPin = None
            elif (self, 0, i) not in [val for key, val in main.connectedPins.items()]:
                color = (red-50,green-50,100)

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
                [main.connections.remove(c) for c in main.connections[::-1] if c[3] == len(self.inputs)-1]
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

class ValueNode:
    def __init__(self, func, x=0, y=0):
        self.name = "Value"
        self.label = main.fontMedium.render(self.name, True, (10,10,10))
        self.inputs = []
        self.outputs = []
        self.x, self.y = x, y
        self.w, self.h = self.label.get_width()+75, 50+25*len(self.outputs)
        self.bounds = [self.x, self.x+self.w, self.y, self.y+self.h]

        main.nodeList.insert(0, self)
        self.color = 255,255,255
        self.editing = -1

    def move(self, x, y):
        self.x, self.y = x, y
        self.bounds = [x, x+self.w, y, y+self.h]

    def render(self):
        pg.draw.rect(main.win, (10,10,10), (main.origin[0]+self.x-2, main.origin[1]+self.y-2, self.w+4, self.h+4))
        pg.draw.rect(main.win, self.color, (main.origin[0]+self.x, main.origin[1]+self.y, self.w, self.h))

        for i in range(len(self.outputs)):
            color = (150,150,150)
            if self.x+self.w-10 <= main.mousePos[0] <= self.x+self.w+10 and self.y+50+i*25-10 <= main.mousePos[1] <= self.y+50+i*25+10:
                if main.mouseButtons[0] and main.startPin != (self,self.w,i):
                    main.endPin = (self,self.w,i)
                else:
                    main.startPin = (self,self.w,i)
            elif main.endPin == (self,self.w,i):
                main.endPin = None
            elif (self, self.w, i) not in [val for key, val in main.connectedPins.items()]:
                color = (100,100,100)

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
                [main.connections.remove(c) for c in main.connections[::-1] if c[1] == len(self.outputs)-1]
                self.outputs.pop()
                self.w, self.h = self.label.get_width()+75, 50+25*len(self.outputs)
        else:
            color = (40,40,40)
        pg.draw.rect(main.win, color, (main.origin[0]+mPos[0], main.origin[1]+mPos[1], bSize, bSize))
        pg.draw.line(main.win, (255,255,255), (main.origin[0]+mPos[0]+4, main.origin[1]+mPos[1]+bSize//2-1), (main.origin[0]+mPos[0]+14, main.origin[1]+mPos[1]+bSize//2-1), 2)
        if pPos[0] <= main.mousePos[0] < pPos[0]+bSize and pPos[1] <= main.mousePos[1] <= pPos[1]+bSize:
            color = (80,80,80)
            if main.leftClick:
                self.outputs.append(f'v{len(self.outputs)+1}')
                self.w, self.h = self.label.get_width()+75, 50+25*len(self.outputs)
        else:
            color = (40,40,40)
        pg.draw.rect(main.win, color, (main.origin[0]+pPos[0], main.origin[1]+pPos[1], bSize, bSize))
        pg.draw.line(main.win, (255,255,255), (main.origin[0]+pPos[0]+4, main.origin[1]+pPos[1]+bSize//2-1), (main.origin[0]+pPos[0]+14, main.origin[1]+pPos[1]+bSize//2-1), 2)
        pg.draw.line(main.win, (255,255,255), (main.origin[0]+pPos[0]+bSize//2-1, main.origin[1]+pPos[1]+4), (main.origin[0]+pPos[0]+bSize//2-1, main.origin[1]+pPos[1]+14), 2)

        main.win.blit(self.label, (main.origin[0]+self.x+10, main.origin[1]+self.y+10))