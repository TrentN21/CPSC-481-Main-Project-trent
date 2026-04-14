import pygame
import random
import time

# Set up Pygame
pygame.init()

# Size of Display
x = 800
y = 400

# Background
screen = pygame.display.set_mode((x, y))
screen.fill('bisque2')

# font for text
font = pygame.font.SysFont("Arial", 32)

# pits
pits= [
  [x/10,y/4,x/6.5,y/1.7,4],
  [x/10,y/4,x/3.7,y/1.7,4],
  [x/10,y/4,x/2.58,y/1.7,4],  
  [x/10,y/4,x/1.98,y/1.7,4],
  [x/10,y/4,x/1.6,y/1.7,4],
  [x/10,y/4,x/1.3335,y/1.7,4],
  [x/10,y/1.5,x/1.15,y/6,0],
  [x/10,y/4,x/1.3335,y/6,4],
  [x/10,y/4,x/1.6,y/6,4],
  [x/10,y/4,x/1.98,y/6,4],
  [x/10,y/4,x/2.58,y/6,4],
  [x/10,y/4,x/3.7,y/6,4],
  [x/10,y/4,x/6.5,y/6,4],
  [x/10,y/1.5,x/25,y/6,0]
]

# end condition for player
endcondition = [
  [x/10,y/4,x/6.5,y/1.7,0],
  [x/10,y/4,x/3.7,y/1.7,0],
  [x/10,y/4,x/2.58,y/1.7,0],  
  [x/10,y/4,x/1.98,y/1.7,0],
  [x/10,y/4,x/1.6,y/1.7,0],
  [x/10,y/4,x/1.3335,y/1.7,0]
]

#end condition for opponents
opsendcondition = [
  [x/10,y/4,x/1.3335,y/6,0],
  [x/10,y/4,x/1.6,y/6,0],
  [x/10,y/4,x/1.98,y/6,0],
  [x/10,y/4,x/2.58,y/6,0],
  [x/10,y/4,x/3.7,y/6,0],
  [x/10,y/4,x/6.5,y/6,0]
]

# logic for opponent
def opchoice():
  #add logic later
  refresh()
  x=random.randint(7,12) 
  while pits[x][4] == 0:
    x=random.randint(7,12)
  print(x)
  return(x)

#refreshes board
def refresh():
    for pit in pits:
        square = pygame.Surface(pit[:2])
        square.fill('bisque1')
        screen.blit(square, (pit[2:4]))
        value = font.render(f"{pit[4]}", True, (0, 0, 0))
        screen.blit(value, (pit[2:4]))
    pygame.display.flip()


# Action logic 
def action(number, side):
  x = pits[number][4]
  pits[number][4] = 0
  refresh()
  counter = number
  for i in range(x):
    counter+= 1
    if side == 0 and counter == 13:
      counter += 1
    elif side == 1 and counter == 7:
      counter += 1
    if counter > 13:
      counter = (counter % 13)-1
    pits[counter][4] += 1
    time.sleep(.5)
    refresh()
  if side == 0 and counter < 6 and pits[counter][4] == 1 and pits[-(counter+2)][4] != 0:
    pits[6][4]  += (pits[-(counter+2)][4] + 1)
    pits[-(counter+2)][4] = 0
    pits[counter][4] = 0
  elif side == 1 and 13 > counter > 6 and pits[counter][4] == 1 and pits[12-counter][4] != 0:
    pits[-1][4]  += (pits[12-counter][4] + 1)
    pits[12-counter][4] = 0
    pits[counter][4] = 0
  time.sleep(1)
  refresh()
  if counter == 13:
    action(opchoice(),1)
  elif side == 0 and counter != 6:
    action(opchoice(),1)


# loop set up
running = True
clock = pygame.time.Clock()

# Main loop
while running:
  # Checks end condition
  if pits[:6] == endcondition:
    for i in range(7,13):
      pits[-1][4] += pits[i][4]
      pits[i][4] = 0
  elif pits[7:13] == opsendcondition:
    for i in range(0,6):
      pits[6][4] += pits[i][4]
      pits[i][4] = 0

  # player input 
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
    elif pygame.mouse.get_pressed()[0]:
      for i in range(6):
        pit = pits[i]
        rect = pygame.Rect(pit[2:4],pit[:2])
        if rect.collidepoint(pygame.mouse.get_pos()) and pits[i][4] != 0:
          action(i,0)
    refresh()

pygame.quit()
