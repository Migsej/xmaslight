import board, neopixel, time, random

pixels = neopixel.NeoPixel(board.D18, 50)
while True:
    
    for i in range(50):
        pixels[i] = (random.randrange(255),random.randrange(255),random.randrange(255))
    time.sleep(1)
