import board
import time
import neopixel

pixels = neopixel.NeoPixel(board.D18, 50)

for i in range(0,50):
    pixels.fill((0,0,0))
    pixels[i] = ((255,255,255))
    time.sleep(5)
