# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Tuple,List,Union,Dict,Callable
from pygame import *
init()
def rot90(v:Vector2,clock:bool=True)->Vector2:
    return Vector2(-int(clock)*v.y,int(clock)*v.x)
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
    segments=[]
    def __init__(self,startPoint:Vector2,endPoint:Vector2,color:Union[Tuple[int,int,int],None]=(25,25,25)):
        super(Segment, self).__init__(startPoint,endPoint,color)
        Segment.segments.append(self)

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

class IntersectionFactory:
    def __init__(self):
        pass

    def line2line(self,l1:Line,l2:Line):
        A=l1.startPoint
        B=l1.endPoint
        C=l2.startPoint
        D=l2.endPoint
        if (B-A).cross(D-C)==0:
            return []
        k=-(A-C).cross(D-C)/(B-A).cross(D-C)
        return A+k*(B-A)

    def line2segment(self,l:Line,s:Segment):
        A=s.startPoint
        B=s.endPoint
        C=l.startPoint
        D=l.endPoint
        if (B-A).cross(D-C)==0:
            return []
        k=-(A-C).cross(D-C)/(B-A).cross(D-C)
        if 0<=k and k<=1:
            return A + k * (B - A)
        return[]

    def segment2segment(self,s1:Segment,s2:Segment):
        A=s1.startPoint
        B=s1.endPoint
        C=s2.startPoint
        D=s2.endPoint
        if (B-A).cross(D-C)==0:
            return []
        k=-(A-C).cross(D-C)/(B-A).cross(D-C)
        d=-(C-A).cross(B-A)/(D-C).cross(B-A)
        if 0<=k and k<=1 and 0<=d and d<=1:
            return A + k * (B - A)
        return[]

    def line2circle(self,l:Line,c:Circle):
        A=l.startPoint
        B=l.endPoint
        C=c.center
        a=(A-B).magnitude_squared()
        b=2*(A-B).dot(C-A)
        c=(C-A).magnitude_squared()-c.radius**2
        d=b**2-4*a*c
        if d<0:
            return []
        if d==0:
            k=-b/2/a
            return [A+k*(B-A)]
        if d>0:
            k1=(-b+d**0.5)/2/a
            k2=(-b-d**0.5)/2/a
            return [A+k1*(B-A),A+k2*(B-A)]

    def segment2circle(self,s:Segment,c:Circle):
        A=s.startPoint
        B=s.endPoint
        C=c.center
        a=(A-B).magnitude_squared()
        b=2*(A-B).dot(C-A)
        c=(C-A).magnitude_squared()-c.radius**2
        d=b**2-4*a*c
        if d<0:
            return []
        if d==0:
            k=-b/2/a
            if 0<k and k<1:
                return [A+k*(B-A)]
        if d>0:
            k1=(-b+d**0.5)/2/a
            k2=(-b-d**0.5)/2/a
            res=[]
            if 0<k1 and k1<1:
                res.append(A+k1*(B-A))
            if 0<k2 and k2<1:
                res.append(A+k2*(B-A))
            return res

    def circle2circle(self,c1:Circle,c2:Circle):
        B=c1.center
        C=c2.center

        R1=c1.radius
        R2=c2.radius

        x=(R1**2+(B-C).magnitude_squared()-R2**2)/2/(B-C).magnitude_squared()*(C-B)
        if R1**2<x.magnitude_squared():
            return []
        if R1**2==x.magnitude_squared():
            return [B+x]
        y=rot90(C-B).normalize()*(R1**2-x.magnitude_squared())**0.5
        return [B+x+y,B+x-y]


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
        Point([200,100],isMoveable=True)
        Point([500, 400],isMoveable=True)
        Point([600, 400], isMoveable=True)
        Point([500, 250], isMoveable=True)

        Segment(Point.points[0],Point.points[1])
        Line(Point.points[2], Point.points[3])
        Circle(Point.points[4],50)
        Circle(Point.points[3], 50)
        self.pointMover=PointMover()
        self.intersection=IntersectionFactory()

    def update(self):
        for even in event.get():
            if even.type==QUIT:
                self.stop()
        self.pointMover.update()
        print(self.intersection.circle2circle(Circle.circles[1],Circle.circles[0]))

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