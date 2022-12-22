from pygame import *
from math import sin,pi
from numpy import array,ones,zeros
import numpy as np
init()

class LightSurface:
    def __init__(self,dt,game,m):
        self.n=game.WIDTH-40

        self.y=zeros(self.n,dtype=np.float16)
        self.vel=zeros(self.n,dtype=np.float16)
        self.m=ones(self.n,dtype=np.int32)
        self.m*=m
        self.m[0]=10000000
        self.m[-1]=10000000
        self.dx=zeros(self.n,dtype=np.float16)

        self.dt=dt
        self.g=game

    def updateCubes(self):
        self.dx[:-1]=self.y[1:]
        self.dx[-1]=0
        self.dx[1:]=self.dx[1:]+self.y[:-1]
        self.dx=self.dx/2
        self.dx=self.dx-self.y




        self.vel=self.vel+self.dx/self.m#*self.dt
        self.y=self.y+self.vel#*self.dt



    def draw(self,y):
        for i in range(self.n):
            draw.rect(self.g.win,(255,255,255),[20+i,y+self.y[i],1,1])

    def move(self,pos):
        self.y[pos[0]-20]=pos[1]-self.g.HEIGHT/2

class Game:
    def __init__(self):
        self.WIDTH=1200
        self.HEIGHT=600
        self.FPS=6000
        self.dt=1
        self.isRunning=True

        self.t=0

        self.win=display.set_mode((self.WIDTH,self.HEIGHT))
        self.clock=time.Clock()

        self.lightSurface=LightSurface(self.dt,self,1)
        self.lightSurface2 = LightSurface(self.dt, self,4)

        self.mpos=mouse.get_pos()
        self.mpress=mouse.get_pressed()

    def UpdateStuff(self):
        self.mpos = mouse.get_pos()
        self.mpress = mouse.get_pressed()
        self.lightSurface.updateCubes()
        self.lightSurface2.updateCubes()

        for e in event.get():
            if e.type==QUIT:
                self.stop()

        self.t += 1
        if self.t/60<pi:
            self.lightSurface.move([20,self.HEIGHT/2+100*sin(self.t/60)])
            self.lightSurface2.move([20, self.HEIGHT / 2 + 100 * sin(self.t / 60)])

    def DrawStuff(self):
        self.lightSurface.draw(150)
        self.lightSurface2.draw(450)

    def WindowUpdateStuff(self):
        self.UpdateStuff()
        self.win.fill((0,0,0))
        self.DrawStuff()
        display.update()
        self.clock.tick(self.FPS)
        display.set_caption(str(round(self.clock.get_fps())))

    def run(self):
        while self.isRunning:
            self.WindowUpdateStuff()

    def stop(self):
        self.isRunning=False

game=Game()
game.run()
quit()
