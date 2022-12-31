import coords
import neopixel
import board



pixels = neopixel.NeoPixel(board.D18, 50)

pixels.fill(0,0,0)

coordinates = [(x,coords.coords[x][0], coords.coords[x][1]) for x in range(len(coords.coords))]

def sorting(e):
    return e[1]
coordinates.sort(key=sorting)

columns = 5
columnlength = coordinates[-1][1] - coordinates[0][1] / columns

for i in range(columns):
    for j in coordinates:
        if j[1] < i + columnlength:
            pixels[j[0]] = (100,0,0)

    pixels.fill(0,0,0)





