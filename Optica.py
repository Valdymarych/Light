from typing import Tuple,List,Union,Dict
from pygame import *

class PointsMover:
    def __init__(self,points:List[Vector2]):
        self.points=points
        self.movePoint:Vector2=None

    def move(self,mpos:Vector2,mpess:Tuple[bool,bool,bool]):
        if mpess[0]:
            if not self.movePoint:
                minDistance: float = 30 ** 2 + 1
                self.movePoint = None
                for point in self.points:
                    distance = (point - mpos).magnitude_squared()
                    if distance < minDistance:
                        minDistance = distance
                        self.movePoint = point
            if self.movePoint:
                self.movePoint.xy = mpos.xy
        else:
            self.movePoint=None

class Skeleton:
    skeletons=[]
    points=[]
    def __init__(self,points: Dict[str,Vector2]):
        self.points=points
        Skeleton.points.extend(self.points.values())
        Skeleton.skeletons.append(self)

    def __getattr__(self, item:str):
        return self.points.get(item)

    def __setattr__(self, key:str, value:any):
        if key=="points":
            super().__setattr__(key, value)
        else:
            if key in self.points.keys():
                raise UserWarning("setter error")
            else:
                super().__setattr__(key, value)

    def draw(self,win:Surface):
        for point in self.points.values():
            draw.circle(win,(255,255,0),point.xy,10)

class Intersection:
    def __init__(self,pos: Vector2,cameDir: Vector2,wentDirs: List[Vector2],barrier,length:float):
        self.pos: Vector2=pos
        self.cameDir: Vector2=cameDir
        self.wentDirs: List[Vector2]=wentDirs
        self.length: float=length
        self.barrier=barrier

class Barrier:
    barriers=[]
    def __init__(self):
        Barrier.barriers.append(self)
        self.skeleton:Skeleton=Skeleton({})

    def build(self):  # sceleton -> points -> other
        pass

    def getIntersections(self,startPos:Vector2,startDir:Vector2,source:any)-> List[Intersection]:
        pass

    def draw(self,win:Surface):
        pass

class FlatBarrier(Barrier):
    def __init__(self,start: Vector2,end: Vector2):
        super(FlatBarrier, self).__init__()
        self.start=start
        self.end=end
        self.along:Vector2=Vector2(0,0)
        self.length:float=0
        self.normal:Vector2=Vector2(0,0)
        self.alongNormal:Vector2=Vector2(0,0)
        self.skeleton:Skeleton=Skeleton({"start":self.start,"end":self.end})
        self.build()



    def build(self):
        self.along: Vector2 = self.end - self.start
        self.length: float = self.along.magnitude()
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

class FlatMirror(FlatBarrier):
    strokeStep=20
    stroke=Vector2(10,10)
    def __init__(self,start: Vector2,end: Vector2):
        super(FlatMirror, self).__init__(start,end)

    def build(self):
        super(FlatMirror, self).build()
        self.strokeCount=int(self.length/FlatMirror.strokeStep)
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

class FlatRefractingSurface(FlatBarrier):
    def __init__(self,start: Vector2,end: Vector2,n0:float,n:float):
        super(FlatRefractingSurface, self).__init__(start,end)
        self.n0:float=n0
        self.n:float=n
    def getAngle(self,intersection:Intersection) ->List[Intersection]:
        x = self.alongNormal.dot(intersection.cameDir)
        direction = float(self.along.cross(intersection.cameDir))
        n = self.n / self.n0
        if direction < 0:
            n = self.n0 / self.n

        if n * x>1:  # sin B > 1
            nextDir=self.alongNormal*x/abs(x)
        else:
            y = n * x * ((1 - x ** 2) / (1 - (x*n) ** 2)) ** 0.5
            nextDir = intersection.cameDir - self.alongNormal * (x - y)
            nextDir.normalize()
        nextDir2 = intersection.cameDir - 2 * self.normal * self.normal.dot(intersection.cameDir)
        return [Intersection(intersection.pos, intersection.cameDir, [nextDir, nextDir2], intersection.barrier, intersection.length)]
    def draw(self,win):
        draw.line(win,(255,255,255),self.start,self.end)

class FlatScreen(FlatBarrier):
    def __init__(self,start:Vector2,end:Vector2):
        super(FlatScreen, self).__init__(start,end)

    def getAngle(self,intersection:Intersection) ->List[Intersection]:
        return [Intersection(intersection.pos,intersection.cameDir,[],intersection.barrier,intersection.length)]

    def draw(self,win:Surface):
        draw.line(win,(255,255,255),self.start,self.end)

class Ray:
    def __init__(self, pos: Vector2, direction: Vector2):
        self.startPos: Vector2 = pos
        self.startDir: Vector2 = direction/direction.length()
        self.construction:List[Union[Tuple,Vector2]]=[Vector2(0,0)]

    def construct(self,barriers:List[Barrier],source:Intersection=None):
        intersection: Intersection=Intersection(self.startPos+self.startDir*32000,self.startDir,[],source,32000)
        min_length: float=64000
        for barrier in barriers:
            intersectionsWithBarrier=barrier.getIntersections(self.startPos,self.startDir,source)
            for i in intersectionsWithBarrier:
                if i.length<0.01:
                    continue
                elif i.length<min_length:
                    min_length=i.length
                    intersection=i
        if len(intersection.wentDirs)==0:
            return self.startPos,intersection.pos
        if len(intersection.wentDirs)==1:
            return self.startPos,*Ray(intersection.pos,intersection.wentDirs[0]).construct(barriers,intersection)
        if len(intersection.wentDirs)>1:
            return self.startPos,[list(Ray(intersection.pos,wentDir).construct(barriers,intersection)) for wentDir in intersection.wentDirs]
    def fullConstruct(self,barriers:List[Barrier]):
        self.construction=list(self.construct(barriers))

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

class Source:
    def __init__(self,pos:Vector2,color:Tuple[int,int,int]=(255,255,255)):
        self.pos:Vector2=pos
        self.rays:List[Ray]=[]
        self.color:Tuple[int,int,int]=color

    def addRay(self,dir):
        self.rays.append(Ray(self.pos,dir))

    def fullConstruct(self,barriers):
        for ray in self.rays:
            ray.fullConstruct(barriers)

    def draw(self,win):
        for ray in self.rays:
            ray.draw(win,self.color)

class Game:
    def __init__(self):
        self.WIDTH: int = 1200
        self.HEIGHT: int = 500
        self.FPS: int = 40
        self.isRunning: bool = True

        self.win: Surface = display.set_mode((self.WIDTH, self.HEIGHT))
        self.clock: time.Clock = time.Clock()

        self.mPos: Vector2 = Vector2(mouse.get_pos())
        self.mPress: Tuple[bool,bool,bool]=mouse.get_pressed()

        self.mir=FlatRefractingSurface(Vector2(785,300),Vector2(800,100),3/2,1)
        self.screen=FlatMirror(Vector2(150,30),Vector2(103, 237))
        self.source=Source(Vector2(200,200))
        self.source.addRay(Vector2(3,0))
        self.source.fullConstruct(Barrier.barriers)
        self.pointsMover=PointsMover(Skeleton.points)

    def UpdateStuff(self):
        self.mPos = Vector2(mouse.get_pos())
        self.mPress = mouse.get_pressed(3)
        self.pointsMover.move(self.mPos,self.mPress)
        self.mir.build()
        self.screen.build()
        self.source.fullConstruct(Barrier.barriers)


        for e in event.get():
            if e.type == QUIT:
                self.stop()

    def DrawStuff(self):
        self.source.draw(self.win)
        for barrier in Barrier.barriers:
            barrier.draw(self.win)
        for skeleton in Skeleton.skeletons:
            skeleton.draw(self.win)

    def WindowUpdateStuff(self):
        self.UpdateStuff()
        self.win.fill((0, 0, 0))
        self.DrawStuff()
        display.update()
        self.clock.tick(self.FPS)
        display.set_caption(str(round(self.clock.get_fps())))

    def run(self):
        while self.isRunning:
            self.WindowUpdateStuff()

    def stop(self):
        self.isRunning = False


game = Game()
game.run()
quit()
