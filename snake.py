import board
import neopixel
import asyncio
import itertools
import masterclock 
import ledagent
import random

# switch off auto_write
pixels = neopixel.NeoPixel(board.D18, 50,
                           pixel_order=neopixel.RGB,
                           auto_write=False)
pixels.fill((0, 0, 0))
pixels.show()


mclock = masterclock.MasterClock(0.02)
def tick_cb(updated):
    if updated:
        pixels.show()
mclock.set_tick_cb(tick_cb)

agents = [ ledagent.LedAgent(mclock, pixels, i) for i in range(0, 50) ]

def finish_all():
    for ag in agents:
        ag.put_eof()

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

async def snake(color, updir, speed = 1.0):
    print(f"snake: {color} {speed}")
    for i in range(0, 50):
        ag = agents[i if updir else 49-i]
        ag.put_trapeze(color, (0,0,0), int(20 * speed), 0, int(60 * speed))
        await mclock.delay(int(15 * speed))

async def color_snake(color_scheme, updir, speed = 1.0):
    print(f"color_snake {speed}")
    icolor = 0
    for i in range(0, 50):
        ag = agents[i if updir else 49-i]
        ag.put_trapeze(color_scheme[icolor % len(color_scheme)], (0,0,0), int(20 * speed), 0, int(60 * speed))
        icolor += 1
        await mclock.delay(int(15 * speed))
        
async def animation(color_scheme, speed = 1.0):
    snake_delay =0
    tasks = [ ]
    for round in range(1000):
        for color in color_scheme:
            while len(tasks) > len(color_scheme):
                await asyncio.wait([tasks[0]])
                del tasks[0]
            tasks.append(asyncio.create_task(snake(color, False, speed)))
            await mclock.delay(300)
    # wait for remaining snakes.
    asyncio.wait(tasks)
    finish_all()

async def wild_snake():
    for round in range(1000):
        await mclock.delay(100)
        await color_snake(rainbow, True, 0.3)
        
async def main():
    await asyncio.gather(mclock.run(), animation(rainbow), animation(rainbow,  2), wild_snake())
   
asyncio.run(main())
