import board
import neopixel

pixels = neopixel.NeoPixel(board.D18, 50)

pixels.fill((0,0,0))
pixellist = []
for pixel in range(50):
    pixels[pixel] = (100, 100, 100)
    action = input('2 to add to the current row. 1 to add a new row: ')
    if action == '1':
        pixellist.append([])
        pixellist[-1].append(pixel)
    elif action == '2':
        pixellist[-1].append(pixel)
    pixels[pixel] = (0, 0, 0)
print(pixellist)
with open('ledcoords.py', 'w') as f:
    f.write(f'coords = {pixellist}')
