from typing import Tuple,List,Union,Dict

from pygame import *

class Skeleton:
    def __init__(self,points: Dict[str,Vector2]):
        self.points=points

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


class Intersection:
    def __init__(self,pos: Vector2,cameDir: Vector2,wentDirs: List[Vector2],length):
        self.pos: Vector2=pos
        self.cameDir: Vector2=cameDir
        self.wentDirs: List[Vector2]=wentDirs
        self.length: float=length

class Barrier:
    barriers=[]
    def __init__(self):
        Barrier.barriers.append(self)
        self.skeleton:Skeleton=Skeleton({})

    def build(self):  # sceleton -> points -> other
        pass

    def getIntersections(self,startPos:Vector2,startDir:Vector2)-> List[Intersection]:
        pass

class Mirror(Barrier):
    def __init__(self,start: Vector2,end: Vector2,isBilateral:bool=False):
        super(Mirror, self).__init__()
        self.start=start
        self.end=end
        self.isBilateral=isBilateral
        self.skeleton:Skeleton=Skeleton({"start":self.start,"end":self.end})
        self.build()

    def build(self):
        self.along:Vector2=self.end-self.start
        self.length:float=self.along.magnitude()
        self.normal:Vector2=Vector2(-self.along.y,self.along.x)/self.length
        self.alongNormal:Vector2=self.along.normalize()

    def getIntersections(self, startPos: Vector2, startDir: Vector2) -> List[Intersection]:
        x1,y1=self.start.xy
        dx1,dy1=self.along.xy
        x2,y2=startPos.xy
        dx2,dy2=(startDir*32000).xy


        if dy1*dx2!=dx1*dy2:
            s=(y2*dx2-y1*dx2+x1*dy2-x2*dy2)/(dy1*dx2-dx1*dy2)
            if abs(dx2)>abs(dy2):
                t=(x1-x2+s*dx1)/dx2
            else:
                t=(y1-y2+s*dy1)/dy2
            if 0<s<1 and 0<t<1:
                exist=float(self.along.cross(startDir))
                if exist>0 or self.isBilateral:
                    nextDir=startDir-2*self.normal*self.normal.dot(startDir)
                    return [Intersection(self.start+self.along*s,startDir,[nextDir],32000*t)]

                return [Intersection(self.start+self.along*s,startDir,[],32000*t)]
        return []
    def draw(self,win):
        draw.line(win,(255,255,255),self.start,self.end)

class Ray:
    def __init__(self, pos: Vector2, direction: Vector2):
        self.startPos: Vector2 = pos
        self.startDir: Vector2 = direction/direction.length()
        self.construction:List[Union[Tuple,Vector2]]=[Vector2(0,0)]

    def construct(self,barriers:List[Barrier]):
        intersection: Intersection=Intersection(self.startPos+self.startDir*32000,self.startDir,[],32000)
        min_length: float=64000
        for barrier in barriers:
            intersectionsWithBarrier=barrier.getIntersections(self.startPos,self.startDir)
            for i in intersectionsWithBarrier:
                if i.length<0.01:
                    continue
                elif i.length<min_length:
                    min_length=i.length
                    intersection=i
        if len(intersection.wentDirs)==0:
            return self.startPos,intersection.pos
        if len(intersection.wentDirs)==1:
            return self.startPos,*Ray(intersection.pos,intersection.wentDirs[0]).construct(barriers)
        if len(intersection.wentDirs)>1:
            return self.startPos,[list(Ray(intersection.pos,wentDir).construct(barriers)) for wentDir in intersection.wentDirs]
    def fullConstruct(self,barriers:List[Barrier]):
        self.construction=list(self.construct(barriers))

    def draw(self,win):
        self.drawPart(win,self.construction)

    def drawPart(self,win,construction:list):
        if type(construction[-1])==list:
            for i in range(1,len(construction)-1):
                draw.line(win,(255,255,255),construction[i-1],construction[i])
            for i in range(len(construction[-1])):
                self.drawPart(win,[self.construction[-2]].extend(construction[-1][0]))
        else:
            for i in range(1,len(construction)):
                draw.line(win,(255,255,255),construction[i-1],construction[i])


class Game:
    def __init__(self):
        self.WIDTH: int = 1200
        self.HEIGHT: int = 600
        self.FPS: int = 40
        self.isRunning: bool = True

        self.win: Surface = display.set_mode((self.WIDTH, self.HEIGHT))
        self.clock: time.Clock = time.Clock()

        self.mPos: Vector2 = Vector2(mouse.get_pos())
        self.mPress: Tuple[bool,bool,bool]=mouse.get_pressed()

        self.mir=Mirror(Vector2(600,300),Vector2(800,100))

        self.ray0 = Ray(Vector2(200, 200), Vector2(3,0))
        self.ray0.fullConstruct(Barrier.barriers)

    def UpdateStuff(self):
        self.mPos = Vector2(mouse.get_pos())
        self.mPress = mouse.get_pressed()
        self.mir.skeleton.start.xy=self.mPos.xy
        self.mir.build()
        self.ray0.fullConstruct(Barrier.barriers)

        for e in event.get():
            if e.type == QUIT:
                self.stop()

    def DrawStuff(self):
        self.ray0.draw(self.win)
        for barrier in Barrier.barriers:
            barrier.draw(self.win)

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
