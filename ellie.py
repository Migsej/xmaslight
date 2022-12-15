import board
import neopixel
import asyncio
import numpy

pixels = neopixel.NeoPixel(board.D18, 50)

stepduration = 0.05

pixels.fill((0, 0, 0))

class LedAgent:
    def __init__(self, index):
        self.index = index
        self.current = numpy.zeros(3)
        self._push_current()
        self.eof = False
        self.q = asyncio.Queue()

    def put_task(self, task):
        self.q.put_nowait(task)

    def put_eof(self):
        self.eof = True
        
    def _push_current(self):
        # order seems to be swapped
        pixels[self.index] = (self.current[1], self.current[0], self.current[2])
#        print(f"{self.index}\t{pixels[self.index]}")
        
    async def run(self):
        while not self.eof or not self.q.empty():
            task = await self.q.get()
            await task(self)
            self.q.task_done()

    async def sleep(self, nsteps):
#        print(f"{self.index}: sleep({nsteps})")
        await asyncio.sleep(stepduration * nsteps)
        
    async def set_color(self, destcolor):
#        print(f"{self.index}: self_color({destcolor})")
        self.current = destcolor
        self._push_current()
        
    async def lin_slope(self, nsteps, destcolor):
#        print(f"{self.index}: lin_slope({nsteps}, {destcolor})")
        if nsteps <= 0:
            self.current = destcolor
            self._push_current()
            return
                   
        srccolor = self.current
        distvec = destcolor - srccolor
        for step in range(0, nsteps):
            await asyncio.sleep(stepduration)
            self.current = ((step + 1) / nsteps) * distvec + srccolor
            self._push_current()

agents = [ LedAgent(i) for i in range(0, 50) ]

def finish_all():
    for ag in agents:
        ag.put_eof()

rainbow = [
    numpy.array([148, 0, 211]),
    numpy.array([75, 0, 130]),
    numpy.array([0, 0, 255]),
    numpy.array([0, 255, 0]),
    numpy.array([255, 255, 0]),
    numpy.array([255, 127, 0]),
    numpy.array([255, 0 , 0])
]
                   
async def animation():
    for round in range(0, 100):
        color = rainbow[round % len(rainbow)]
        for i in range(0, 50):
            ag40 = agents[49-i]
            delay=i*20 + (100 if round > 0 else 0)
            ag40.put_task(lambda ag, delay=delay : ag.sleep(delay))
            ag40.put_task(lambda ag : ag.set_color(numpy.array([0,0,0])))
            ag40.put_task(lambda ag, color=color : ag.lin_slope(30, color))
#            ag40.put_task(lambda ag : ag.sleep(20))
            ag40.put_task(lambda ag : ag.lin_slope(30, numpy.array([0,0,0])))
    finish_all()
                   
async def main():
    tasks = [ asyncio.create_task(agent.run()) for agent in agents ]
    await animation()
    await asyncio.gather(*tasks)
   
asyncio.run(main())
