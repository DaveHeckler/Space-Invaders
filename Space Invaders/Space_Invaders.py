import random, pygame, sys
from pygame.locals import *

FPS = 15
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
CELLSIZE = 10
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)

#             R    G    B
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
RED       = (255,   0,   0)
GREEN     = (  0, 255,   0)
DARKGREEN = (  0, 155,   0)
DARKGRAY  = ( 40,  40,  40)
YELLOW    = ( 239,255,  96)
BGCOLOR = BLACK

LEFT = 'left'
RIGHT = 'right'
NONE = 'none'

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('Space Invaders')

    while True:
        runGame()
        showGameOverScreen()

def runGame():
    #Player Vars
    startx = 5
    starty = 45
    playerCoords = {'x': startx,     'y': starty}
    direction = NONE
    bulletCoords = []       

    #Alien Vars
    alienCoords = CreateAliens()
    changeDir = False
    movedDown = False
    WaitAmount = 10 #Number of game loops to wait until moving the aliens
    alienWait = WaitAmount
    x = 1
    y = 0

    while True: # main game loop
        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN: # Signify which direction to move the player
                if (event.key == K_LEFT or event.key == K_a):
                    direction = LEFT
                elif (event.key == K_RIGHT or event.key == K_d):
                    direction = RIGHT
                elif event.key == K_ESCAPE:
                    terminate()
                elif event.key == K_SPACE:
                    bulletCoords.append({'x': playerCoords['x'], 'y': playerCoords['y']}) #Add a bullet
            elif event.type == KEYUP: #Signify that the movement should stop
                if (event.key == K_LEFT or event.key == K_a):
                    direction = NONE
                elif (event.key == K_RIGHT or event.key == K_d):
                    direction = NONE     

        # move the worm by adding a segment in the direction it is moving}
        if direction == LEFT and playerCoords['x'] > 0:
            playerCoords['x'] = playerCoords['x'] - 1
        elif direction == RIGHT and playerCoords['x'] < (WINDOWWIDTH / CELLSIZE) -  1:
            playerCoords['x'] = playerCoords['x'] + 1          
        
        # Move the bullets that exist
        if len(bulletCoords) > 0: # If there are bullets
            for coord in bulletCoords: # Loop through the bullets
                coord['y'] = coord['y'] - 1 # Move it up

                if coord['y'] < 0: # If the bullet has reached the end of the screen
                    bulletCoords.remove(coord) #Remove it

        # Move the aliens
        if len(alienCoords) > 0 and alienWait == 0: #If wait is up and there are aliens
            if changeDir: # Aliens reached the end, move them down
                prevx = x # Save old direction to flip later
                x = 0 # Dont move left or right
                y = 1 # Move down 1
                movedDown = True

            for alien in alienCoords: # Loop through each alien
                index  = alienCoords.index(alien) # Get the index of the current
                alienCoords[alienCoords.index(alien)] = {'x': alien['x'] + x, 'y': alien['y'] + y} # Move the alien
                
                if alienCoords[index]['x'] > (WINDOWWIDTH / CELLSIZE) -  2: # Reached the end, signify a down and change direction
                    changeDir = True
                if alienCoords[index]['x'] <  1:
                    changeDir = True

            if movedDown: # Aliens have been moved down, now change their direction
                x = prevx * -1 # Switch the x direction
                y = 0 # Don't move down
                changeDir = False
                movedDown = False

            alienWait = WaitAmount # Reset the timer
        alienWait -= 1 # Count down for the alien timer

        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()
        drawPlayer(playerCoords)
        drawBullets(bulletCoords)
        drawAliens(alienCoords)
        drawScore(playerCoords['x'])
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def drawPressKeyMsg():
    pressKeySurf = BASICFONT.render('Press a key to play.', True, DARKGRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (WINDOWWIDTH - 200, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)

def terminate():
    pygame.quit()
    sys.exit()

def getRandomLocation():
    return {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}

def showGameOverScreen():
    gameOverFont = pygame.font.Font('freesansbold.ttf', 150)
    gameSurf = gameOverFont.render('Game', True, WHITE)
    overSurf = gameOverFont.render('Over', True, WHITE)
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()
    gameRect.midtop = (WINDOWWIDTH / 2, 10)
    overRect.midtop = (WINDOWWIDTH / 2, gameRect.height + 10 + 25)

    DISPLAYSURF.blit(gameSurf, gameRect)
    DISPLAYSURF.blit(overSurf, overRect)
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(500)
    checkForKeyPress() #clear out any key presses in the event queue

    while True:
        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return

def checkForKeyPress():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key

def drawScore(score):
    scoreSurf = BASICFONT.render('Score: %s' % (score), True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 120, 10)
    DISPLAYSURF.blit(scoreSurf, scoreRect)

def drawPlayer(playerCoords):
    x = playerCoords['x'] * CELLSIZE
    y = playerCoords['y'] * CELLSIZE
    Player = pygame.Rect(x,y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, DARKGREEN, Player)

def drawBullets(bulletCoords):
    for coord in bulletCoords:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        Bullet = pygame.Rect(x,y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, YELLOW, Bullet)

def CreateAliens():
    #Setup the AlienCoord Datastructure
    AlienCoords = []
    Alien = {}

    #Loop through the portion of the window where there should be aliens
    for y in range(int((WINDOWHEIGHT / CELLSIZE))):
        for x in range(int((WINDOWWIDTH / CELLSIZE))):
            if (x % 2) == 0 and (y % 2) == 0 and x > 8 and x < 56 and y < 20 and y > 1: #Even cells only
                Alien = ({'x': x,     'y': y}) #Create Alien
                AlienCoords.append(Alien) #Add Alien to list

    return AlienCoords

def drawAliens(alienCoords):
    for coord in alienCoords:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        Alien = pygame.Rect(x,y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, RED, Alien)

def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE): # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE): # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))

if __name__ == '__main__':
    main()