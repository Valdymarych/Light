# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Tuple,List,Union,Dict,Callable
from pygame import *

class Game:
    def __init__(self):
        self.WIDTH=1000
        self.HEIGHT=500
        self.FPS=60
        self.BACKGROUND=(200,200,200)

        self.win=display.set_mode((self.WIDTH,self.HEIGHT))
        self.clock=time.Clock()
        self.isRunning=True

    def update(self):
        for even in event.get():
            if even.type==QUIT:
                self.stop()


    def draw(self):
        pass

    def windowUpdate(self):
        display.update()
        self.win.fill(self.BACKGROUND)
        display.set_caption(str(round(self.clock.get_fps())))
        self.clock.tick(60)

    def run(self):
        while self.isRunning:
            self.update()
            self.draw()
            self.windowUpdate()

    def stop(self):
        quit()
        self.isRunning=False

if __name__=="__main__":
    game=Game()
    game.run()