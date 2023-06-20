# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Tuple,List,Union,Dict,Callable
from pygame import *
init()
# План:
# 1)Створення початкових умов
# 2)Побудова структури на базі данних початкових умов
#   2.0)Розбиття побудови на менші частинки
#   2.1)Побудова елементарних частинок за допомогою базових функцій побудови
# 3)Динамічна зміна початкових умов
class Point(Vector2):
    points:List[Point]=[]
    def __init__(self,pos:List[float],color:Tuple[int,int,int]=(25,25,25),isMoveable:bool=False):
        super(Point, self).__init__(pos)
        self.color=color
        self.isMoveable=isMoveable
        Point.points.append(self)

    def draw(self,win):
        draw.circle(win,self.color,self.xy,5)

    @staticmethod
    def drawAll(win):
        for point in Point.points:
            point.draw(win)


class Segment:
    segments:List[Segment]=[]
    def __init__(self,startPoint:Vector2,endPoint:Vector2,color:Tuple[int,int,int]=(25,25,25)):
        self.startPoint=startPoint
        self.endPoint=endPoint
        self.color=color
        Segment.segments.append(self)

    def draw(self,win):
        draw.line(win,self.color,self.startPoint.xy,self.endPoint.xy,4)

    @staticmethod
    def drawAll(win):
        for segment in Segment.segments:
            segment.draw(win)

class PointMover:
    def __init__(self):
        self.currentPoint:Union[None,Point]=None

    def update(self):
        mPress=mouse.get_pressed()
        mPos:Vector2=Vector2(mouse.get_pos())
        if mPress[0]:
            if self.currentPoint==None:
                currentMin=2500
                for point in Point.points:
                    if (point-mPos).magnitude_squared()<currentMin:
                        currentMin = (point - mPos).magnitude_squared()
                        self.currentPoint=point

            if self.currentPoint!=None:
                self.currentPoint.xy=mPos.xy
        else:
            self.currentPoint=None


class Game:
    def __init__(self):
        self.WIDTH=1000
        self.HEIGHT=500
        self.FPS=60
        self.BACKGROUND=(200,200,200)

        self.win=display.set_mode((self.WIDTH,self.HEIGHT))
        self.clock=time.Clock()
        self.isRunning=True


        Point([100,100])
        Point([200,300])
        Point([500, 300])
        Segment(Point.points[0], Point.points[1])
        Segment(Point.points[1], Point.points[2])
        Segment(Point.points[0], Point.points[2])

        self.pointMover=PointMover()

    def update(self):
        for even in event.get():
            if even.type==QUIT:
                self.stop()
        self.pointMover.update()


    def draw(self):
        Segment.drawAll(self.win)
        Point.drawAll(self.win)


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
        quit()

    def stop(self):
        self.isRunning=False

if __name__=="__main__":
    game=Game()
    game.run()