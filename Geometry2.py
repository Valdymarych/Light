# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Tuple,List,Union,Dict,Callable
from pygame import *
from math import atan2,pi
from time import time as tm
init()
def rot90(v:Vector2,clock:bool=True)->Vector2:
    return Vector2(-int(clock)*v.y,int(clock)*v.x)
def clamp(num, min_value, max_value):
   return max(min(num, max_value), min_value)
def getAngleBetweenVectors(v1,v2):
    return atan2(v1.cross(v2),v1.dot(v2))


def getClosestIntersectionPointParams(p:Vector2):
    primitives=Drawwer.getAllVisibleObjects()
    params={
        "a":None,
        "b":None,
        "a_class":None,
        "b_class":None,
        "orientation":None
    }
    minLength=10000**2
    def checkPos(a,b,pos,orientation=False):
        if pos:
            length = (pos - p).magnitude_squared()
            if length < minLength:
                params["a"]=a
                params["b"]=b
                params["a_class"]=a.__class__.name
                params["b_class"] =b.__class__.name
                params["orientation"]=orientation
                return length
        return minLength
    for a in primitives:
        for b in primitives:
            if a is b:
                continue
            if "circle" in [a.__class__.name,b.__class__.name]:
                pos1=inter(a,b,a.__class__.name,b.__class__.name,orientation=False)()
                pos2 = inter(a, b, a.__class__.name, b.__class__.name, orientation=True)()
                minLength=checkPos(a,b,pos1,False)
                minLength=checkPos(a, b, pos2,True)
            else:
                pos=inter(a,b,a.__class__.name,b.__class__.name)()
                minLength=checkPos(a,b,pos)

    points=Drawwer.getAllVisiblePoints()
    pointsParams=[point.metaParams for point in points]
    for pointParams in pointsParams:
        k=0
        if pointParams:
            if pointParams["a"] is params["a"]:
                k+=1
            if pointParams["b"] is params["b"]:
                k+=1
            if pointParams["orientation"] is params["orientation"]:
                k+=1
        if k==3:
            return 10000,params
    return minLength,params

class GeometryObject:
    def __init__(self,color:Union[Tuple[int,int,int],None]=None):
        self.color=color
        self.invisible=False
    def __point_init__(self,color:Union[Tuple[int,int,int],None]=None):
        self.color=color
        self.invisible=False
    def draw(self):
        pass
    @staticmethod
    def drawAll():
        pass
    def getState(self):
        pass
    def closestPoint(self,p:Vector2):
        pass


class Point(Vector2,GeometryObject):
    points:List[Point]=[]
    name="point"
    def __init__(self,pos:Union[List[float],None]=None,color:Union[Tuple[int,int,int],None]=None,isMoveable:bool=False,
                 restriction:List[object]=None,dynamicPosition:Union[None,Callable]=None,metaParams:Dict=None):
        self.dynamicPosition=dynamicPosition
        self.state = True
        self.restriction=restriction
        if self.restriction:
            Factory.management.append(self)
        if self.dynamicPosition:
            Factory.management.append(self)
            pos=self.manage()
        if self.state:
            super(Point, self).__init__(pos)
        else:
            super(Point, self).__init__(0,0)
        super(Point,self).__point_init__(color)
        self.color=color
        self.isMoveable=isMoveable
        self.metaParams=metaParams

        Point.points.append(self)

    def manage(self):
        if self.restriction:
            self.restrict()
        if self.dynamicPosition:
            pos=self.dynamicPosition()
            if pos==None:
                self.state=False
            else:
                self.state=True
                self.xy=pos
            return pos

    def draw(self):
        Drawwer.drawPoint(self)

    @staticmethod
    def drawAll():
        for point in Point.points:
            point.draw()

    def getState(self):
        return self.state

    def restrict(self):
        poses:List[Union[None,Vector2]]=[restriction.closestPoint(self) for restriction in self.restriction]
        poses_clear:List[Vector2]=[]
        for pos in poses:
            if pos!=False:
                poses_clear.append(pos)
        if len(poses_clear)==0:
            self.state=False
        else:
            self.state=True
            lengths=[(pos-self).magnitude_squared() for pos in poses_clear]
            self.xy=poses_clear[lengths.index(min(lengths))]

class Drawwer:
    win:Union[Surface,None]=None
    winCorners=[

    ]
    winEdges=[

    ]
    @staticmethod
    def drawPoint(self:Point):
        if Drawwer.noneColorCheck(self):
            draw.circle(Drawwer.win, self.color, self.xy, 5)

    @staticmethod
    def drawLine(self:Line):
        if Drawwer.noneColorCheck(self):
            if (self.endPoint-self.startPoint).magnitude_squared()==0:
                return
            points=[]
            for edge in Drawwer.winEdges:
                intersection=Factory.line2segment(self,edge)
                if intersection:
                    points.append(intersection)
            if len(points)!=2:
                return

            draw.line(Drawwer.win,self.color,points[0],points[1])

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
            points=[]
            for edge in Drawwer.winEdges:
                intersection=Factory.ray2segment(self,edge)
                if intersection:
                    points.append(intersection)
            if len(points)==1:
                draw.line(Drawwer.win, self.color, self.startPoint, points[0])
            if len(points)==2:
                draw.line(Drawwer.win, self.color, points[1], points[0])

    @staticmethod
    def drawCircle(self:Circle):
        if Drawwer.noneColorCheck(self):
            if self.radius>100000:
                return
            draw.circle(Drawwer.win, self.color, self.center.xy, self.radius,self.width)
    @staticmethod
    def noneColorCheck(self:GeometryObject):
        if not Drawwer.invisible:
            if self.color==None:
                self.color=(25,25,52)
        if self.color == None:
            return False
        else:
            if self.getState() and self.invisible==False:
                return True


    @staticmethod
    def setWin(win:Surface,invisible:bool):
        Drawwer.win=win
        Drawwer.invisible=invisible
        Drawwer.WIDTH=win.get_width()
        Drawwer.HEIGHT=win.get_height()
        Drawwer.winCorners=[
            Point([0,0]),
            Point([Drawwer.WIDTH,0]),
            Point([Drawwer.WIDTH,Drawwer.HEIGHT]),
            Point([0, Drawwer.HEIGHT])
        ]
        Drawwer.winEdges=[
            Segment(Drawwer.winCorners[0],Drawwer.winCorners[1]),
            Segment(Drawwer.winCorners[1], Drawwer.winCorners[2]),
            Segment(Drawwer.winCorners[2], Drawwer.winCorners[3]),
            Segment(Drawwer.winCorners[3], Drawwer.winCorners[0])
        ]

    @staticmethod
    def getAllVisibleObjects():
        res=[]
        for object in Line.lines+Circle.circles:
            if Drawwer.noneColorCheck(object):
                res.append(object)
        return res

    @staticmethod
    def getAllVisiblePoints():
        res=[]
        for object in Point.points:
            if Drawwer.noneColorCheck(object):
                res.append(object)
        return res


class Line(GeometryObject):
    lines:List[Line]=[]
    name = "line"
    def __init__(self,startPoint:Point,endPoint:Point,color:Union[Tuple[int,int,int],None]=None):
        super(Line, self).__init__(color)
        self.startPoint = startPoint
        self.endPoint = endPoint
        Line.lines.append(self)

    def draw(self):
        Drawwer.drawLine(self)

    @staticmethod
    def drawAll():
        for line in Line.lines:
            line.draw()

    def getState(self):
        return self.startPoint.getState() and self.endPoint.getState()

    def closestPoint(self,p:Vector2):
        if self.getState()==False:
            return False
        ba = self.endPoint - self.startPoint
        pa = p - self.startPoint
        h = pa.dot(ba) / ba.dot(ba)
        return self.startPoint+h*ba
class Segment(Line):
    segments=[]
    name = "segment"
    def __init__(self,startPoint:Point,endPoint:Point,color:Union[Tuple[int,int,int],None]=None,width:int=2):
        super(Segment, self).__init__(startPoint,endPoint,color)
        self.width=width
        Segment.segments.append(self)

    def draw(self):
        Drawwer.drawSegment(self)
    def closestPoint(self,p:Vector2):
        if self.getState()==False:
            return False
        ba = self.endPoint - self.startPoint
        pa = p - self.startPoint
        h = clamp(pa.dot(ba) / ba.dot(ba),0,1)
        return self.startPoint+h*ba
class Ray(Line):
    name = "ray"
    def __init__(self,startPoint:Point,endPoint:Point,color:Union[Tuple[int,int,int],None]=None):
        super(Ray, self).__init__(startPoint,endPoint,color)

    def draw(self):
        Drawwer.drawRay(self)
    def closestPoint(self,p:Vector2):
        if self.getState()==False:
            return False
        ba = self.endPoint - self.startPoint
        pa = p - self.startPoint
        h = max(pa.dot(ba) / ba.dot(ba),0)
        return self.startPoint+h*ba
class Circle(GeometryObject):
    circles:List[Circle]=[]
    name = "circle"
    def __init__(self,center:Point,radiusPoint:Union[Point,None]=None,radius:Union[float,None]=None,
                 color:Union[Tuple[int,int,int],None]=None,width:int=2):
        super(Circle, self).__init__(color)
        self.center:Point=center
        if radius:
            self.radius = radius
        else:
            Factory.management.append(self)
            self.radiusPoint:Point = radiusPoint
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

    def closestPoint(self,p:Vector2):
        if self.getState()==False:
            return False
        a=(p-self.center).normalize()
        return a*self.radius+self.center

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
                if self.currentPoint.restriction:
                    self.currentPoint.restrict()
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
        if d<0 or a==0:
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
        if d<0 or a==0:
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
        d=round(d,2)
        if d<0 or a==0:
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

class AnimFactory:
    win=None
    @staticmethod
    def setWin(win:Surface):
        AnimFactory.win=win

    @staticmethod
    def animPoint(p:Point,color=(0,0,0),length=15):
        def animPointMain(t):
            draw.circle(AnimFactory.win,color,p.xy,5*t/length)
        return Animation(animPointMain,True,length)


    @staticmethod
    def animSegment(s,mode='simple',color=(0,0,0),length=60):
        """
        :param s: Segment
        :param mode: mode in ["simple","symmetry","smoothstep"]
        :return:
        """
        win=AnimFactory.win
        def animSegmentMain(t):
            if mode == "simple":
                draw.aaline(win, color, s.startPoint.xy, (s.startPoint + (s.endPoint - s.startPoint) * t / length).xy)
            if mode == "symmetry":
                draw.aaline(win, color, s.startPoint.xy, (s.startPoint + (s.endPoint - s.startPoint) * t / length/2).xy)
                draw.aaline(win, color, s.endPoint.xy, (s.endPoint + (s.startPoint - s.endPoint) * t / length/2).xy)
            if mode == "smoothstep":
                t = t / 60
                t = t ** 2 * (3 - 2 * t)
                draw.aaline(win, color, s.startPoint.xy, (s.startPoint + (s.endPoint - s.startPoint) * t).xy)

        anim=Animation(animSegmentMain, True, length)
        return anim

    @staticmethod
    def animTriangle(s1,s2,s3,mode="simple"):
        anim = Animation()
        anim.addParallelTask(AnimFactory.animSegment(s1, mode))
        anim.addParallelTask(AnimFactory.animSegment(s2, mode))
        anim.addParallelTask(AnimFactory.animSegment(s3, mode))
        return anim


    @staticmethod
    def animCircle(c:Circle,color=(0,0,0),width=1,length=60):
        def animCircleMain(t):
            if t==length:
                draw.circle(AnimFactory.win,color,c.center,c.radius,width)
            else:
                draw.arc(AnimFactory.win,color,[c.center.x-c.radius,c.center.y-c.radius,2*c.radius,2*c.radius],0,2*pi*t/length,width)
        anim=Animation(animCircleMain, True,length)
        return anim

    @staticmethod
    def animWait(length=60):
        def animWaitMain(t):
            pass
        anim=Animation(animWaitMain,True,length)
        return anim

    @staticmethod
    def removeAnimation(animation:Animation,length=10):
        def removeAnimationMain(t):
            if t==0:
                animation.show=lambda x:None
        anim=Animation(removeAnimationMain,True,length)
        return anim

    @staticmethod
    def reverseAnimation(animation:Animation,length=None):
        showFunc=animation.copyShow
        showFuncLength=animation.frameLen
        if length==None:
            length=showFuncLength
        def reverseAnimationMain(t):
            showFunc(showFuncLength-int(t*showFuncLength/length))

        anim=Animation()
        protoanim=Animation(reverseAnimationMain,True,length)
        anim.addParallelTask(protoanim)
        anim.addParallelTask(AnimFactory.removeAnimation(animation,length))
        anim.addTask(AnimFactory.removeAnimation(protoanim,0))
        return anim
class Animation:
    def __init__(self, anim:Callable=None, base:bool=False, frameLen:int=0):
        """

        :param root: elder animation
        :param anim: drawwing function ( for base==True only )
        :param base: base==True => drawwable; base==False => connection
        """
        self.base:bool = base
        self.anim:Callable = anim
        self.tasks: List[List[Animation]] = []
        self.frameLen=frameLen

    def addTask(self, task: Animation):
        if not self.base:
            self.tasks.append([task])
            self.frameLen+=task.frameLen

    def addParallelTask(self,task:Animation):
        if not self.base:
            if len(self.tasks)==0:
                self.tasks.append([task])
                self.frameLen+=task.frameLen
            else:
                self.tasks[-1].append(task)

    def show(self,t:int):
        """

        :param t: frame index
        :return: None
        """
        self.copyShow(t)

    def copyShow(self,t:int):
        """

        :param t: frame index
        :return: None
        """
        if self.base:
            self.anim(t)
        else:
            for anims in self.tasks:
                if anims[0].frameLen<=t:
                    for anim in anims:
                        anim.show(anims[0].frameLen)
                    t-=anims[0].frameLen
                else:
                    for anim in anims:
                        anim.show(t)
                    break



# inter -(return)> stateCheker(Callable) -(call)> Factory.a2b() -(return)> pos or None

def inter(a,b,a_class=None,b_class=None,basePoint:Union[Point,None]=None,orientation:bool=False,orientationBoth:bool=False):
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
    def getLambda():
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
                if orientationBoth:
                    return (lambda: Factory.line2circle(a, b))
                else:
                    return (lambda: Factory.line2circle(a, b)[int(orientation)])
            case ("segment","circle"):
                if orientationBoth:
                    return (lambda: Factory.segment2circle(a, b))
                else:
                    return (lambda: Factory.segment2circle(a, b)[int(orientation)])
            case ("ray","circle"):
                if orientationBoth:
                    return (lambda: Factory.ray2circle(a, b))
                else:
                    return (lambda: Factory.ray2circle(a, b)[int(orientation)])
            case ("circle","circle"):
                if orientationBoth:
                    return (lambda: Factory.circle2circle(a, b))
                else:
                    return (lambda: Factory.circle2circle(a, b)[int(orientation)])
    lambdaFunction=getLambda()
    def stateChecker():
        if (a.getState()==False) or (b.getState()==False):
            return None
        else:
            return lambdaFunction()

    return stateChecker



def intersectionPoint(a,b,a_class=None,b_class=None,basePoint:Union[Point,None]=None,orientation:bool=False,color:Tuple[int,int,int]=None):
    return Point(dynamicPosition=inter(a,b,a_class,b_class,basePoint,orientation),color=color,metaParams={"a":a,"b":b,"a_class":a_class,"b_class":b_class,"orientation":orientation})


def getBuildAndAnim():

    """
    buildObject (*objects,*params) ->  (mainObject,Tree[Objects])
    :return:
    """

    def build(A,B,C):
        # будуємо кут ABC
        AB=buildLine(A,B,color=(0,0,0))
        BC=buildLine(B,C,color=(0,0,0))
        CA = buildLine(C,A,color=(0,0,0))

        circle=buildCircumscribedCircle(A,B,C,color=(0,0,0))
        return None

    def buildCircle(center:Point,radiusPoint:Union[Point,None]=None,radius:Union[float,None]=None,
                 color:Union[Tuple[int,int,int],None]=None,width:int=2):
        return Circle(center,radiusPoint,radius,color,width)

    def buildLine(startPoint:Point,endPoint:Point,color:Union[Tuple[int,int,int],None]=None):
        return Line(startPoint,endPoint,color)

    def buildSegment(startPoint:Point,endPoint:Point,color:Union[Tuple[int,int,int],None]=None,width:int=2):
        return Segment(startPoint,endPoint,color,width)

    def buildRay(startPoint:Point,endPoint:Point,color:Union[Tuple[int,int,int],None]=None):
        return Ray(startPoint,endPoint,color)

    def buildTriangle(p1,p2,p3,color=(25,25,25),width:int=2):
        s1=buildSegment(p1,p2,color=color,width=width)
        s2=buildSegment(p2,p3,color=color,width=width)
        s3=buildSegment(p3,p1,color=color,width=width)

        return [s1,s2,s3]


    def buildBisectorLine(p,l1:Line,l2:Line,orientation:Tuple[bool,bool]=(False,False),
                      color:Union[None,Tuple[int,int,int]]=None):
        c1=buildCircle(p,radius=100)
        p11=intersectionPoint(l1, c1, orientation=orientation[0])
        p12=intersectionPoint(l2, c1, orientation=orientation[1])
        bisector=buildMedianPerpendicular(p11,p12,color)
        return bisector

    def buildBisectorRay(p,l1:Line,l2:Line,l3:Line,orientation:Tuple[bool,bool]=(False,False),
                      color:Union[None,Tuple[int,int,int]]=None):
        protoBisector=buildBisectorLine(p,l1,l2,orientation)
        p1=intersectionPoint(protoBisector,l3)#Point(dynamicPosition=inter(protoBisector,l3))#lambda: Factory.line2line())
        bisector=buildRay(p,p1,color=color)
        return bisector

    def buildCevian(p:Point,l:Line,s:Segment):
        p2=intersectionPoint(l,s)#Point(dynamicPosition=inter(l,s))#lambda:Factory.line2line(l,s))
        return buildSegment(p,p2,(250,0,0))

    def buildMedianPerpendicular(p1:Point,p2:Point,color:Union[None,Tuple[int,int,int]]=None):
        c1=buildCircle(p1,p2)
        c2=buildCircle(p2,p1)
        p3=intersectionPoint(c1,c2,orientation=False)#Point(dynamicPosition=inter(c1,c2,orientation=False))#lambda:Factory.circle2circle(c1,c2)[0])
        p4 =intersectionPoint(c1,c2,orientation=True)# Point(dynamicPosition=inter(c1,c2,orientation=True))
        medianPerpendicular=buildLine(p3,p4,color)
        return medianPerpendicular

    def buildNormal(p:Point,l:Line,color:Union[None,Tuple[int,int,int]]=None):
        if l.endPoint is p:
            c=buildCircle(p,l.startPoint)
        else:
            c = buildCircle(p, l.endPoint)
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
        c = buildCircle(o, h, color=(25, 25, 25),width=width)
        return c

    def buildCircumscribedCircle(p1,p2,p3,color=None,width=2)->Circle:
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
        c=buildCircle(cen,p1,color=color,width=width)
        return c

    def buildMidpoint(p1,p2) -> Point:
        l=buildLine(p1,p2)
        per=buildMedianPerpendicular(p1,p2)
        midPoint=intersectionPoint(l,per)
        return midPoint

    def buildTangents(p,c)->List[Point]:
        m=buildMidpoint(p,c.center)
        c2=buildCircle(m,p)
        t1=intersectionPoint(c,c2,orientation=True)
        t2 = intersectionPoint(c, c2, orientation=False)
        return [t1,t2]

        return build

    def anim(A,B,C):
        root=Animation()

        def recurse(A,B,C,iter=5):
            M1=Point(dynamicPosition=lambda :(A+B)/2)#buildMidpoint(A,B)
            M2=Point(dynamicPosition=lambda :(B+C)/2)
            M3=Point(dynamicPosition=lambda :(A+C)/2)

            tringleAnim = Animation()
            tringleAnim.addTask(AnimFactory.animTriangle(buildSegment(M1,M2),buildSegment(M2,M3),buildSegment(M3,M1)))
            if iter>0:
                nextgen=Animation()

                nextgen.addParallelTask(recurse(M1,M2,B,iter-1))
                nextgen.addParallelTask(recurse(A, M3, M1,iter-1))
                nextgen.addParallelTask(recurse(M3,C,M2,iter-1))
                tringleAnim.addTask(nextgen)
            return tringleAnim

        AB=buildSegment(A,B)
        BC = buildSegment(B,C)
        CA = buildSegment(C,A)

        serpinsky=recurse(A,B,C)
        triangle=AnimFactory.animTriangle(AB,BC,CA)

        root.addTask(triangle)


        root.addTask(serpinsky)
        root.addTask(AnimFactory.reverseAnimation(serpinsky))
        root.addTask(AnimFactory.reverseAnimation(triangle))

        return root

    return build,anim



build,anim=getBuildAndAnim()
def manage(management):
    for object in management:
        object.manage()

class Game:
    WIDTH = 1500
    HEIGHT = 700
    def __init__(self,invisible:bool=False):
        self.WIDTH=Game.WIDTH
        self.HEIGHT=Game.HEIGHT
        self.FPS=60
        self.BACKGROUND=(200,200,200)

        self.win=display.set_mode((self.WIDTH,self.HEIGHT))
        self.clock=time.Clock()
        self.isRunning=True



        p1=Point([750,100],isMoveable=True,color=(25,25,25))
        p2=Point([1300,600],isMoveable=True,color=(25,25,25))
        p3=Point([200, 600],isMoveable=True,color=(25,25,25))
        self.pointMover=PointMover()
        Drawwer.setWin(self.win,invisible)
        AnimFactory.setWin(self.win)
        build(p1, p2, p3)
        self.anim=anim(p1,p2,p3)
        print(len(Line.lines),len(Circle.circles),len(Point.points))
        self.t=0
    def update(self):
        self.pointMover.update()
        for even in event.get():
            self.evenHandler(even)
        manage(Factory.management)

    def draw(self):
        if False:
            Line.drawAll()
            Circle.drawAll()
            Point.drawAll()
        else:
            self.anim.show(self.t)
        self.t += 1


    def windowUpdate(self):
        display.update()
        self.win.fill(self.BACKGROUND)
        display.set_caption(str(round(self.clock.get_fps())))
        self.clock.tick(self.FPS)

    def run(self):
        self.win.fill(self.BACKGROUND)
        while self.isRunning:
            self.update()
            self.draw()
            self.windowUpdate()
        quit()

    def stop(self):
        self.isRunning=False

    def evenHandler(self,even):
        if even.type==QUIT:
            self.stop()
if __name__=="__main__":
    game=Game(True)
    game.run()