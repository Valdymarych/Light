from __future__ import annotations
from typing import Tuple,List,Union,Dict
from pygame import *
import random as rd
from math import pi,asin
from pickle import dumps,loads
from time import time as tm

init()
font.init()

def rot90(v:Vector2,clock:bool=True)->Vector2:
    return Vector2(-int(clock)*v.y,int(clock)*v.x)

def getProjection(v1:Vector2,base:Vector2)->Vector2:
    return base.normalize() * v1.dot(base) / base.magnitude()

class PointsMover:
    def __init__(self,points:List[Point]):
        self.points=points
        self.movedPoint:Point=None

    def move(self,mpos:Vector2,mpess:Tuple[bool,bool,bool]):
        if mpess[0]:
            if not self.movedPoint:
                minDistance: float = 30 ** 2 + 1
                self.movedPoint = None
                for point in self.points:
                    distance = (point.pos - mpos).magnitude_squared()
                    if distance < minDistance:
                        minDistance = distance
                        self.movedPoint = point
            if self.movedPoint:
                PointsMover.movePoint(self.movedPoint,mpos)
        else:
            self.movedPoint=None

    def setPoints(self,points:List[Point]):
        self.points=points

    @staticmethod
    def movePoint(point:Point,mPos:Vector2):
        dPos=Vector2(mPos.x-round(point.pos.x),mPos.y-round(point.pos.y))
        point.pos.xy = mPos
        if len(point.skeleton.points)==1:
            for dependent in point.skeleton.dependents:
                PointsMover.moveSkeleton(dependent,dPos)

    @staticmethod
    def moveSkeleton(skeleton:Skeleton,dPos:Vector2):
        for point in skeleton.points:
            point.pos.xy+=dPos
        for dependent in skeleton.dependents:
            PointsMover.moveSkeleton(dependent,dPos)

class Point:
    def __init__(self,name:str,pos:Vector2,skeleton:Skeleton):
        self.name=name
        self.pos=pos
        self.skeleton=skeleton
    def __str__(self):
        return self.name+str(self.skeleton.body)

class Skeleton:
    def __init__(self,points: Dict[str,Vector2],body:any):
        self.points=[Point(name,pos,self) for name,pos in points.items()]

        self.body=body
        self.dependents:List[Skeleton]=[]

    def addDependent(self,other:Skeleton):
        self.dependents.append(other)

    def draw(self,win:Surface):
        for point in self.points:
            draw.circle(win,(255,255,0),point.pos,5)
        for dependent in self.dependents:
            dependent.draw(win)

    def getPoints(self) -> Tuple[List[Point],List[Point]]:
        pointsDependent=[]
        points=[]
        for dependent in self.dependents:
            p=dependent.getPoints()
            points.extend(p[1])
            pointsDependent.extend(p[0])
        pointsDependent.extend(points)
        return (pointsDependent,self.points)

class Intersection:
    def __init__(self,pos: Vector2,cameDir: Vector2,wentDirs: List[Vector2],barrier:Barrier,length:float):
        self.pos: Vector2=pos
        self.cameDir: Vector2=cameDir
        self.wentDirs: List[Vector2]=wentDirs
        self.length: float=length
        self.barrier:Barrier=barrier

    def getImaginaryRays(self) -> list:
        return [ImaginaryRay(self.pos,-direction) for direction in self.wentDirs]

class Barrier:
    barriers=[]
    def __init__(self,isCollectingImaginaryRays:bool=False):
        self.isCollectingImaginaryRays=isCollectingImaginaryRays
        Barrier.barriers.append(self)
        self.skeleton:Skeleton=Skeleton({},self)

    def build(self):  # sceleton -> points -> other
        pass

    def getIntersections(self,startPos:Vector2,startDir:Vector2,source:any) -> List[Intersection]:
        pass

    def draw(self,win:Surface):
        pass

    def getInitData(self):
        return [self.isCollectingImaginaryRays]

    @staticmethod
    def getIcoSurface(size:int) -> Surface:
        surf=Surface((size, size))
        return surf

class FlatBarrier(Barrier):
    def __init__(self,start: Vector2,end: Vector2,isCollectingImaginaryRays:bool=False):
        super(FlatBarrier, self).__init__(isCollectingImaginaryRays)
        self.start=start
        self.end=end
        self.along:Vector2=self.end-self.start
        self.center=self.start+self.along/2
        self.length:float=0
        self.normal:Vector2=Vector2(0,0)
        self.alongNormal:Vector2=Vector2(0,0)
        self.skeleton:Skeleton=Skeleton({"center":self.center},self)
        self.skeleton.addDependent(Skeleton({"start":self.start},self))
        self.build()

    def build(self):
        self.end=2*self.center-self.start
        self.along: Vector2 = self.end - self.start
        self.length: float = self.along.magnitude()
        if self.length==0:
            self.center.xy=(self.start+Vector2(0.1,0)).xy
            self.build()
            return
        self.normal: Vector2 = Vector2(-self.along.y, self.along.x) / self.length
        self.alongNormal: Vector2 = self.along.normalize()

    def getIntersections(self, startPos: Vector2, startDir: Vector2, source:any) -> List[Intersection]:
        x1,y1=self.start.xy
        dx1,dy1=self.along.xy
        x2,y2=startPos.xy
        dx2,dy2=(startDir*32000).xy

        if source and source.barrier==self:
            return []

        if dy1*dx2!=dx1*dy2:
            s=(y2*dx2-y1*dx2+x1*dy2-x2*dy2)/(dy1*dx2-dx1*dy2)
            if abs(dx2)>abs(dy2):
                t=(x1-x2+s*dx1)/dx2
            else:
                t=(y1-y2+s*dy1)/dy2
            if 0<s<1 and 0<t<1:
                return self.getAngle(Intersection(self.start + self.along * s, startDir,[],self,32000*t))
        return []

    def getAngle(self,intersection:Intersection)->List[Intersection]:
        pass

    def getInitData(self):
        return [self.start,self.end,self.isCollectingImaginaryRays]

class FlatMirror(FlatBarrier):
    strokeStep=20
    stroke=Vector2(10,10)
    def __init__(self,start: Vector2,end: Vector2,isCollectingImaginaryRays:bool=False):
        super(FlatMirror, self).__init__(start,end,isCollectingImaginaryRays)

    def build(self):
        super(FlatMirror, self).build()
        self.strokeCount=int(self.length/FlatMirror.strokeStep)+1
        self.strokeStep=self.length/self.strokeCount

    def getAngle(self,intersection:Intersection) ->List[Intersection]:
        exist = float(self.along.cross(intersection.cameDir))
        if exist > 0:
            nextDir = intersection.cameDir - 2 * self.normal * self.normal.dot(intersection.cameDir)
            return [Intersection(intersection.pos, intersection.cameDir, [nextDir], intersection.barrier,intersection.length)]

        return [Intersection(intersection.pos, intersection.cameDir, [], intersection.barrier, intersection.length)]

    def draw(self,win):
        draw.line(win,(255,255,255),self.start,self.end)
        for i in range(self.strokeCount):
            draw.line(win,(255,0,255),self.start+self.alongNormal*self.strokeStep*(i+0.5),self.start+self.alongNormal*(self.strokeStep*(i+0.5)+FlatMirror.stroke.x)+self.normal*FlatMirror.stroke.y)

    def getInitData(self):
        return [self.start,self.end,self.isCollectingImaginaryRays]

class FlatRefractingSurface(FlatBarrier):
    def __init__(self,start: Vector2,end: Vector2,n0:float,n:float,isMirror:bool=False,isCollectingImaginaryRays:bool=False):
        super(FlatRefractingSurface, self).__init__(start,end,isCollectingImaginaryRays)
        self.n0:float=n0
        self.n:float=n
        self.isMirror=isMirror
    def getAngle(self,intersection:Intersection) ->List[Intersection]:
        x = self.alongNormal.dot(intersection.cameDir)
        direction = float(self.along.cross(intersection.cameDir))
        n = self.n / self.n0
        if direction < 0:
            n = self.n0 / self.n

        nextDirs = [intersection.cameDir - 2 * self.normal * self.normal.dot(intersection.cameDir)] if self.isMirror else []
        if abs(n * x)>1:  # sin B > 1
            #nextDir=self.alongNormal*x/abs(x)
            return [Intersection(intersection.pos, intersection.cameDir, nextDirs, intersection.barrier,
                                 intersection.length)]
        else:
            y = n * x * ((1 - x ** 2) / (1 - (x*n) ** 2)) ** 0.5
            nextDir = intersection.cameDir - self.alongNormal * (x - y)
            nextDir.normalize()
            nextDirs.append(nextDir)
            return [Intersection(intersection.pos, intersection.cameDir, nextDirs, intersection.barrier,
                                 intersection.length)]

    def draw(self,win):
        draw.line(win,(255,255,255),self.start,self.end)

    def getInitData(self):
        return [self.start,self.end,self.n0,self.n,self.isMirror,self.isCollectingImaginaryRays]

class FlatScreen(FlatBarrier):
    def __init__(self,start:Vector2,end:Vector2):
        super(FlatScreen, self).__init__(start,end,False)

    def getAngle(self,intersection:Intersection) ->List[Intersection]:
        return [Intersection(intersection.pos,intersection.cameDir,[],intersection.barrier,intersection.length)]

    def draw(self,win:Surface):
        draw.line(win,(255,255,255),self.start,self.end)

    def getInitData(self):
        return [self.start,self.end]

class SphericalBarrier(Barrier):
    def __init__(self,center:Vector2,mainPolus:Vector2,height:float,isCollectingImaginaryRays:bool=False):
        super(SphericalBarrier, self).__init__(isCollectingImaginaryRays)
        self.center:Vector2=center
        self.mainPolus:Vector2=mainPolus
        self.height:float=height
        self.skeleton:Skeleton=Skeleton({"center":self.center},self)
        self.skeleton.addDependent(Skeleton({"polus":self.mainPolus},self))
        self.normal:Vector2=Vector2(0,0)
        self.mainRadius:Vector2=Vector2(0,0)
        self.radius:float=0
        self.startAngle:float=0
        self.endAngle:float=0
        self.build()

    def build(self):
        self.mainRadius = self.mainPolus - self.center
        if self.mainRadius.magnitude()==0:
            self.mainPolus+=Vector2(0.1,0)
            self.mainRadius=Vector2(0.1,0)
        self.normal=-self.mainRadius.normalize()
        self.radius=self.mainRadius.magnitude()
        if self.mainRadius.magnitude_squared()<self.height**2/4:
            self.edge =rot90(self.normal) * self.radius
        else:
            self.edge=-self.normal*(self.mainRadius.magnitude_squared()-self.height**2/4)**(1/2)+rot90(self.normal)*self.height/2

        self.startAngle=asin(min(1,max([-1,-self.edge.y/self.radius])))
        if self.edge.x<0:
            self.startAngle=-pi-self.startAngle

        self.endAngle=self.startAngle-2*asin(min(1,max([-1,self.height/2/self.radius])))

    def getIntersections(self,startPos:Vector2,startDir:Vector2,source:any) -> List[Intersection]:
        return []

    def getAngles(self,intersection:Intersection) -> List[Intersection]:
        return []

    def draw(self,win:Surface):
        draw.arc(win,(255,255,255),[*(self.center-Vector2(self.radius,self.radius)).xy,2*self.radius,2*self.radius],self.endAngle,self.startAngle)

    def getInitData(self):
        return [self.center,self.mainPolus,self.height,self.isCollectingImaginaryRays]

class SphericalBarrierReal(SphericalBarrier):
    def __init__(self,center:Vector2,mainPolus:Vector2,height:float,isCollectingImaginaryRays:bool=False):
        super(SphericalBarrierReal, self).__init__(center,mainPolus,height,isCollectingImaginaryRays)
        self.build()

    def getIntersections(self,startPos:Vector2,startDir:Vector2,source:any) -> List[Intersection]:
        v1=startPos-self.center
        v2=Vector2(-startDir.y,startDir.x)
        d=getProjection(v1,v2)
        if self.radius**2>=d.magnitude()**2:
            intersection1=self.center+d-startDir.normalize()*(self.radius**2-d.magnitude()**2)**(1/2)
            intersection2=self.center+d+startDir.normalize()*(self.radius**2-d.magnitude()**2)**(1/2)
            intersects:List[Vector2]=[i for i in [intersection1,intersection2] if getProjection(i-self.center,rot90(self.normal)).magnitude()<self.height/2 and self.normal.dot(i-self.center)<0 and (i-startPos).dot(startDir)>0 and (i-startPos).magnitude()>0.01]
            if len(intersects)>0:
                intersect=intersects[0]
                if len(intersects)==2:
                    intersect=intersects[1] if (intersects[0]-startPos).magnitude()>(intersects[1]-startPos).magnitude() else intersects[0]
                return self.getAngles(Intersection(intersect,startDir,[],self,(intersect-startPos).magnitude()))
        return []

    def getAngles(self,intersection:Intersection) -> List[Intersection]:
        return []

    def draw(self,win:Surface):
        draw.arc(win,(255,255,255),[*(self.center-Vector2(self.radius,self.radius)).xy,2*self.radius,2*self.radius],self.endAngle,self.startAngle)

    def getInitData(self):
        return [self.center,self.mainPolus,self.height,self.isCollectingImaginaryRays]

class SphericalBarrierUnReal(SphericalBarrier):
    def __init__(self,center:Vector2,mainPolus:Vector2,height:float,isCollectingImaginaryRays:bool=False):
        super(SphericalBarrierUnReal, self).__init__(center,mainPolus,height,isCollectingImaginaryRays)
        self.build()

    def getIntersections(self,startPos:Vector2,startDir:Vector2,source:any) -> List[Intersection]:
        along = rot90(self.normal) * min(2*self.radius,self.height)
        start=self.mainPolus-along/2

        x1, y1 = start.xy
        dx1, dy1 = along.xy
        x2, y2 = startPos.xy
        dx2, dy2 = (startDir*32000).xy

        if source and source.barrier == self:
            return []

        if dy1 * dx2 != dx1 * dy2:
            s = (y2 * dx2 - y1 * dx2 + x1 * dy2 - x2 * dy2) / (dy1 * dx2 - dx1 * dy2)
            if abs(dx2) > abs(dy2):
                t = (x1 - x2 + s * dx1) / dx2
            else:
                t = (y1 - y2 + s * dy1) / dy2
            if 0 < s < 1 and 0 < t < 1:
                return self.getAngles(Intersection(start + along * s, startDir, [], self, t*32000))
        return []

    def getAngles(self,intersection:Intersection) -> List[Intersection]:
        return []

    def draw(self,win:Surface):
        draw.arc(win,(255,255,255),[*(self.center-Vector2(self.radius,self.radius)).xy,2*self.radius,2*self.radius],self.endAngle,self.startAngle)

    def getInitData(self):
        return [self.center,self.mainPolus,self.height,self.isCollectingImaginaryRays]

class SphericalMirrorReal(SphericalBarrierReal):
    strokeStep=20
    stroke=Vector2(10,10)
    def __init__(self,center:Vector2,mainPolus:Vector2,height:float,isCollectingImaginaryRays:bool=False,isConcave:bool=True):
        super(SphericalMirrorReal, self).__init__(center,mainPolus,height,isCollectingImaginaryRays)
        self.isConcave:bool=isConcave
        self.strokeCount:int=0
        self.strokeStep:int=0

    def build(self):
        super(SphericalMirrorReal, self).build()
        length=2 * asin(min(1, max([-1, self.height / 2 / self.radius])))*self.radius
        self.strokeCount=int(length/SphericalMirrorReal.strokeStep)+1
        self.strokeStep=length/self.strokeCount/self.radius

    def getAngles(self,intersection:Intersection) -> List[Intersection]:

        normal = (self.center - intersection.pos).normalize()
        if normal.dot(intersection.cameDir) * (int(self.isConcave) * 2 - 1) < 0:
            intersection.wentDirs=[intersection.cameDir-2*getProjection(intersection.cameDir,normal)]
        return [intersection]

    def getInitData(self):
        return [self.center,self.mainPolus,self.height,self.isCollectingImaginaryRays,self.isConcave]

    def draw(self,win:Surface):
        super(SphericalMirrorReal, self).draw(win)
        for i in range(self.strokeCount):
            start=self.center+Vector2(self.radius,0).rotate_rad(-self.startAngle+(i+0.5)*self.strokeStep)
            draw.line(win,(255,0,0),start,start+(int(self.isConcave)*2-1)*SphericalMirrorReal.stroke.rotate_rad(-self.startAngle+(i+0.5)*self.strokeStep),2)

class SphericalMirrorUnReal(SphericalBarrierUnReal):
    strokeStep=20
    stroke=Vector2(10,10)
    def __init__(self,center:Vector2,mainPolus:Vector2,height:float,isCollectingImaginaryRays:bool=False,isConcave:bool=True):
        super(SphericalMirrorUnReal, self).__init__(center,mainPolus,height,isCollectingImaginaryRays)
        self.isConcave:bool=isConcave
        self.strokeCount:int=0
        self.strokeStep:int=0

    def build(self):
        super(SphericalMirrorUnReal, self).build()
        length=2 * asin(min(1, max([-1, self.height / 2 / self.radius])))*self.radius
        self.strokeCount=int(length/SphericalMirrorReal.strokeStep)+1
        self.strokeStep=length/self.strokeCount/self.radius


    def getAngles(self,intersection:Intersection) -> List[Intersection]:
        normal = (self.center - intersection.pos).normalize()
        if normal.dot(intersection.cameDir) * (int(self.isConcave) * 2 - 1) < 0:
            inters=intersection.pos-self.mainPolus
            intersx=-getProjection(inters,self.normal)
            dirx=-getProjection(intersection.cameDir,self.normal)
            diry=getProjection(intersection.cameDir,rot90(self.normal))
            if dirx.x==0:
                dirx.x=0.0001
            if dirx.x>0:
                return []
            newInters=intersection.pos-intersection.cameDir*intersx.x/dirx.x

            focus=self.mainRadius/2+self.center
            secondFocus=focus-diry*self.mainRadius.x/2/dirx.x
            intersection.wentDirs=[(int(self.isConcave)*2-1)*(secondFocus-newInters).normalize()]
            intersection.pos=newInters


        return [intersection]

    def getInitData(self):
        return [self.center,self.mainPolus,self.height,self.isCollectingImaginaryRays,self.isConcave]

    def draw(self,win:Surface):
        super(SphericalMirrorUnReal, self).draw(win)
        for i in range(self.strokeCount):
            start=self.center+Vector2(self.radius,0).rotate_rad(-self.startAngle+(i+0.5)*self.strokeStep)
            draw.line(win,(255,0,0),start,start+(int(self.isConcave)*2-1)*SphericalMirrorUnReal.stroke.rotate_rad(-self.startAngle+(i+0.5)*self.strokeStep),2)
        along = rot90(self.normal) * min(2*self.radius,self.height)
        start=self.mainPolus-along/2
        draw.line(win,(255,255,255),start,start+along)

class SphericalRefractingSurfaceReal(SphericalBarrierReal):
    def __init__(self,center:Vector2,mainPolus:Vector2,height:float,n0:float,n:float,isCollectingImaginaryRays:bool=False):
        super(SphericalRefractingSurfaceReal, self).__init__(center,mainPolus,height,isCollectingImaginaryRays)
        self.n:float=n
        self.n0:float=n0

    def getIntersections(self,startPos:Vector2,startDir:Vector2,source:any) -> List[Intersection]:
        if source and source.barrier==self:
            return []
        return super(SphericalRefractingSurfaceReal, self).getIntersections(startPos,startDir,source)

    def getAngles(self,intersection:Intersection) -> List[Intersection]:
        normal=(self.center-intersection.pos).normalize()
        alongNormal=rot90(normal)
        x = alongNormal.dot(intersection.cameDir)

        direction = float(alongNormal.cross(intersection.cameDir))
        n = self.n / self.n0
        if direction < 0:
            n = self.n0 / self.n

        nextDirs = []
        if abs(n * x)>1:  # sin B > 1
            #nextDir=self.alongNormal*x/abs(x)
            return [Intersection(intersection.pos, intersection.cameDir, nextDirs, intersection.barrier,
                                 intersection.length)]
        else:
            y = n * x * ((1 - x ** 2) / (1 - (x*n) ** 2)) ** 0.5
            nextDir = intersection.cameDir - alongNormal * (x - y)
            nextDir.normalize()
            nextDirs.append(nextDir)
            return [Intersection(intersection.pos, intersection.cameDir, nextDirs, intersection.barrier,
                                 intersection.length)]


    def getInitData(self):
        return [self.center,self.mainPolus,self.height,self.n0,self.n,self.isCollectingImaginaryRays]

class Lens(Barrier):
    stroke=Vector2(10,30)
    def __init__(self,center:Vector2,focus:Vector2,height:float,isConverging=True,isCollectingImaginaryRays:bool=False):
        super(Lens, self).__init__(isCollectingImaginaryRays)
        self.center=center
        self.focus=focus
        self.height=height
        self.normal:Vector2=Vector2(0,0)
        self.alongNormal:Vector2=Vector2(0,0)
        self.start:Vector2=Vector2(0,0)
        self.end:Vector2=Vector2(0,0)
        self.along:Vector2=Vector2(0,0)
        self.focal:Vector2=Vector2(0,0)
        self.isConverging=isConverging
        self.stroke=Vector2(Lens.stroke.x,(2*int(self.isConverging)-1)*Lens.stroke.y)
        self.build()
        self.skeleton: Skeleton = Skeleton({"center": self.center},self)
        self.skeleton.addDependent(Skeleton({"focus": self.focus},self))

    def build(self):
        self.focal=self.focus-self.center
        if self.focal.magnitude_squared()==0:
            self.focal=Vector2(0.1,0)
            self.focus.xy=self.center+self.focal.xy
        self.normal=self.focal.normalize()
        self.alongNormal=rot90(self.normal)
        self.start=self.center-self.alongNormal*self.height/2
        self.end=self.start+self.alongNormal*self.height
        self.along=self.end-self.start


    def getIntersections(self,startPos:Vector2,startDir:Vector2,source:any) -> List[Intersection]:
        if source and source.barrier==self:
            return []
        x1,y1=self.start.xy
        dx1,dy1=self.along.xy
        x2,y2=startPos.xy
        dx2,dy2=startDir.xy

        if dy1*dx2!=dx1*dy2:
            s=(y2*dx2-y1*dx2+x1*dy2-x2*dy2)/(dy1*dx2-dx1*dy2)
            if abs(dx2)>abs(dy2):
                t=(x1-x2+s*dx1)/dx2
            else:
                t=(y1-y2+s*dy1)/dy2
            if 0<s<1 and 0<t:
                inter=self.start + self.along * s
                if getProjection(startDir.normalize(),self.normal).x==0:
                    focus=self.center+startDir*abs(self.focal.y/getProjection(startDir.normalize(),self.normal).y)
                else:
                    focus=self.center+startDir*abs(self.focal.x/getProjection(startDir.normalize(),self.normal).x)

                wentDir=(focus-inter).normalize()
                if not self.isConverging:
                    wentDir=-(self.center*2-focus-inter).normalize()
                return [Intersection(inter,startDir,[wentDir],self,t)]

        return []

    def draw(self,win:Surface):

        draw.line(win,(255,255,255),self.start,self.end)
        draw.line(win,(255,255,255),self.start,self.start+self.normal*self.stroke.x+self.alongNormal*self.stroke.y)
        draw.line(win, (255, 255, 255), self.start,self.start - self.normal * self.stroke.x + self.alongNormal * self.stroke.y)
        draw.line(win,(255,255,255),self.end,self.end+self.normal*self.stroke.x-self.alongNormal*self.stroke.y)
        draw.line(win, (255, 255, 255), self.end,self.end - self.normal * self.stroke.x - self.alongNormal * self.stroke.y)

    def getInitData(self):
        return [self.center,self.focus,self.height,self.isConverging,self.isCollectingImaginaryRays]

    @staticmethod
    def getIcoSurface(size:int,isConverging:bool=True) -> Surface:
        h=int(size*0.1)
        if not isConverging:
            h=int(size*0.25)
        w=int(size*0.5)
        surf=Surface((size,size))
        start=Vector2(w,h)
        end=Vector2(w,size-h)
        normal=Vector2(1,0)
        alongNormal=Vector2(0,1)
        stroke=Lens.stroke/2
        if not isConverging:
            stroke=Vector2(Lens.stroke.x,-Lens.stroke.y)/2
        draw.line(surf,(255,255,255),start,end,2)
        draw.line(surf,(255,255,255),start,start+normal*stroke.x+alongNormal*stroke.y,2)
        draw.line(surf, (255, 255, 255), start,start - normal * stroke.x + alongNormal * stroke.y,2)
        draw.line(surf,(255,255,255),end,end+normal*stroke.x-alongNormal*stroke.y,2)
        draw.line(surf, (255, 255, 255), end,end - normal * stroke.x - alongNormal * stroke.y,2)
        return surf


class Source:
    sources=[]
    def __init__(self,pos:Vector2,color:Tuple[int,int,int]=(255,255,255),rayDirs:List[Vector2]=[]):
        self.pos:Vector2=pos
        self.rays:List[Ray]=[]
        for direction in rayDirs:
            self.addRay(direction)
        self.imaginaryRays:List[ImaginaryRay]=[]
        self.color:Tuple[int,int,int]=color
        self.strokes=[]
        self.skeleton=Skeleton({"pos":self.pos},self)
        for i in range(20):
            self.strokes.append(Vector2((2*rd.random()-1)*10).rotate(rd.random()*360))
        Source.sources.append(self)

    def addRay(self,dir):
        self.rays.append(Ray(self.pos,dir,self))

    def addImaginaryRay(self,ray):
        self.imaginaryRays.append(ray)

    def fullConstruct(self,barriers):
        self.imaginaryRays.clear()
        for ray in self.rays:
            ray.fullConstruct(barriers)

    def draw(self,win):
        for ray in self.rays:
            ray.draw(win,self.color)
        for imaginaryRay in self.imaginaryRays:
            imaginaryRay.draw(win,self.color)
        for stroke in self.strokes:
            draw.line(win,self.color,self.pos,self.pos+stroke,2)
    def getInitData(self):
        return [self.pos,self.color,[ray.startDir for ray in self.rays]]

class Ray:
    maxDepth=50
    minLength=4000

    def __init__(self, pos: Vector2, direction: Vector2, source:Source):
        self.startPos: Vector2 = pos
        self.startDir: Vector2 = direction/direction.length()
        self.construction:List[Union[Tuple,Vector2]]=[Vector2(0,0)]
        self.source:Source=source

    def construct(self,barriers:List[Barrier],depth:int,tempSource:Intersection=None):
        intersection: Intersection=Intersection(self.startPos+self.startDir*3000,self.startDir,[],tempSource.barrier if tempSource else tempSource,32000)
        if depth>Ray.maxDepth:
            return self.startPos,intersection.pos
        min_length: float=Ray.minLength

        for barrier in barriers:
            intersectionsWithBarrier=barrier.getIntersections(self.startPos,self.startDir,tempSource)
            for i in intersectionsWithBarrier:
                if i.length<0.01:
                    continue
                elif i.length<min_length:
                    min_length=i.length
                    intersection=i
        if intersection.barrier and intersection.barrier.isCollectingImaginaryRays:
            for ray in intersection.getImaginaryRays():
                self.source.addImaginaryRay(ray)
        if len(intersection.wentDirs)==0:
            return self.startPos,intersection.pos
        if len(intersection.wentDirs)==1:
            return self.startPos,*Ray(intersection.pos,intersection.wentDirs[0],self.source).construct(barriers,depth+1,intersection)
        if len(intersection.wentDirs)>1:
            return self.startPos,[list(Ray(intersection.pos,wentDir,self.source).construct(barriers,depth+1,intersection)) for wentDir in intersection.wentDirs]
    def fullConstruct(self,barriers:List[Barrier]):
        self.construction=list(self.construct(barriers,0))

    def draw(self,win,color:Tuple[int,int,int]=(255,255,255)):
        self.drawPart(win,self.construction,color)

    def drawPart(self,win,construction:list,color:Tuple[int,int,int]=(255,255,255)):
        if type(construction[-1])==list:
            for i in range(1,len(construction)-1):
                draw.line(win,color,construction[i-1],construction[i],3)
            for i in range(len(construction[-1])):
                self.drawPart(win,[construction[-2]]+construction[-1][i],color)
        else:
            for i in range(1,len(construction)):
                draw.line(win,color,construction[i-1],construction[i],3)

class ImaginaryRay:
    strokeLength=8
    def __init__(self,pos:Vector2,direction:Vector2):
        self.direction=direction.normalize()
        self.pos:Vector2=pos
        self.strokeCount=600//ImaginaryRay.strokeLength

    def draw(self,win:Surface,color:Tuple[int,int,int]):
        print(self.strokeCount)
        for i in range(self.strokeCount):
            draw.line(win,color,self.pos+(2*i+1)*self.direction*ImaginaryRay.strokeLength,self.pos+self.direction*(2*i+2)*ImaginaryRay.strokeLength,2)


class Button:
    buttons:List[Button]=[]
    buttonPressed=False
    def __init__(self,pos:Vector2,size:Vector2,id:str,text:str,func,fontSize:int=16,funcArgs:List[any]=None,background:Tuple[int,int,int]=(50,50,50),backgroundImage:Surface=None):
        self.pos:Vector2=pos
        self.size:Vector2=size
        self.id:str=id
        self.text:str=text
        self.func=func
        self.funcArgs=funcArgs if funcArgs!=None else []
        self.background=background
        self.pressedBackround=(150,100,100)
        self.fontSize:int=fontSize
        self.rect:Rect=Rect(self.pos,self.size)
        self.isPressed:bool=False

        self.font=font.SysFont("Arial",self.fontSize)
        self.textRendered=self.font.render(self.text,False,(255,255,255))
        self.textRenderedRect=self.textRendered.get_rect(center=self.rect.center)

        self.backgroundImage = backgroundImage
        if backgroundImage:
            self.backgroundImageRect=self.backgroundImage.get_rect(center=self.rect.center)

        Button.buttons.append(self)

    def press(self):
        self.func(*self.funcArgs)
        self.isPressed=True

    @staticmethod
    def draw(win,currentButtons):
        for button in Button.buttons:
            if button.id in currentButtons:
                if button.backgroundImage:
                    win.blit(button.backgroundImage,button.backgroundImageRect)
                else:
                    draw.rect(win,button.pressedBackround if button.isPressed else button.background,button.rect,0,6)
                draw.rect(win, (255,0,0), button.rect,2,6)
                win.blit(button.textRendered,button.textRenderedRect)

    @staticmethod
    def pressButton(mPos:Vector2,mPress:Tuple[bool,bool,bool],currentButtons:List[str]):
        if mPress[0]:
            if not Button.buttonPressed:
                for button in Button.buttons:
                    if button.id in currentButtons:
                        if button.rect.collidepoint(mPos.x,mPos.y):
                            button.press()
                            Button.buttonPressed=True
        else:
            if Button.buttonPressed:
                Button.buttonPressed=False
                for button in Button.buttons:
                    button.isPressed=False

class CreateButton(Button):
    def __init__(self, pos: Vector2, size: Vector2, id: str,func,funcArgs: List[any],backgroundImage:Surface=None):
        super(CreateButton, self).__init__(pos,size,id,"",func,funcArgs=funcArgs,backgroundImage=backgroundImage)

    def press(self):
        super(CreateButton, self).press()
        funcArgs=[]
        for arg in self.funcArgs:
            try:
                funcArgs.append(arg.copy())
            except AttributeError:
                funcArgs.append(arg)
        self.funcArgs=funcArgs

class UI:
    def __init__(self,game:Game):
        self.game:Game=game
        Button(Vector2(self.game.WIDTH-70, 0), Vector2(70, 70), "quit", "QUIT", self.game.stop, 32)
        Button(Vector2(15, 15), Vector2(70, 70), "create", "+", self.createModeOn, 120)


        CreateButton(Vector2(0,0),Vector2(100,100),"lens+",self.createBarrier,[Lens,Vector2(100,500),Vector2(200,500),300,True],Lens.getIcoSurface(100))
        CreateButton(Vector2(101, 0), Vector2(100, 100), "lens-", self.createBarrier,[Lens, Vector2(100, 500), Vector2(200, 500), 300, False],Lens.getIcoSurface(100,False))

        Button(Vector2(100+101+15, 15), Vector2(70, 70), "unCreate", "~", self.createModeOff, 120)

        self.barrierButtonIds=["lens+","lens-"]

        self.currentButtons:List[str]=["quit","create"]
        self.events=[]
        self.rootSkeleton=Skeleton({},self)
        self.pointsMover=PointsMover([])
        self.mPos:Vector2=Vector2(mouse.get_pos())
        self.mPress: Tuple[bool,bool,bool]=mouse.get_pressed()

    def update(self):
        self.mPos = Vector2(mouse.get_pos())
        self.mPress = mouse.get_pressed(3)
        if self.pointsMover.movedPoint==None:
            Button.pressButton(self.mPos,self.mPress,self.currentButtons)

        self.pointsMover.setPoints(self.rootSkeleton.getPoints()[0])
        for e in event.get():
            if e.type == QUIT:
                self.game.stop()
            if e.type == KEYDOWN:
                if e.key == K_s:
                    self.game.save()
                if e.key == K_l:
                    self.game.load()
        if not Button.buttonPressed:
            self.pointsMover.move(self.mPos,self.mPress)

    def draw(self,win):
        self.rootSkeleton.draw(win)
        Button.draw(win,self.currentButtons)

    def createModeOn(self):
        self.currentButtons=["quit","unCreate"]+self.barrierButtonIds

    def createModeOff(self):
        self.currentButtons=["quit","create"]

    def createBarrier(self,barrierType:type,*args):
        newBar=barrierType(*list(args))
        print(1)
        self.rootSkeleton.addDependent(newBar.skeleton)
        self.createModeOff()

    def connectSkeletons(self):
        for barrier in Barrier.barriers:
            self.rootSkeleton.addDependent(barrier.skeleton)
        for source in Source.sources:
            self.rootSkeleton.addDependent(source.skeleton)

class Game:
    def __init__(self):
        self.WIDTH: int = 1080
        self.HEIGHT: int = 640
        self.FPS: int = 60
        self.isRunning: bool = True

        self.win: Surface = display.set_mode((self.WIDTH, self.HEIGHT),RESIZABLE)
        self.clock: time.Clock = time.Clock()


        self.mir=FlatRefractingSurface(Vector2(785,300),Vector2(800,100),3/2,1)
        self.screen=FlatMirror(Vector2(150,30),Vector2(103, 237),True)
        self.spherical=SphericalRefractingSurfaceReal(Vector2(100,100),Vector2(200,100),500,1,3/2)
        self.refr=FlatRefractingSurface(Vector2(800,200),Vector2(900,150),3/2,1)

        self.lens = Lens(Vector2(750, 250), Vector2(800, 250), 300, False)
        self.lens=Lens(Vector2(600,250),Vector2(700,250),300,True)
        self.source=Source(Vector2(200,450),(255,0,0))
        self.source.addRay(Vector2(3, -0.5))
        self.source.addRay(Vector2(3, 0))
        self.source.addRay(Vector2(3, 0.5))
        self.source=Source(Vector2(200,425),(255,255,0))
        self.source.addRay(Vector2(3, -0.5))
        self.source.addRay(Vector2(3, 0))
        self.source.addRay(Vector2(3, 0.5))
        self.UI=UI(self)
        self.UI.connectSkeletons()

    def UpdateStuff(self):
        self.UI.update()
        for barrier in Barrier.barriers:
            barrier.build()
        for source in Source.sources:
            source.fullConstruct(Barrier.barriers)

    def DrawStuff(self):
        for source in Source.sources:
            source.draw(self.win)
        for barrier in Barrier.barriers:
            barrier.draw(self.win)
        self.UI.draw(self.win)

    def WindowUpdateStuff(self):

        self.UpdateStuff()
        self.win.fill((0, 0, 0))
        self.DrawStuff()
        display.update()
        self.clock.tick(self.FPS)
        display.set_caption(str(round(self.clock.get_fps())))

    def save(self):
        objs=Barrier.barriers+Source.sources
        f=open("ducks","wb+")
        f.write(dumps([[obj.__class__,*obj.getInitData()] for obj in objs]))
        f.close()

    def load(self):
        try:
            f=open("ducks","rb")
            objs=loads(f.read())
            f.close()
            Barrier.barriers.clear()
            Source.sources.clear()
            self.pointsMover.points.clear()
            Skeleton.skeletons.clear()
            for obj in objs:
                obj[0](*obj[1:])

        except FileNotFoundError:
            f=open("ducks","w+")
            f.close()
            print("file empty")
        except EOFError:
            print("file empty or corrupted")

    def run(self):
        while self.isRunning:
            self.WindowUpdateStuff()

    def stop(self):
        self.isRunning = False


game = Game()
game.run()
quit()
