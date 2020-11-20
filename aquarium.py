#!/usr/bin/env python3

# IMPORTS
import os
import sys
import time
import json
import getch
import random
import signal
import threading

import ui


# VARIABLE SETUP
## frametime & rate
framerate = 15
frametime = 1/framerate

## loop controller
keepGoing = True

## PATH to be referenced for files
PATH = os.path.abspath(os.path.dirname(__file__))

## logfile referenced by dbg
logfile = os.path.join(PATH,'log')

## terminal dimensions
tWidth, tHeight = os.get_terminal_size()

## globals used
POI = None
foods = []



# FUNCTIONS
## function called on exit
def exit(*args):
    global keepGoing
    keepGoing = False
    print('\033[0;0H\033[2J\033[?25h')


## function for logging data
def dbg(*args):
    with open(logfile,'a') as f:
        f.write(' '.join([str(a) for a in args])+'\n')


## main loop to handle inputs
### TODO: whatever key captured should be sent to UI class for evaluation
def getchLoop():
    while keepGoing:
        key = getch()
        if key == "q":
            exit()



# CLASSES
class Tank:
    # handles all activity within the tank
    def __init__(self,properties={}):
        self.size = 60,30
        self.xborder = (tWidth-self.size[0])//2
        self.yborder = (tHeight-self.size[1])//2

        self.drawBorders()
        self.generatePOI()


    def drawNewFrame(self):
        for f in self.fishes:
            skin = f.skin

            # clear previous
            px,py = f.pos
            sys.stdout.write(f"\033[{py};{px}H"+len(f.skin)*' ')

            # print new
            frame = f.getNextFrame()
            sys.stdout.write(f'\033[{tHeight-2};0H\033[K'+str(frame))

            if isinstance(frame, str):
                if frame == 'turn':
                    skin = (f.skin if f.pskin == f.rskin else f.rskin)
                    x,y = f.pos
            else:
                x,y = frame

                if x > px:
                    skin = f.skin
                else:
                    skin = f.rskin


            sys.stdout.write(f"\033[{y};{x}H"+skin)

            # update fish
            f.pos = x,y
            f.pskin = skin


    def generatePOI(self):
        global POI

        x = random.randint(self.xborder,self.xborder+self.size[0])

        # limit y movement to 3rd of height
        if POI:
            y = POI[1]
        else:
            y = 0

        ylimit = tHeight//6
        ymax = min(y+ylimit,self.yborder+self.size[1])
        ymin = max(y-ylimit,self.yborder)
        y = random.randint(min(ymin,ymax),max(ymin,ymax))


        POI = x,y


    def drawBorders(self):
        return
        for x in range(self.size[0]+1):
            sys.stdout.write(f'\033[{self.yborder};{self.xborder+x}H=')
            sys.stdout.write(f'\033[{self.yborder+self.size[1]};{self.xborder+x}H=')

        for y in range(self.size[1]):
            sys.stdout.write(f'\033[{self.yborder+y};{self.xborder}H|')
            sys.stdout.write(f'\033[{self.yborder+y};{self.xborder+self.size[0]}H|')


class Fish:
    # frame-based system
    # tank handler goes through each fish, gets a new frame and prints it at once
    def __init__(self,properties={}):
        self.pos = tWidth//2,tHeight//2

        self.path = []
        self.actions = []
        self.sleepCounter = 0
        self.sleepTarget = 0

        self.food = None
        self.POI = None

        # PROPERTIES
        self.name = None
        self.species = 'Molly'
        self.data = data[self.species]
        self.age = 1

        self.getSkins()


    def getSkins(self):
        if self.name:
            self.skin = self.data['specials'][self.name][self.age]
        else:
            self.skin = self.data['growth'][self.age]

        # reverse skin
        rev = ''
        reversible = ['<>','[]','{}','()','/\\','db','qp']
        for c in reversed(self.skin):
            for r in reversible:
                if c in r:
                    new = r[r.index(c)-1]
                    break
            else:
                new = c

            rev += new
        self.rskin = rev
        self.pskin = self.skin


    def getPigment(self):
        # PHASE 2
        pass


    def applyPigment(self):
        # PHASE 2
        pass


    def generatePathTo(self,xy):
        path = []

        x1,y1 = self.pos
        x2,y2 = xy

        # x dif, x direction
        dx = abs(x2-x1)
        sx = (1 if x1 < x2 else -1)

        # y dif, y direction
        dy = -abs(y2-y1)
        sy = (1 if y1 < y2 else -1)

        # error
        error = dx+dy

        while True:
            path.append([x1,y1])
            if (x1 == x2 and y1 == y2):
                break

            error2 = 2*error

            if error2 >= dy:
                error += dy
                x1 += sx

            if error2 <= dx:
                error += dx
                y1 += sy

        self.path = path


    def getNextFrame(self):
        if self.path == []:
            self.POI = None
            self.food = None

            xy = self.getNewPoint()
            self.generatePathTo(xy)
            self.animate()

        # get next move
        move = self.path[0]

        # get next action
        if len(self.actions):

            action = self.actions[-1]
            actionSplit = action.split(' ')
            self.actions.pop()

            if len(actionSplit) > 1:
                verb, noun = action.split(' ')
            else:
                verb = action
                noun = 0

            if verb == "turn":
                return 'turn'

        if self.sleepTarget == 0 or self.sleepTarget <= globalTimer:
            self.sleepTarget = 0
            self.path.pop(0)
            return move

        else:
            return self.pos


    def getNewPoint(self):

        if len(foods):
            index = random.randint(0,len(foods)-1)
            self.food = foods[index]
            foods.pop(index)
            xy = self.food.xy

        elif POI != None:

            # follow global POI if chance
            if (random.randint(0,100) > 45):
                self.POI = POI
                x,y = POI

                # get maximum offsets
                x += random.randint(-10,10)
                y += random.randint(-5,5)
                xy = x,y

                # TODO: this isnt good
                xlimit = tank.xborder+tank.size[0]-len(self.skin)
                ylimit = tank.yborder+tank.size[1]-1

                if x not in range(tank.xborder+len(self.skin),xlimit) or y not in range(tank.yborder+1,ylimit):
                    x,y = POI
                    x -= len(self.skin)
                    xy = x,y

            # otherwise request new POI
            else:
                tank.generatePOI()
                self.getNewPoint()

                xy = POI

        return xy


    def animate(self):
        if self.food:
            # animation of fish going towards, decreasing food health & going back
            pass

        elif self.POI:
            # animation of fish turning around random times
            x,y = self.path[-1]
            sleepTime = random.randint(10,20)//10

            self.actions.append('turn')
            self.sleep(sleepTime)
            self.actions.append('turn')


    def sleep(self,t):
        x,y = self.path[-1]
        for a in range(t*framerate):
            self.path.append([x,y])



# STARTUP
## initialize screen
print('\033[2J\033[?25l')

## data loading
with open(os.path.join(PATH,'data.json')) as f:
    data = json.load(f)

## clear log
open(logfile,'w').close()

## catch exit
signal.signal(signal.SIGINT,exit)

## TODO: finalize
tank = Tank()
tank.fishes = [Fish() for _ in range(5)]

## time counters
counter = 0
globalTimer = 0

# MAIN LOOP ================================================================
## input loop
threading.Thread(target=getchLoop).start()
## main display loop
while keepGoing:
    tank.drawNewFrame()
    tank.drawBorders()
    counter += 1

    if counter == frametime**-1 * 2:
        tank.generatePOI()
        counter = 0

    # if POI:
        # sys.stdout.write(f'\033[{tHeight-2};0H\033[K'+str(POI))

    sys.stdout.flush()
    globalTimer += frametime

    time.sleep(frametime)

dbg('gracefully exited. goodbye!')
