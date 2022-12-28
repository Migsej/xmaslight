import pygame
from pygame.locals import *

pygame.init()
x =600
y = 600

screen = pygame.display.set_mode((x, y), RESIZABLE)

image = pygame.image.load('tree2.jpg').convert()

screen.blit(image, (0,0))

pygame.transform.scale(screen, (x,y))
pygame.display.flip()
status = True

lights = []
while status:

    for i in pygame.event.get():
        if i.type == pygame.QUIT:
            status = False
        elif i.type == VIDEORESIZE:
            screen.blit(pygame.transform.scale(image, i.dict['size']),(0,0))
        elif i.type == VIDEOEXPOSE:  # handles window minimising/maximising
            screen.fill((0, 0, 0))
            screen.blit(pygame.transform.scale(image, screen.get_size()), (0, 0))
            pygame.display.update()
        elif i.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            if len(lights) == 50:
                print(lights)
                status = False
            lights.append(pos)
pygame.quit()
