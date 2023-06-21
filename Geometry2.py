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

class Drawwer:
    win:Union[Surface,None]=None

    @staticmethod
    def drawPoint(self:Point):
        if Drawwer.noneColorCheck(self):
            draw.circle(Drawwer.win, self.color, self.xy, 5)

    @staticmethod
    def drawLine(self:Line):
        if Drawwer.noneColorCheck(self):
            if (self.endPoint-self.startPoint).magnitude_squared()==0:
                return
            direction=(self.endPoint-self.startPoint).normalize()
            draw.line(Drawwer.win,self.color,self.startPoint-direction*2000,self.startPoint+direction*2000)

    @staticmethod
    def drawSegment(self:Segment):
        if Drawwer.noneColorCheck(self):
            draw.line(Drawwer.win, self.color, self.startPoint.xy, self.endPoint.xy, 3)

    @staticmethod
    def drawCircle(self:Circle):
        if Drawwer.noneColorCheck(self):
            draw.circle(Drawwer.win, self.color, self.center.xy, self.radius, 2)

    @staticmethod
    def noneColorCheck(self):
        return self.color != None


    @staticmethod
    def setWin(win:Surface):
        Drawwer.win=win


class Point(Vector2):
    points:List[Point]=[]
    def __init__(self,pos:Union[List[float],None]=None,color:Union[Tuple[int,int,int],None]=None,isMoveable:bool=False,
                 dynamicPosition:Union[None,Callable]=None,management:Union[List,None]=None):
        self.dynamicPosition=dynamicPosition
        if self.dynamicPosition:
            management.append(self)
            pos=self.dynamicPosition()
        super(Point, self).__init__(pos)
        self.color=color
        self.isMoveable=isMoveable
        Point.points.append(self)

    def manage(self):
        self.xy=self.dynamicPosition()

    def draw(self):
        Drawwer.drawPoint(self)

    @staticmethod
    def drawAll():
        for point in Point.points:
            point.draw()

class Line:
    lines:List[Line]=[]
    def __init__(self,startPoint:Vector2,endPoint:Vector2,color:Union[Tuple[int,int,int],None]=None):
        self.startPoint = startPoint
        self.endPoint = endPoint
        self.color = color

        Line.lines.append(self)

    def draw(self):
        Drawwer.drawLine(self)

    @staticmethod
    def drawAll():
        for line in Line.lines:
            line.draw()

class Segment(Line):
    segments=[]
    def __init__(self,startPoint:Vector2,endPoint:Vector2,color:Union[Tuple[int,int,int],None]=None):
        super(Segment, self).__init__(startPoint,endPoint,color)
        Segment.segments.append(self)

    def draw(self):
        Drawwer.drawSegment(self)

class Circle:
    circles:List[Circle]=[]
    def __init__(self,center:Vector2,radius:Union[float,None]=None,color:Union[Tuple[int,int,int],None]=None,
                 dynamicRadius:Union[None,Callable]=None,management:Union[List,None]=None):
        self.center:Vector2=center
        self.color=color
        self.dynamicRadius=dynamicRadius
        if dynamicRadius:
            management.append(self)
            radius=self.dynamicRadius()
        self.radius: float = radius
        Circle.circles.append(self)


    def manage(self):
        self.radius=self.dynamicRadius()

    def draw(self):
        Drawwer.drawCircle(self)

    @staticmethod
    def drawAll():
        for circle in Circle.circles:
            circle.draw()

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
    def __init__(self,management:List):
        self.management=management

    def line2lineVectors(self,A:Vector2,B:Vector2,C:Vector2,D:Vector2):
        if (B-A).cross(D-C)==0:
            return []
        k=-(A-C).cross(D-C)/(B-A).cross(D-C)
        return A+k*(B-A)

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

    def line2segmentVectors(self,A:Vector2,B:Vector2,C:Vector2,D:Vector2):
        """
        :param A: segment start
        :param B: segment end
        :param C: line start
        :param D: line end
        :return: intersection
        """
        if (B-A).cross(D-C)==0:
            return []
        k=-(A-C).cross(D-C)/(B-A).cross(D-C)
        if 0<=k and k<=1:
            return A + k * (B - A)
        return[]

    def segment2segment(self,A:Vector2,B:Vector2,C:Vector2,D:Vector2):
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


def buildTriangle(p1,p2,p3):
    s1=Segment(p1,p2,color=(25,25,25))
    s2=Segment(p2,p3,color=(25,25,25))
    s3=Segment(p3,p1,color=(25,25,25))
    return s1,s2,s3


def buildBisector(p,l1:Line,l2:Line,factory:IntersectionFactory,orientation:Tuple[bool,bool]=(False,False),
                  color:Union[None,Tuple[int,int,int]]=None):
    c1=Circle(p,25,None)
    p11=Point(dynamicPosition=lambda :factory.line2circle(l1,c1)[int(orientation[0])],management=factory.management)
    p12=Point(dynamicPosition=lambda :factory.line2circle(l2,c1)[int(orientation[1])],management=factory.management)
    bisector=buildMedianPerpendicular(p11,p12,factory,color)
    return bisector

def buildCevian(p:Point,l:Line,s:Segment,factory:IntersectionFactory):
    p2=Point(dynamicPosition=lambda:factory.line2line(l,s),management=factory.management)
    Segment(p,p2,(250,0,0))

def buildMedianPerpendicular(p1:Point,p2:Point,factory:IntersectionFactory,color:Union[None,Tuple[int,int,int]]=None):
    c1=Circle(p1,dynamicRadius=lambda:(p1-p2).magnitude(),management=factory.management)
    c2=Circle(p2,dynamicRadius=lambda:(p1-p2).magnitude(),management=factory.management)
    p3=Point(dynamicPosition=lambda:factory.circle2circle(c1,c2)[0],management=factory.management)
    p4 = Point(dynamicPosition=lambda: factory.circle2circle(c1, c2)[1],management=factory.management)
    medianPerpendicular=Line(p3,p4,color)
    return medianPerpendicular

def buildNormal(p:Point,l:Line,factory:IntersectionFactory,color:Union[None,Tuple[int,int,int]]=None):
    c=Circle(p,dynamicRadius=lambda:(l.startPoint-p).magnitude(),management=factory.management)
    p1=Point(dynamicPosition=lambda:factory.line2circle(l,c)[0],management=factory.management)
    p2=Point(dynamicPosition=lambda:factory.line2circle(l,c)[1],management=factory.management)
    normal=buildMedianPerpendicular(p1,p2,factory,color)
    return normal

def buildExternallyInscribedCircle(p1,p2,l1,l2,l3,orientation,factory):
    b1 = buildBisector(p1, l2, l3, factory, (False,orientation[0]))
    b2 = buildBisector(p2, l1, l3, factory, (False,orientation[1]))
    o2 = Point(color=(100, 100, 0), dynamicPosition=lambda: factory.line2line(b1, b2), management=factory.management)
    normal2 = buildNormal(o2, l1, factory, None)
    h2 = Point(color=(0, 100, 0), dynamicPosition=lambda: factory.line2line(l1, normal2), management=factory.management)
    c2 = Circle(o2, dynamicRadius=lambda: (h2 - o2).magnitude(), management=factory.management, color=(25, 25, 25))

def build(p1,p2,p3,factory):
    s1,s2,s3=buildTriangle(p1,p2,p3)

    l1=Line(p2,p3,(25,25,25))
    l2=Line(p1,p3,(25,25,25))
    l3=Line(p1,p2,(25,25,25))

    buildExternallyInscribedCircle(p1,p2,l1,l2,l3,(False,False),factory)
    buildExternallyInscribedCircle(p1, p2, l1, l2, l3, (True, False), factory)
    buildExternallyInscribedCircle(p1, p2, l1, l2, l3,(True, True), factory)
    buildExternallyInscribedCircle(p1, p2, l1, l2, l3, (False, True), factory)


def manage(management):
    for object in management:
        object.manage()

class Game:
    def __init__(self):
        self.WIDTH=1000
        self.HEIGHT=500
        self.FPS=60
        self.BACKGROUND=(200,200,200)

        self.win=display.set_mode((self.WIDTH,self.HEIGHT))
        self.clock=time.Clock()
        self.isRunning=True


        p1=Point([400,100],isMoveable=True,color=(25,25,25))
        p2=Point([500,100],isMoveable=True,color=(25,25,25))
        p3=Point([500, 400],isMoveable=True,color=(25,25,25))

        self.pointMover=PointMover()
        self.management:List[any]=[]
        self.intersection=IntersectionFactory(self.management)
        Drawwer.setWin(self.win)
        build(p1, p2, p3,self.intersection)
    def update(self):
        for even in event.get():
            if even.type==QUIT:
                self.stop()
        self.pointMover.update()
        manage(self.management)

    def draw(self):
        Line.drawAll()
        Circle.drawAll()
        Point.drawAll()


    def windowUpdate(self):
        display.update()
        self.win.fill(self.BACKGROUND)
        display.set_caption(str(round(self.clock.get_fps())))
        self.clock.tick(self.FPS)

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