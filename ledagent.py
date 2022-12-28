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

def do_constant(color, nsteps):
    for step in range(nsteps):
        yield color
        
def do_delay(nsteps):
    return itertools.repeat(COLOR_INACTIVE, nsteps)

def do_trapeze(startcolor, upcolor, endcolor, slopeup_steps, up_steps, slopedown_steps):
    return itertools.chain(
        do_lin_slope(startcolor, upcolor, slopeup_steps),
        do_constant(upcolor, up_steps),
        do_lin_slope(upcolor, endcolor, slopedown_steps))

class LedAgent:
    def __init__(self, mclock, pixels, index):
        self.pixels = pixels
        self.index = index
        self.current = (0,0,0)
        self.eof = False
        # list of active iterators
        self.tasks = []
        self.mclock = mclock
        mclock.add_ticker(self)

    def tok(self, clock):
        # we take the mean of all the active tasks
        color = (0,0,0)
        ncolors = 0
        # reverse we can delete takss without upsetting the iterator
        #print("tok {self.index}")
        for i in range(len(self.tasks) - 1, -1, -1):
            t = self.tasks[i]
            try:
                tmp = next(t)
                color = (color[0] + tmp[0], color[1] + tmp[1], color[2] + tmp[2])
                ncolors += 1
            except StopIteration:
                del self.tasks[i]
        if ncolors == 0:
            if self.eof:                
                self.mclock.remove_ticker(self)
            return False            
        elif ncolors > 1:
            color = (color[0] / ncolors, color[1] / ncolors, color[2] / ncolors)
        # nothing to do
        if color == self.current:
            return False
        self.current =  color
        intcolor = int(color[0]), int(color[1]), int(color[2])
        #print(f"{self.index}: {intcolor}")
        self.pixels[self.index] = intcolor
        return True
        
    def put_eof(self):
        #print(f"{self.index}: eof")
        self.eof = True
        
    def put_lin_slope(self, dstcolor, nsteps):
        #print(f"{self.index}: put_lin_slope")
        self.tasks.append(iter(do_lin_slope(self.current, dstcolor, nsteps)))

    def put_delay(self, nsteps):
        #print(f"{self.index}: put_delay")
        self.tasks.append(iter(do_delay(nsteps)))

    def put_trapeze(self, upcolor, endcolor, slopeup_steps, up_steps, slopedown_steps):
        #print(f"{self.index}: put_trapeze {upcolor}")
        self.tasks.append(iter(do_trapeze(self.current, upcolor, endcolor, slopeup_steps, up_steps, slopedown_steps)))

