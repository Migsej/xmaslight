import board
import neopixel
import asyncio
import itertools
import random

# switch off auto_write
pixels = neopixel.NeoPixel(board.D18, 50,
                           pixel_order=neopixel.RGB)

rgb = [
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255)
    ]

for i in range(0, 50):
    pixels[i] = rgb[i % 3]
    
