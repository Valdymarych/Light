from typing import Tuple,List,Union

from pygame import *

class Intersection:
    def __init__(self,pos: Vector2,cameDir: Vector2,wentDir: Vector2,length):
        self.pos: Vector2=pos
        self.cameDir: Vector2=cameDir
        self.wentDir: Vector2=wentDir
        self.length: float=length

class Barrier:
    barriers=[]
    def __init__(self):
        Barrier.barriers.append(self)

    def build(self):
        pass

    def getIntersections(self,startPos:Vector2,startDir:Vector2)-> List[Intersection]:
        pass

class Mirror(Barrier):
    def __init__(self,start: Vector2,end: Vector2,isBilateral:bool=False):
        super(Mirror, self).__init__()
        self.start=start
        self.end=end
        self.isBilateral=isBilateral

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
                    return [Intersection(self.start+self.along*s,startDir,nextDir,32000*t)]

                return [Intersection(self.start+self.along*s,startDir,Vector2(0,0),32000*t)]

        return []
    def draw(self,win):
        draw.line(win,(255,255,255),self.start,self.end)

class Ray:
    def __init__(self, pos: Vector2, direction: Vector2):
        self.startPos: Vector2 = pos
        self.startDir: Vector2 = direction/direction.length()
        self.construction:List[Union[Tuple,Vector2]]=[Vector2(0,0)]

    def construct(self,barriers:List[Barrier]):
        intersections: List[Intersection]=[]
        min_length: float=64000
        for barrier in barriers:
            intersectionsWithBarrier=barrier.getIntersections(self.startPos,self.startDir)
            for i in intersectionsWithBarrier:
                if i.length<0.01:
                    continue
                elif i.length<min_length:
                    min_length=i.length
                    intersections=[i]
                elif i.length==min_length:
                    intersections.append(i)
        if len(intersections)==0:
            return self.startPos,self.startPos+self.startDir*64000
        if len(intersections)==1:
            if intersections[0].wentDir.magnitude()==0:
                return self.startPos,intersections[0].pos
            return self.startPos,*Ray(intersections[0].pos,intersections[0].wentDir).construct(barriers)
        if len(intersections)>1:
            return self.startPos,[list(Ray(i.pos,i.wentDir).construct(barriers)) for i in intersections]
    def fullConstruct(self,barriers:List[Barrier]):
        self.construction=list(self.construct(barriers))

    def draw(self,win):
        self.drawPart(win,self.construction)

    def drawPart(self,win,construction):
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
        self.FPS: int = 60
        self.isRunning: bool = True

        self.win: Surface = display.set_mode((self.WIDTH, self.HEIGHT))
        self.clock: time.Clock = time.Clock()

        self.mPos: Vector2 = Vector2(mouse.get_pos())
        self.mPress: Tuple[bool,bool,bool]=mouse.get_pressed()

        self.mir=Mirror(Vector2(400,500),Vector2(800,100))

        self.ray0 = Ray(Vector2(200, 200), Vector2(3,0))
        self.ray0.fullConstruct(Barrier.barriers)

    def UpdateStuff(self):
        self.mPos = Vector2(mouse.get_pos())
        self.mPress = mouse.get_pressed()
        self.mir.start=self.mPos
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
