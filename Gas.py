from __future__ import annotations
from typing import Tuple,List,Union,Dict,Callable
from pygame import *
from random import random
from math import atan2,pi
from time import time as tm


class Object:
    def update(self,events:List[event.Event],dt:float):
        pass

    def draw(self,win:Surface):
        pass

class SideEffect:
    def __init__(self,show:Callable,collect:Callable,period=1):
        self.show=show
        self.collect=collect
        self.period=period
        self.t=0
        self.a=0

class Window:
    def __init__(self,WIDTH,HEIGHT,sideEffects:List[SideEffect]):
        self.WIDTH=WIDTH
        self.HEIGHT=HEIGHT
        self.BACKGROUND=(240,240,240)
        self.FPS=60

        self.dt=1

        self.isRunning=True

        self.win=display.set_mode((self.WIDTH,self.HEIGHT))
        self.clock=time.Clock()

        self.objects:List[Object]=[]

        self.sideEffects=sideEffects

    def update(self):
        events=event.get()
        for even in events:
            if even.type==QUIT:
                self.isRunning=False

        for effect in self.sideEffects:
            effect.t+=1
            effect.collect(effect)
            if effect.t==effect.period:
                effect.show(effect)
                effect.t=0

        for obj in self.objects:
            obj.update(events,self.dt)

    def draw(self):
        for obj in self.objects:
            obj.draw(self.win)

    def winUpdate(self):
        display.update()
        self.win.fill(self.BACKGROUND)
        self.clock.tick(self.FPS)
        display.set_caption(str(round(self.clock.get_fps())))

    def add_object(self,obj):
        self.objects.append(obj)

    def loop(self):
        while self.isRunning:
            self.update()
            self.draw()
            self.winUpdate()

class Border(Object):

    def __init__(self,pos:Vector2,moveable:bool=False):
        self.pos=pos
        self.vel=Vector2(0,0)
        self.force=Vector2(0,0)
        self.mass=20
        self.mass=1/self.mass
        self.pressure=Vector2(0,0)
        self.moveable=moveable
        self.normal=Vector2(0,0)

    def addPressure(self,dp:Vector2,pos:Vector2):
        self.pressure+=dp

    def update(self,events:List[event.Event],dt:float):
        if self.moveable:
            self.vel+=self.pressure*self.mass
            self.pos+=self.vel*dt
        self.pressure.x=0
        self.pressure.y=0

    def getIntersection(self,startPos:Vector2,vel:Vector2) -> bool:
        return False




class FlatBorder(Border):
    def __init__(self, startPos, endPos):

        self.startPos = Vector2(startPos)
        super(FlatBorder, self).__init__(self.startPos)
        self.endPos = Vector2(endPos)

        self.along = self.endPos - self.startPos
        self.normal = self.along.rotate(90).normalize()

    def draw(self, win):
        draw.line(win, (20, 20, 20), self.pos, self.pos+self.along)
        draw.line(win, (255,0,0),self.pos+self.along/2,self.pos+self.along/2+self.normal*35)

    def getIntersection(self,startPos:Vector2,vel:Vector2):
        if self.along.cross(vel)==0:
            print(self.along,vel)
        k=-(self.along.cross(startPos-self.pos))/(self.along.cross(vel))
        if k<=0.00000001 or k>1:
            return False
        q=((startPos-self.pos).cross(vel))/(self.along.cross(vel))
        if q<0 or q>1:
            return False

        return [startPos+k*vel,k,vel-2*self.normal*vel.dot(self.normal)]




class Ball(Object):
    def __init__(self,pos,borders,vel_magnitude):
        self.pos=Vector2(pos)
        self.vel=Vector2(1,0).rotate(random()*360)*vel_magnitude
        self.borders=borders
        self.mass=1

    def draw(self,win):
        draw.rect(win,(20,20,20),[self.pos.x,self.pos.y,3,3])

    def update(self,events,dt,rest:int=1):
        for border in self.borders:
            self.vel-=border.vel
            intersect=border.getIntersection(self.pos,self.vel*rest)
            if intersect:
                self.pos=intersect[0]
                new_vel = intersect[2] / rest
                rest*=intersect[1]
                border.addPressure((self.vel-new_vel)*self.mass,self.pos)
                self.vel=new_vel
                self.update(events,dt,rest)
                break
            self.vel+=border.vel
        else:
            self.pos+=self.vel*dt*rest


def pressureCollectOfX(x):
    def pressureCollect(effect):
        effect.a-=x.pressure.dot(x.normal)
    return pressureCollect
def pressureShowOfX(x:FlatBorder):
    def pressureShow(effect):
        print(effect.a/x.along.magnitude()/effect.period)
        effect.a=0
    return pressureShow






pos=[450,250]
size=[100,100]


b1=FlatBorder([500,200],[600,300])
b2=FlatBorder([600,300],[100,400])
b3=FlatBorder([100,400],[500,200])


Win=Window(1000,500,[SideEffect(pressureShowOfX(b1),pressureCollectOfX(b1),1000),
                     SideEffect(pressureShowOfX(b2),pressureCollectOfX(b2),1000),
                     SideEffect(pressureShowOfX(b3),pressureCollectOfX(b3),1000),
           ])

Win.add_object(b1)
Win.add_object(b2)
Win.add_object(b3)
#Win.add_object(b4)
for i in range(1000):
    Win.add_object(Ball([500,300],[b1,b2,b3],1))
#Win.add_object(Ball([100.5,50.6],[b1]))
#Win.add_object(Ball([100.234,50.534],[b1]))
Win.loop()