import board
import neopixel
import asyncio
import itertools
import time

# switch off auto_write
pixels = neopixel.NeoPixel(board.D18, 50,
                           pixel_order=neopixel.RGB,
                           auto_write=False)

stepduration = 0.02

print("reset")
pixels.fill((0, 0, 0))
pixels.show()
clock = 0

COLOR_INACTIVE=(-1,-1,-1)

def do_lin_slope(srccolor, dstcolor, nsteps):
    distred = dstcolor[0] - srccolor[0]
    distgreen = dstcolor[1] - srccolor[1]
    distblue = dstcolor[2] - srccolor[2]
    for step in range(nsteps):
        factor = ((step+1)/nsteps)
        yield  (factor * distred + srccolor[0],
                factor * distgreen + srccolor[1],
                factor * distblue + srccolor[2])

def do_delay(nsteps):
    return itertools.repeat(COLOR_INACTIVE, nsteps)

def do_trapeze(startcolor, upcolor, endcolor, slopeup_steps, up_steps, slopedown_steps):
    return itertools.chain(
        do_lin_slope(startcolor, upcolor, slopeup_steps),
        do_delay(up_steps),
        do_lin_slope(upcolor, endcolor, slopedown_steps))

class LedAgent:
    def __init__(self, index):
        self.index = index
        self.current = (0,0,0)
        self.eof = False
        self.tasks = []
        self.active_iterator = None

    def set_clock(self, clock):
#        print(f"{self.index}: set_clock({clock})")
        index = 0
        while True:
            if self.active_iterator == None:
                if len(self.tasks) == 0:
                    return False
                self.active_iterator = iter(self.tasks.pop(0))
            try:
                color = next(self.active_iterator)
                if color != COLOR_INACTIVE and color != self.current:
                    self.current =  (int(color[0]), int(color[1]), int(color[2]))
  #                  print(f"{self.index}: {self.current}")
                    pixels[self.index] = self.current
                    return True
            except StopIteration:
                self.active_iterator = None

    def is_finished(self):
        return self.active_iterator == None and len(self.tasks) == 0 and self.eof
    
    def put_eof(self):
        print(f"{self.index}: eof")
        self.eof = True
        
    def put_lin_slope(self, dstcolor, nsteps):
 #       print(f"{self.index}: put_lin_slope")
        self.tasks.append(do_lin_slope(self.current, dstcolor, nsteps))

    def put_delay(self, nsteps):
#        print(f"{self.index}: put_delay")
        self.tasks.append(do_delay(nsteps))

    def put_trapeze(self, upcolor, endcolor, slopeup_steps, up_steps, slopedown_steps):
#        print(f"{self.index}: put_trapeze {upcolor}")
        self.tasks.append(do_trapeze(self.current, upcolor, endcolor, slopeup_steps, up_steps, slopedown_steps))

def finish_all():
    for ag in agents:
        ag.put_eof()

agents = [ LedAgent(i) for i in range(0, 50) ]

# elements are (clock, fut)
waiterfuts = []

# runs "forever
async def master_clock():
    global clock
    all_finished = False
    while not all_finished:
        # wake up waiters:
        do_yield = False
        for i in range(len(waiterfuts) - 1, -1, -1):
            waiter = waiterfuts[i]
            if waiter[0] <= clock:
                do_yield = True
                waiter[1].set_result(clock)
                del waiterfuts[i]
        if do_yield:
            await asyncio.sleep(0)
            
#        print(f"master tick {clock}")
        all_finished = True
        updated = False
        for ag in agents:
            if ag.set_clock(clock):
                updated = True
            if not ag.is_finished():
                all_finished = False
        if updated:
            pixels.show()
        clock += 1
        await asyncio.sleep(stepduration)
    print("master clock finished")

def step_delay(steps):
    fut = asyncio.get_running_loop().create_future()
    waiterfuts.append((clock + steps, fut))
    return fut

rgb = [
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255)
    ]

rainbow = [
    (148, 0, 211),
    (75, 0, 130),
    (0, 0, 255),
    (0, 255, 0),
    (255, 255, 0),
    (255, 127, 0),
    (255, 0 , 0)
]

async def snake_down(color):
    print(f"snake: {color}")
    for i in range(0, 50):
        ag = agents[49-i]
        ag.put_trapeze(color, (0,0,0), 20, 0, 60)
        await step_delay(15)
    
async def animation():
    print("animation")
    snake_delay =0
    tasks = [ ]
    for round in range(1000):
        for color in rainbow:
            while len(tasks) > len(rainbow):
                await asyncio.wait([tasks[0]])
                del tasks[0]
            tasks.append(asyncio.create_task(snake_down(color)))
            await step_delay(400)

    asyncio.wait(tasks)
    finish_all()
                   
async def main():
    clock_task = asyncio.create_task(master_clock())
    await animation()
    await clock_task
   
asyncio.run(main())

# got this from adafruit
def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b) if ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)
