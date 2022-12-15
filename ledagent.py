import neopixel
import asyncio
import itertools
import masterclock

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
    def __init__(self, mclock, pixels, index):
        self.pixels = pixels
        self.index = index
        self.current = (0,0,0)
        self.eof = False
        self.tasks = []
        self.active_iterator = None
        self.mclock = mclock
        mclock.add_ticker(self)

    def tok(self, clock):
        #print(f"{self.index}: set_clock({clock})")
        while self.active_iterator != None or len(self.tasks) > 0:
            if self.active_iterator == None:
                self.active_iterator = iter(self.tasks.pop(0))
            try:
                color = next(self.active_iterator)
                if color != COLOR_INACTIVE and color != self.current:
                    self.current =  (int(color[0]), int(color[1]), int(color[2]))
                    #print(f"{self.index}: {self.current}")
                    self.pixels[self.index] = self.current
                    return True
            except StopIteration:
                self.active_iterator = None
        if self.eof:                
            self.mclock.remove_ticker(self)
        return False
        
    def put_eof(self):
        #print(f"{self.index}: eof")
        self.eof = True
        
    def put_lin_slope(self, dstcolor, nsteps):
        #print(f"{self.index}: put_lin_slope")
        self.tasks.append(do_lin_slope(self.current, dstcolor, nsteps))

    def put_delay(self, nsteps):
        #print(f"{self.index}: put_delay")
        self.tasks.append(do_delay(nsteps))

    def put_trapeze(self, upcolor, endcolor, slopeup_steps, up_steps, slopedown_steps):
        #print(f"{self.index}: put_trapeze {upcolor}")
        self.tasks.append(do_trapeze(self.current, upcolor, endcolor, slopeup_steps, up_steps, slopedown_steps))

