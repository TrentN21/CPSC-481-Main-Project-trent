import pygame

pygame.init()

x = 800
y = 400

screen = pygame.display.set_mode((x, y))
screen.fill('bisque2')

goal = pygame.Surface((x/10,y/1.5))
goal.fill('bisque1')

spot = pygame.Surface((x/10,y/4))
spot.fill('bisque1')
 

clock = pygame.time.Clock()
running = True



while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.blit(goal, (x/25,y/6))
    screen.blit(goal, (x/1.15,y/6))
    screen.blit(spot, (x/6.5,y/6))
    screen.blit(spot, (x/3.7,y/6))
    screen.blit(spot, (x/2.58,y/6))
    screen.blit(spot, (x/1.98,y/6))
    screen.blit(spot, (x/1.6,y/6))
    screen.blit(spot, (x/1.3335,y/6))
    screen.blit(spot, (x/6.5,y/1.7))
    screen.blit(spot, (x/3.7,y/1.7))
    screen.blit(spot, (x/2.58,y/1.7))
    screen.blit(spot, (x/1.98,y/1.7))
    screen.blit(spot, (x/1.6,y/1.7))
    screen.blit(spot, (x/1.3335,y/1.7))
    
    
    
    pygame.display.flip()

    clock.tick(60)

pygame.quit()
