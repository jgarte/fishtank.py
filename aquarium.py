#!/usr/bin/env python3

# IMPORTS
import os
import sys
import time
import json
import random
import signal
import threading
from getch import getch



# VARIABLE SETUP
## frametime & rate
framerate = 60
fish_framerate = 15
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
available_foods = []

## history
### file length in lines
historyLength = 100
### history file
history = os.path.join(PATH,'fishtank_history')

if not "fishtank_history" in os.listdir(PATH):
    open(history,'w').close()



# FUNCTIONS
## function called on exit
def exit(*args):
    global keepGoing
    keepGoing = False
    dbg('gracefully exited. goodbye!')
    print('\033[0;0H\033[2J\033[?25h')


## function for logging data
def dbg(*args):
    s = ' '.join([str(a) for a in args])
    with open(logfile,'a') as f:
        f.write(s+'\n')
    sys.stdout.write(f"\033[{tHeight-2};0H"+s)


## main loop to handle inputs
def getchLoop():
    # this loop getch hijacked by current UI
    while keepGoing:
        key = getch()

        # feeding menu
        if ui.is__in_feed:
            ui.feedingSelection(key)

        # normal
        else:
            ui.sendKey(key)


# CLASSES
## all classes under tank have some of the same functions & variables:
## - getNewFrame()
## - skin, pskin & rskin
## - pos
## - pause() & is_paused
## these allow for a unified way of handling them.
class Tank:
    # handles all activity within the tank
    def __init__(self,properties={}):
        self.size = 60,30
        self.xborder = (tWidth-self.size[0])//2
        self.yborder = (tHeight-self.size[1])//2

        self.drawBorders()
        self.generatePOI()

        self.frame = []


    def drawNewFrame(self,updateContents=True):
        if updateContents:
            for e in self.contents:
                if e.is_paused:
                    continue

                skin = e.skin

                # clear previous
                px,py = e.pos
                sys.stdout.write(f"\033[{py};{px}H"+len(e.skin)*' ')

                # print new
                frame = e.getNextFrame()

                # actions
                if isinstance(frame, str):
                    if frame == 'turn':
                        skin = (e.skin if e.pskin == e.rskin else e.rskin)
                        x,y = e.pos
                else:
                    x,y = frame

                    if x > px:
                        skin = e.skin
                    else:
                        skin = e.rskin

                sys.stdout.write(f"\033[{y};{x}H"+skin)

                # update variables
                e.pos = x,y
                e.pskin = skin

        # UI actions
        for e in self.frame:
            content,xy = e
            x,y = xy
            sys.stdout.write(f"\033[{y};{x}H"+content)


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

    def pauseFish(self,value=True):
        for e in self.contents:
            e.is_paused = value


    def drawBorders(self):
        return
        for x in range(self.size[0]+1):
            sys.stdout.write(f'\033[{self.yborder};{self.xborder+x}H=')
            sys.stdout.write(f'\033[{self.yborder+self.size[1]};{self.xborder+x}H=')

        for y in range(self.size[1]):
            sys.stdout.write(f'\033[{self.yborder+y};{self.xborder}H|')
            sys.stdout.write(f'\033[{self.yborder+y};{self.xborder+self.size[0]}H|')


class Fish:
    def __init__(self,properties={}):
        self.pos = tWidth//2,tHeight//2

        # instance variables
        self.path = []
        self.actions = []
        self.sleepCounter = 0
        self.sleepTarget = 0

        # flags
        self.is_paused = False

        # variables for movement
        self.food = None
        self.POI = None

        # PROPERTIES (TEMPORARY)
        ## TODO: save & reload
        self.name = None
        self.species = 'Molly'
        self.data = data[self.species]
        self.age = 1

        # set skins according to properties
        self.getSkins()


    def pause(self,state=True):
        self.is_paused = state


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
        #  PHASE2
        pass


    def applyPigment(self):
        #  PHASE2
        pass


    def generatePathTo(self,xy,maxStep=1):
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
            if random.randint(1,maxStep) == 1:
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

            xy = self.getNewPoint()
            maxStep = (3 if self.food else 1)

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
        global available_foods

        if self.food:
            self.food.pause()
            self.food = None
            return self.pos


        elif len(available_foods):
            index = random.randint(0,len(available_foods)-1)
            self.food = available_foods[index]
            available_foods.pop(index)
            xy = self.food.pos

        elif POI != None:

            # follow global POI if chance
            if (random.randint(0,100) > 45):
                self.POI = POI
                x,y = POI

                # get maximum offsets
                x += random.randint(-10,10)
                y += random.randint(-5,5)
                xy = x,y

                # TODO: this isnt working
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
        for a in range(t*fish_framerate):
            self.path.append([x,y])


class Pellet:
    def __init__(self,pos,direction=1,health=None):
        # temp, to be replaced by health system
        # self.getSkin()
        self.skin = '#'
        self.rskin = '#'
        self.pskin = '#'

        # instance variables
        self.pos = pos
        self.health = health
        self.direction = direction

        # flags
        self.is_paused = False

    def getPath(self):
        # make the path gen global
        # fish needs to calculate how many frames away it is, query path[d] and go to it
        # when it gets there pause it, animate and do stuff
        pass

    def getNextFrame(self):
        if counter % 8 == 0:
            x,y = self.pos

            y += (1 if random.randint(1,3) > 1 else 0)
            x += self.direction*random.randint(-1,2)

            return (x,y)
        else:
            return self.pos

    def pause(self,value=True):
        self.is_paused = value


class Interface:
    def __init__(self):
        # instance variables
        self.cmd = ""
        self.history_location = 0
        self.xcursor = 0
        self.prompt_default = "command: "

        # flags
        self.is__escape_char = False
        self.is__in_prompt = False
        self.is__in_feed = False

        # menu variables
        self.feedcursor = 0
        self.feed_coords = None


    def sendKey(self,key):
        def navigateHistory(direction,save=False):
            # save current line: TODO
            if save and False:
                history_l.insert(0,self.cmd)

            # get new location
            if direction == 'up':
                history_loc = min(self.history_location+1,len(history_l))
            else:
                history_loc = max(0,self.history_location-1)

            # refresh instance variable
            self.history_location = history_loc

            # handle stuff
            if history_loc == 0:
                self.cmd = ''
            else:
                self.cmd = history_l[-history_loc].rstrip()

            # refresh cursor
            self.xcursor = len(self.prompt+self.cmd)+1


        highlight = '\033[47m'

        # mostly for debug/easy access, may be removed
        if self.is__in_prompt:

            # get history contents
            with open(history,'r') as f:
                history_l = f.readlines()

            # HANDLE KEYS
            if self.is__escape_char:
                ## second key in escape characters
                if key == "[":
                    return

                ## move cursor left
                elif key in ['D','K']:
                    self.xcursor = max(self.xcursor-1,0)

                ## move cursor right
                elif key in ['C','M']:
                    self.xcursor = min(self.xcursor+1,len(self.cmd))

                ## move up in history
                elif key in ['A','TODO']:
                    navigateHistory('up',save=True)

                ## move down in history
                elif key in ['B','TODO']:
                    navigateHistory('down')

                ## do escape behavior (exit prompt)
                else:
                    self.echo("\033[K")
                    self.cmd = ""
                    self.is__in_prompt = False
                    self.is__escape_char = False
                    return

                ## reset states
                key = ""
                self.is__escape_char = False

            ## escape
            elif key == "\x1b":
                self.is__escape_char = True
                return

            ## backspace
            elif key == '\x7f':
                # avoid index errors
                if self.xcursor > 0:
                    left = self.cmd[:self.xcursor-1]
                    right = self.cmd[self.xcursor:]
                    self.cmd = left+right
                    self.xcursor -= 1

                # not sure about this
                if len(self.cmd) == 0 and False:
                    self.sendKey('\x1b')
                    return

            ## end prompt, send command
            elif key in ['\r','\n']:

                # save command: TODO
                if False:
                    history_l.append(self.cmd)
                    dbg('history:',history_l)
                    if len(self.cmd):
                        with open(history,'w') as f:
                            f.write(history_l[:historyLength])

                self.handleCommand(self.cmd)
                self.cmd = ""
                self.is__in_prompt = False
                self.is__escape_char = False

                return

            ## add character at cursor
            elif key:
                # split cmd
                left = self.cmd[:self.xcursor]
                right = self.cmd[self.xcursor:]

                # add character
                left += key

                # rejoin command
                self.cmd = left+right

                # iterate cursor
                self.xcursor += 1


            # FORMAT, SEND CMD
            ## Add highlight color
            ### get left side
            left = self.cmd[:self.xcursor]

            ### get character under cursor
            if self.xcursor > len(self.cmd)-1:
                underCursor = ' '
            else:
                underCursor = self.cmd[self.xcursor]

            ### get right side
            right = self.cmd[self.xcursor+1:]


            ## Echo result
            self.echo(self.prompt+left+highlight+"\033[30m"+underCursor+'\033[0m'+right)


        # PLANS
        # - manual typing input will likely exist as
        #   an option, but wont be needed after PHASE1.
        # - navigation will be context based, with (customizable?) dicts controlling mappings.

        controls = {
            "q": "exit",
            "i": "start_prompt",
            "f": "feed",
            "\x1b": "start_prompt"
        }

        if not self.is__in_prompt and key in controls.keys():
            self.handleCommand(controls[key])


    def handleCommand(self,cmd):
        self.echo("Your command was "+cmd+".")

        # get verb and args
        split = cmd.split(' ')
        verb = split[0]
        if len(split) > 1:
            args = split[1:]
        else:
            args = []

        # TODO: move everything under here into functions

        # launch commands
        ## prompt
        if verb == "start_prompt":
            # get prompt value
            if len(args):
                self.prompt = ' '.join(args)
            else:
                self.prompt = self.prompt_default

            # set up prompt
            self.is__in_prompt = True
            self.xcursor = 0
            self.echo(self.prompt+self.cmd)

        ## feeding menu
        ### TODO
        ### for now just a cluster of points
        elif verb == "feed":

            # try to get coords
            coords = None
            if len(args):
               coords = args.split(',')

               if len(coords) != 2:
                   dbg('invalid coords value "'+str(coors)+'".')
                   coords = None

            # start feeding menu
            ## this controls if selection should be bypassed
            self.feed_coords = coords
            ## start selection
            self.feedingSelection()

        ## exit program
        elif verb == "exit":
            exit()


    def echo(self,s,clear=True):
        sys.stdout.write(f'\033[{tHeight};0H'+("\033[K" if clear else "")+s)
        sys.stdout.flush()



    # FEEDING
    def feedingSelection(self,key=None):
        tank.frame = []
        if key == None:
            tank.pauseFish()
            self.echo("Use 'H' to move left, 'L' to move right!")
            self.is__in_feed = True
            self.feed_index = 0

        if not self.feed_coords:
            # PRINT SELECTION
            y = max(tank.yborder - 3,2)
            counter = 0
            xs = []
            skins = ['#','x','.']

            for x in range(tank.xborder, tank.size[0]+tank.xborder):
                if x % 2 == 0:
                    tank.frame.append(['.',(x,y)])
                    xs.append(x)

        if key == '\x1b':
            tank.pauseFish(0)
            self.echo('\033[K')
            self.is__in_feed = False

        elif key == "l":
            self.feedcursor += 1

        elif key == "h":
            self.feedcursor -= 1

        elif key in ["\r","\n"]:
            # end feeding selection
            self.feedingSelection('\x1b')

            # set coords for spawn
            self.feed_coords = [xs[self.feedcursor],y]

            # remove guide from tank
            tank.frame = tank.frame[-1:]
            sys.stdout.write(f'\033[{y};{0}H'+'\033[K')

            # start spawn
            self.feedingSpawn()

        tank.frame.append(["\033[30;47m"+'#'+'\033[0m',(xs[self.feedcursor],y)])


    def feedingSpawn(self,num=20):
        global available_foods

        for c in range(num):
            direction = (-1 if c % 2 else 1)
            p = Pellet(self.feed_coords,direction=direction)
            available_foods.append(p)
            tank.contents.append(p)


    



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

## TODO:
## - save
## - restore
tank = Tank()
tank.contents = [Fish() for _ in range(5)]

## time counters
counter = 0
globalTimer = 0

## interface handler
ui = Interface()

# MAIN LOOP ================================================================
## input loop
threading.Thread(target=getchLoop).start()

## display loop
while keepGoing:

    # update UI at 60FPS but fish only at 15.
    if counter % (framerate/fish_framerate) == 0:
        updateContents = True
    else:
        updateContents = False

    tank.drawNewFrame(updateContents=updateContents)
    tank.drawBorders()

    # increment globals
    counter += 1
    globalTimer += frametime

    # generate POI if timer
    if counter % framerate*2 == 0:
        tank.generatePOI()

    # update, loop
    sys.stdout.flush()
    time.sleep(frametime)
