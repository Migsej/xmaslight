import coords
import time
import neopixel
import board


pixels = neopixel.NeoPixel(board.D18, 50)

pixels.fill(0,0,0)

coordinates = [(x,coords.coords[x][0], coords.coords[x][1]) for x in range(len(coords.coords))]

def sorting(e):
    return e[2]
coordinates.sort(key=sorting)

print(coordinates)

for pixel in coordinates:
    pixels[pixel[0]] = (100,0,0)
    time.sleep(0.5)
