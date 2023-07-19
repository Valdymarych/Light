# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Tuple,List,Union,Dict,Callable
from pygame import *
from math import atan2
init()
def rot90(v:Vector2,clock:bool=True)->Vector2:
    return Vector2(-int(clock)*v.y,int(clock)*v.x)
def getAngleBetweenVectors(v1,v2):
    return atan2(v1.cross(v2),v1.dot(v2))


def build(p1,p2,p3):
    #s1,s2,s3=buildTriangle(p1,p2,p3,1)

    c=Circle(p1,radius=50,color=(0,0,0))
    t1,t2=buildTangents(p2,c)
    Ray(p2,t1,color=(0,0,0))
    Ray(p2, t2, color=(0, 0, 0))
    #inCircle=buildExternallyInscribedCircle(p1, p2, l1, l2, l3, (True, False),1)
    #outCircle=buildExternallyInscribedCircle(p1, p2, l1, l2, l3, (False, False),1)
    #aroundCricle=buildCircumscribedCircle(p1,p2,p3,3)

    #Ray(p2,inCircle.center,(25,25,25))

    #w=Point(color=(0,255,0),dynamicPosition=lambda:Factory.line2circleSecondPoint(p2,b,aroundCricle))
    #Segment(w,inCircle.center,color=(0,0,255))
    #Segment(w, outCircle.center, color=(0, 0, 255))
    #Segment(w, p1, color=(0, 0, 255))
    #Segment(w, p3, color=(0, 0, 255))


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
            if self.width==1:
                draw.aaline(Drawwer.win, self.color, self.startPoint.xy, self.endPoint.xy)
            else:
                draw.line(Drawwer.win, self.color, self.startPoint.xy, self.endPoint.xy, self.width)

    @staticmethod
    def drawRay(self:Ray):
        if Drawwer.noneColorCheck(self):
            if (self.endPoint-self.startPoint).magnitude_squared()==0:
                return
            direction=(self.endPoint-self.startPoint).normalize()
            draw.line(Drawwer.win,self.color,self.startPoint,self.startPoint+direction*2000)

    @staticmethod
    def drawCircle(self:Circle):
        if Drawwer.noneColorCheck(self):
            if self.radius>100000:
                return
            draw.circle(Drawwer.win, self.color, self.center.xy, self.radius,self.width)
    @staticmethod
    def noneColorCheck(self):
        if not Drawwer.invisible:
            if self.color==None:
                self.color=(25,25,52)
        if self.color == None:
            return False
        else:
            if self.getState():
                return True


    @staticmethod
    def setWin(win:Surface,invisible:bool):
        Drawwer.win=win
        Drawwer.invisible=invisible


class Point(Vector2):
    points:List[Point]=[]
    name="point"
    def __init__(self,pos:Union[List[float],None]=None,color:Union[Tuple[int,int,int],None]=None,isMoveable:bool=False,
                 dynamicPosition:Union[None,Callable]=None):
        self.dynamicPosition=dynamicPosition
        if self.dynamicPosition:
            Factory.management.append(self)
            pos=self.dynamicPosition()
        super(Point, self).__init__(pos)
        self.color=color
        self.isMoveable=isMoveable
        self.state=True
        Point.points.append(self)

    def manage(self):
        pos=self.dynamicPosition()
        if pos==None:
            self.state=False
        else:
            self.state=True
            self.xy=pos

    def draw(self):
        Drawwer.drawPoint(self)

    @staticmethod
    def drawAll():
        for point in Point.points:
            point.draw()

    def getState(self):
        return self.state

class Line:
    lines:List[Line]=[]
    name = "line"
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

    def getState(self):
        return self.startPoint.getState() and self.endPoint.getState()

class Segment(Line):
    segments=[]
    name = "segment"
    def __init__(self,startPoint:Vector2,endPoint:Vector2,color:Union[Tuple[int,int,int],None]=None,width:int=2):
        super(Segment, self).__init__(startPoint,endPoint,color)
        self.width=width
        Segment.segments.append(self)

    def draw(self):
        Drawwer.drawSegment(self)


class Ray(Line):
    name = "ray"
    def __init__(self,startPoint:Vector2,endPoint:Vector2,color:Union[Tuple[int,int,int],None]=None):
        super(Ray, self).__init__(startPoint,endPoint,color)

    def draw(self):
        Drawwer.drawRay(self)

class Circle:
    circles:List[Circle]=[]
    name = "circle"
    def __init__(self,center:Vector2,radiusPoint:Union[Vector2,None]=None,radius:Union[float,None]=None,color:Union[Tuple[int,int,int],None]=None,width:int=2):
        self.center:Vector2=center
        self.color=color
        if radius:
            self.radius = radius
        else:
            Factory.management.append(self)
            self.radiusPoint:Vector2 = radiusPoint
            self.radius = (self.radiusPoint - self.center).magnitude()
        self.width=width
        Circle.circles.append(self)


    def manage(self):
        self.radius=(self.radiusPoint-self.center).magnitude()

    def draw(self):
        Drawwer.drawCircle(self)

    @staticmethod
    def drawAll():
        for circle in Circle.circles:
            circle.draw()

    def getState(self):
        return self.center.getState() and (True if self.radius else self.radiusPoint.getState())

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

class Factory:
    management:List = []

    @staticmethod
    def line2lineKoefs(l1,l2):
        A=l1.startPoint
        B=l1.endPoint
        C=l2.startPoint
        D=l2.endPoint

        if (B - A).cross(D - C) == 0:
            return []
        k = -(A - C).cross(D - C) / (B - A).cross(D - C)
        d = -(C - A).cross(B - A) / (D - C).cross(B - A)
        return [k,d]

    @staticmethod
    def line2lineVectorsKoefs(A:Vector2,B:Vector2,C:Vector2,D:Vector2):
        if (B - A).cross(D - C) == 0:
            return []
        k = -(A - C).cross(D - C) / (B - A).cross(D - C)
        d = -(C - A).cross(B - A) / (D - C).cross(B - A)
        return [k,d]

    @staticmethod
    def line2lineVectors(A:Vector2,B:Vector2,C:Vector2,D:Vector2):

        koefs=Factory.line2lineVectorsKoefs(A,B,C,D)
        if len(koefs)==0:
            return None
        k=koefs[0]
        return A+k*(B-A)

    @staticmethod
    def line2line(l1:Line,l2:Line):
        koefs=Factory.line2lineKoefs(l1,l2)
        if len(koefs)==0:
            return None
        k=koefs[0]
        return l1.startPoint+k*(l1.endPoint-l1.startPoint)

    @staticmethod
    def line2segment(l:Line,s:Segment):
        koefs=Factory.line2lineKoefs(l,s)
        if len(koefs)==0:
            return None
        k=koefs[0]
        d=koefs[1]
        if 0<d and d<1:
            return l.startPoint+k*(l.endPoint-l.startPoint)
        return None

    @staticmethod
    def line2segmentVectors(A:Vector2,B:Vector2,C:Vector2,D:Vector2):
        """
        :param A: segment start
        :param B: segment end
        :param C: line start
        :param D: line end
        :return: intersection
        """
        koefs=Factory.line2lineVectorsKoefs(A,B,C,D)
        if len(koefs)==0:
            return None
        k,d=koefs
        if d>0 and d<1:
            return A+k*(B-A)
        return None

    @staticmethod
    def segment2segment(s1:Segment,s2:Segment):
        koefs=Factory.line2lineKoefs(s1,s2)
        if len(koefs)==0:
            return None
        k=koefs[0]
        d=koefs[1]
        if 0<d and d<1 and 0<k and k<1:
            return s1.startPoint+k*(s1.endPoint-s1.startPoint)
        return None

    @staticmethod
    def segment2segmentVectors(A:Vector2,B:Vector2,C:Vector2,D:Vector2):
        koefs=Factory.line2lineVectorsKoefs(A,B,C,D)
        if len(koefs)==0:
            return None
        k,d=koefs
        if d>0 and d<1 and k>0 and k<1:
            return A+k*(B-A)
        return None

    @staticmethod
    def ray2segmentVectors(A:Vector2,B:Vector2,C:Vector2,D:Vector2):
        koefs=Factory.line2lineVectorsKoefs(A,B,C,D)
        if len(koefs)==0:
            return None
        k,d=koefs
        if k>0 and d>0 and d<1:
            return A+k*(B-A)
        return None

    @staticmethod
    def ray2segment(r:Ray,s:Segment):
        koefs=Factory.line2lineKoefs(r,s)
        if len(koefs)==0:
            return None
        k,d=koefs
        if k>0 and d>0 and d<1:
            return r.startPoint+k*(r.endPoint-r.startPoint)
        return None

    @staticmethod
    def ray2rayVectors(A:Vector2,B:Vector2,C:Vector2,D:Vector2):
        koefs=Factory.line2lineVectorsKoefs(A,B,C,D)
        if len(koefs)==0:
            return None
        k,d=koefs
        if d>0 and k>0:
            return A+k*(B-A)
        return None

    @staticmethod
    def ray2ray(r1:Ray,r2:Ray):
        koefs=Factory.line2lineKoefs(r1,r2)
        if len(koefs)==0:
            return None
        k,d=koefs
        if k>0 and d>0:
            return r1.startPoint+k*(r1.endPoint-r1.startPoint)
        return None

    @staticmethod
    def ray2lineVectors(A:Vector2,B:Vector2,C:Vector2,D:Vector2):
        koefs=Factory.line2lineVectorsKoefs(A,B,C,D)
        if len(koefs)==0:
            return None
        k,d=koefs
        if k>0:
            return A+k*(B-A)
        return None

    @staticmethod
    def ray2line(r:Ray,l:Line):
        koefs=Factory.line2lineKoefs(r,l)
        if len(koefs)==0:
            return None
        k,d=koefs
        if k>0:
            return r.startPoint+k*(r.endPoint-r.startPoint)
        return None


    @staticmethod
    def line2circle(l:Line,c:Circle):
        A=l.startPoint
        B=l.endPoint
        C=c.center
        a=(A-B).magnitude_squared()
        b=2*(A-B).dot(C-A)
        c=(C-A).magnitude_squared()-c.radius**2
        d=b**2-4*a*c
        if d<0:
            return [None,None]
        if d==0:
            k=-b/2/a
            return [A+k*(B-A),None]
        if d>0:
            k1=(-b+d**0.5)/2/a
            k2=(-b-d**0.5)/2/a
            return [A+k1*(B-A),A+k2*(B-A)]

    @staticmethod
    def segment2circle(s:Segment,c:Circle):
        A=s.startPoint
        B=s.endPoint
        C=c.center
        a=(A-B).magnitude_squared()
        b=2*(A-B).dot(C-A)
        c=(C-A).magnitude_squared()-c.radius**2
        d=b**2-4*a*c
        if d<0:
            return [None,None]
        if d==0:
            k=-b/2/a
            if 0<k and k<1:
                return [A+k*(B-A),None]
        if d>0:
            k1=(-b+d**0.5)/2/a
            k2=(-b-d**0.5)/2/a
            res=[]
            if 0<k1 and k1<1:
                res.append(A+k1*(B-A))
            if 0<k2 and k2<1:
                res.append(A+k2*(B-A))
            res.extend([None for _ in range(2-len(res))])
            return res

    @staticmethod
    def ray2circle(r:Ray,c:Circle):
        A=r.startPoint
        B=r.endPoint
        C=c.center
        a=(A-B).magnitude_squared()
        b=2*(A-B).dot(C-A)
        c=(C-A).magnitude_squared()-c.radius**2
        d=b**2-4*a*c
        if d<0:
            return [None,None]
        if d==0:
            k=-b/2/a
            if 0<k:
                return [A+k*(B-A),None]
        if d>0:
            k1=(-b+d**0.5)/2/a
            k2=(-b-d**0.5)/2/a
            res=[]
            if 0<k1:
                res.append(A+k1*(B-A))
            if 0<k2:
                res.append(A+k2*(B-A))
            res.extend([None for _ in range(2-len(res))])
            return res

    @staticmethod
    def circle2circle(c1:Circle,c2:Circle):
        B=c1.center
        C=c2.center

        R1=c1.radius
        R2=c2.radius

        x=(R1**2+(B-C).magnitude_squared()-R2**2)/2/(B-C).magnitude_squared()*(C-B)
        if R1**2<x.magnitude_squared():
            return [None,None]
        if R1**2==x.magnitude_squared():
            return [B+x,None]
        y=rot90(C-B).normalize()*(R1**2-x.magnitude_squared())**0.5
        return [B+x+y,B+x-y]

    @staticmethod
    def circle2circleVectors(B:Vector2,C:Vector2,R1:float,R2:float):
        if (B-C).magnitude_squared()==0:
            return [None,None]
        x=(R1**2+(B-C).magnitude_squared()-R2**2)/2/(B-C).magnitude_squared()*(C-B)
        if R1**2<x.magnitude_squared():
            return [None,None]
        if R1**2==x.magnitude_squared():
            return [B+x,None]
        y=rot90(C-B).normalize()*(R1**2-x.magnitude_squared())**0.5
        return [B+x+y,B+x-y]

    @staticmethod
    def line2circleSecondPoint(basePoint:Point,l:Line,c:Circle):
        points=Factory.line2circle(l,c)
        if points[0]==None:
            return None
        if points[1]==None:
            return points[0]
        if (basePoint-points[0]).magnitude_squared()>(basePoint-points[1]).magnitude_squared():
            return points[0]
        else:
            return points[1]


def inter(a,b,a_class=None,b_class=None,basePoint:Union[Point,None]=None,orientation:bool=False):
    costs=["ray","line","segment","circle"]
    if not a_class:
        a_class=a.__class__.name
        if a_class in ["ray","segment"]:
            a_class="line"
    if not b_class:
        b_class=b.__class__.name
        if b_class in ["ray","segment"]:
            b_class="line"
    a_cost=costs.index(a_class)
    b_cost=costs.index(b_class)

    if b_cost<a_cost:
        a,b=b,a
        a_class,b_class=b_class,a_class
    match (a_class,b_class):
        case ("line","line"):
            return (lambda: Factory.line2line(a,b))
        case ("line","segment"):
            return (lambda: Factory.line2segment(a,b))
        case ("ray","line"):
            return (lambda: Factory.ray2line(a, b))
        case ("segment","segment"):
            return (lambda: Factory.segment2segment(a, b))
        case ("ray","segment"):
            return (lambda: Factory.ray2segment(a,b))
        case ("ray","ray"):
            return (lambda: Factory.ray2ray(a,b))

        case ("line","circle"):
            if basePoint:
                return (lambda: Factory.line2circleSecondPoint(basePoint,a,b))
            return (lambda: Factory.line2circle(a, b)[int(orientation)])
        case ("segment","circle"):
            return (lambda: Factory.segment2circle(a, b)[int(orientation)])
        case ("ray","circle"):
            return (lambda: Factory.ray2circle(a, b)[int(orientation)])
        case ("circle","circle"):
            return (lambda: Factory.circle2circle(a, b)[int(orientation)])

def intersectionPoint(a,b,a_class=None,b_class=None,basePoint:Union[Point,None]=None,orientation:bool=False,color:Tuple[int,int,int]=None):
    return Point(dynamicPosition=inter(a,b,a_class,b_class,basePoint,orientation),color=color)


def buildTriangle(p1,p2,p3,width:int=2):
    s1=Segment(p1,p2,color=(25,25,25),width=width)
    s2=Segment(p2,p3,color=(25,25,25),width=width)
    s3=Segment(p3,p1,color=(25,25,25),width=width)
    return s1,s2,s3


def buildBisectorLine(p,l1:Line,l2:Line,orientation:Tuple[bool,bool]=(False,False),
                  color:Union[None,Tuple[int,int,int]]=None):
    c1=Circle(p,radius=100)
    p11=intersectionPoint(l1, c1, orientation=orientation[0])
    p12=intersectionPoint(l2, c1, orientation=orientation[1])
    bisector=buildMedianPerpendicular(p11,p12,color)
    return bisector

def buildBisectorRay(p,l1:Line,l2:Line,l3:Line,orientation:Tuple[bool,bool]=(False,False),
                  color:Union[None,Tuple[int,int,int]]=None):
    protoBisector=buildBisectorLine(p,l1,l2,orientation)
    p1=intersectionPoint(protoBisector,l3)#Point(dynamicPosition=inter(protoBisector,l3))#lambda: Factory.line2line())
    bisector=Ray(p,p1,color=color)
    return bisector

def buildCevian(p:Point,l:Line,s:Segment):
    p2=intersectionPoint(l,s)#Point(dynamicPosition=inter(l,s))#lambda:Factory.line2line(l,s))
    Segment(p,p2,(250,0,0))

def buildMedianPerpendicular(p1:Point,p2:Point,color:Union[None,Tuple[int,int,int]]=None):
    c1=Circle(p1,p2)
    c2=Circle(p2,p1)
    p3=intersectionPoint(c1,c2,orientation=False)#Point(dynamicPosition=inter(c1,c2,orientation=False))#lambda:Factory.circle2circle(c1,c2)[0])
    p4 =intersectionPoint(c1,c2,orientation=True)# Point(dynamicPosition=inter(c1,c2,orientation=True))
    medianPerpendicular=Line(p3,p4,color)
    return medianPerpendicular

def buildNormal(p:Point,l:Line,color:Union[None,Tuple[int,int,int]]=None):
    c=Circle(p,l.startPoint)
    p1=intersectionPoint(l,c,orientation=False)#Point(dynamicPosition=inter(l,c,orientation=False))#lambda:Factory.line2circle(l,c)[0])
    p2=intersectionPoint(l,c,orientation=True)#Point(dynamicPosition=inter(l,c,orientation=True))#lambda:Factory.line2circle(l,c)[1])
    normal=buildMedianPerpendicular(p1,p2,color)
    return normal

def buildExternallyInscribedCircle(p1,p2,l1,l2,l3,orientation,width=2):
    b1 = buildBisectorLine(p1, l2, l3, (False,orientation[0]))
    b2 = buildBisectorLine(p2, l1, l3, (False,orientation[1]))
    o = intersectionPoint(b1,b2,color=(100,100,0))#Point(color=(100, 100, 0), dynamicPosition=inter(b1,b2))#=lambda: Factory.line2line(b1, b2))
    normal = buildNormal(o, l1, None)
    h = intersectionPoint(l1,normal)#Point(dynamicPosition=inter(l1,normal))#lambda: Factory.line2line(l1, normal))
    c = Circle(o, h, color=(25, 25, 25),width=width)
    return c

def buildCircumscribedCircle(p1,p2,p3,width=2)->Circle:
    """
    Описане коло
    :param p1: вершина1
    :param p2: вершина2
    :param p3: вершина3
    :param width: товщина кола
    :return: Коло описане навколо трикутника
    """
    per1=buildMedianPerpendicular(p1,p2)
    per2=buildMedianPerpendicular(p2,p3)
    cen=intersectionPoint(per1,per2)#Point(dynamicPosition=inter(per1,per2))#lambda:Factory.line2line(per1,per2),color=(200,0,0))
    c=Circle(cen,p1,color=(25,25,25),width=width)
    return c

def buildMidpoint(p1,p2) -> Point:
    l=Line(p1,p2)
    per=buildMedianPerpendicular(p1,p2)
    midPoint=intersectionPoint(l,per)
    return midPoint

def buildTangents(p,c)->List[Point]:
    m=buildMidpoint(p,c.center)
    c2=Circle(m,p)
    t1=intersectionPoint(c,c2,orientation=True)
    t2 = intersectionPoint(c, c2, orientation=False)
    return [t1,t2]

def manage(management):
    for object in management:
        object.manage()

class Game:
    def __init__(self,invisible:bool=False):
        self.WIDTH=1500
        self.HEIGHT=700
        self.FPS=60
        self.BACKGROUND=(200,200,200)

        self.win=display.set_mode((self.WIDTH,self.HEIGHT))
        self.clock=time.Clock()
        self.isRunning=True



        p1=Point([600,100],isMoveable=True,color=(25,25,25))
        p2=Point([700,100],isMoveable=True,color=(25,25,25))
        p3=Point([800, 400],isMoveable=True,color=(25,25,25))
        self.pointMover=PointMover()
        Drawwer.setWin(self.win,invisible)
        build(p1, p2, p3)
    def update(self):
        for even in event.get():
            if even.type==QUIT:
                self.stop()
        self.pointMover.update()
        manage(Factory.management)

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
    game=Game(True)
    game.run()