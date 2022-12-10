from pygame import *
from math import sin,pi
init()

class Cube:
    def __init__(self,m,x):
        self.y=0
        self.next_y=0
        self.vel=0
        self.m=m
        self.x=x

    def update(self,neighborhood,dt):
        dx=sum([i.y for i in neighborhood])/len(neighborhood)-self.y
        self.vel+=dx/self.m*dt
        self.next_y=self.y+self.vel*dt

    def flip(self):
        self.y=self.next_y

class LightSurface:
    def __init__(self,dt,game):
        self.n=game.WIDTH-40
        self.cubes=[Cube(1,i+20) for i in range(self.n)]
        self.cubes[0].m=10000000
        self.cubes[-1].m=10000000
        self.dt=dt
        self.g=game

    def updateCubes(self):
        for i in range(len(self.cubes)):
            neighborhood=[]
            if i!=0:
                neighborhood.append(self.cubes[i-1])
            if i!=len(self.cubes)-1:
                neighborhood.append(self.cubes[i+1])
            self.cubes[i].update(neighborhood,self.dt)
        for c in self.cubes:
            c.flip()

    def draw(self):
        for i in range(len(self.cubes)):
            draw.rect(self.g.win,(255,255,255),[self.cubes[i].x,self.g.HEIGHT/2+self.cubes[i].y,1,1])

    def move(self,pos):
        for c in self.cubes:
            if c.x==pos[0]:
                c.y=pos[1]-self.g.HEIGHT/2

class Game:
    def __init__(self):
        self.WIDTH=1200
        self.HEIGHT=600
        self.FPS=60
        self.dt=1
        self.isRunning=True

        self.t=0

        self.win=display.set_mode((self.WIDTH,self.HEIGHT))
        self.clock=time.Clock()

        self.lightSurface=LightSurface(self.dt,self)

        self.mpos=mouse.get_pos()
        self.mpress=mouse.get_pressed()

    def UpdateStuff(self):
        self.mpos = mouse.get_pos()
        self.mpress = mouse.get_pressed()
        self.lightSurface.updateCubes()
        for e in event.get():
            if e.type==QUIT:
                self.stop()

        self.t += 1
        if self.t/60<pi:
            self.lightSurface.move([20,self.HEIGHT/2+100*sin(self.t/60)])

    def DrawStuff(self):
        self.lightSurface.draw()

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
