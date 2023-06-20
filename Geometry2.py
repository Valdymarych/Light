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
    def __init__(self,pos:List[float],color:Union[Tuple[int,int,int],None]=(25,25,25),isMoveable:bool=False):
        super(Point, self).__init__(pos)
        self.color=color
        self.isMoveable=isMoveable
        Point.points.append(self)

    def draw(self,win):
        if color!=None:
            draw.circle(win,self.color,self.xy,5)

    @staticmethod
    def drawAll(win):
        for point in Point.points:
            point.draw(win)


class Line:
    lines:List[Line]=[]
    def __init__(self,startPoint:Vector2,endPoint:Vector2,color:Union[Tuple[int,int,int],None]=(25,25,25)):
        self.startPoint = startPoint
        self.endPoint = endPoint
        self.color = color

        Line.lines.append(self)

    def draw(self,win):
        if color != None:
            direction=(self.endPoint-self.startPoint).normalize()
            draw.line(win,self.color,self.startPoint-direction*2000,self.startPoint+direction*2000)

    @staticmethod
    def drawAll(win):
        for line in Line.lines:
            line.draw(win)

class Segment(Line):
    def __init__(self,startPoint:Vector2,endPoint:Vector2,color:Union[Tuple[int,int,int],None]=(25,25,25)):
        super(Segment, self).__init__(startPoint,endPoint,color)


    def draw(self,win):
        if color != None:
            draw.line(win,self.color,self.startPoint.xy,self.endPoint.xy,4)

class Circle:
    circles:List[Circle]=[]
    def __init__(self,center:Vector2,radius:float,color:Union[Tuple[int,int,int],None]=(25,25,25)):
        self.center:Vector2=center
        self.radius:float=radius
        self.color=color
        Circle.circles.append(self)

    def draw(self,win:Surface):
        if color != None:
            draw.circle(win,self.color,self.center.xy,self.radius,2)

    @staticmethod
    def drawAll(win:Surface):
        for circle in Circle.circles:
            circle.draw(win)


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
                    if point.isMoveable:
                        if (point-mPos).magnitude_squared()<currentMin:
                            currentMin = (point - mPos).magnitude_squared()
                            self.currentPoint=point

            if self.currentPoint!=None:
                self.currentPoint.xy=(mPos/10+self.currentPoint*9/10).xy
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


        Point([100,100],isMoveable=True)
        Point([200,300],isMoveable=True)
        Point([500, 300],isMoveable=True)
        Segment(Point.points[0], Point.points[1])
        Segment(Point.points[1], Point.points[2])
        Segment(Point.points[0], Point.points[2])
        Line(Point.points[0], Point.points[1])
        Circle(Point.points[0],50)

        self.pointMover=PointMover()

    def update(self):
        for even in event.get():
            if even.type==QUIT:
                self.stop()
        self.pointMover.update()


    def draw(self):
        Segment.drawAll(self.win)
        Circle.drawAll(self.win)
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