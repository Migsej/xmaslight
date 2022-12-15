import board
import neopixel
import asyncio
import itertools
import masterclock 
import ledagent

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

async def snake_down(color):
    print(f"snake: {color}")
    for i in range(0, 50):
        ag = agents[49-i]
        ag.put_trapeze(color, (0,0,0), 20, 0, 60)
        await mclock.delay(15)

async def animation(color_scheme):
    snake_delay =0
    tasks = [ ]
    for round in range(1000):
        for color in color_scheme:
            while len(tasks) > len(color_scheme):
                await asyncio.wait([tasks[0]])
                del tasks[0]
            tasks.append(asyncio.create_task(snake_down(color)))
            await mclock.delay(400)
    # wait for remaining snakes.
    asyncio.wait(tasks)
    finish_all()

async def main():
    clock_task = asyncio.create_task(mclock.run())
    await animation(rainbow)
    await clock_task
   
asyncio.run(main())

