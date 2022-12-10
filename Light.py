from pygame import *
init()

class Game:
    def __init__(self):
        self.WIDTH=1200
        self.HEIGHT=600
        self.FPS=60
        self.isRunning=True

        self.win=display.set_mode((self.WIDTH,self.HEIGHT))
        self.clock=time.Clock()

    def UpdateStuff(self):
        for e in event.get():
            if e.type==QUIT:
                self.stop()


    def DrawStuff(self):
        pass

    def WindowUpdateStuff(self):
        self.UpdateStuff()
        self.win.fill((0,0,0))
        self.DrawStuff()
        display.update()
        self.clock.tick(self.FPS)
        display.set_caption(str(round(self.clock.get_fps())))

    def run(self):
        while self.isRunning:
            self.WindowUpdateStuff()

    def stop(self):
        self.isRunning=False

game=Game()
game.run()
quit()
