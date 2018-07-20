import random, pygame, sys, time
from pygame.locals import *

PlayerImg = pygame.image.load("player.png")

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
YELLOW    = (239, 255,  96)
BLUE      = ( 66, 194, 244)
BGCOLOR = BLACK

LEFT = 'left'
RIGHT = 'right'
NONE = 'none'

Score = 0
bullets = []
alienCoords = []
barricadeCoords = []
Win = True;
AlienLowest = -1
AlienHighest = -1

class Bullet:
    def __init__(self, color, direction, coords):
        self.color = color
        self.direction = direction
        self.coords = coords

class Alien:
    def __init__(self, level):
        self.level = level
        self.coords = coords

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('Space Invaders')

    while True:
        ClearAll()
        CreateBarricades()
        runGame()
        showGameOverScreen()

def runGame():
    # Player Vars
    startx = 5
    starty = 45
    playerCoords = {'x': startx, 'y': starty}
    direction = NONE     

    # Alien Vars
    alienCoords = CreateAliens()
    changeDir = False
    movedDown = False
    WaitAmount = 10 # Number of game loops to wait until moving the aliens
    alienWait = WaitAmount
    CurrentAlienCount = 0
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
                    bullet = Bullet(YELLOW, -1, {'x': playerCoords['x'], 'y': playerCoords['y'] - 1}) #Create the bullet
                    bullets.append(bullet) #Add to bullet list
                elif event.key == K_k: # if 'k' is pressed 
                   alienCoords.clear() # kill those filthy aliens!
                   bullets.clear()
            elif event.type == KEYUP: #Signify that the movement should stop
                if (event.key == K_LEFT or event.key == K_a):
                    direction = NONE
                elif (event.key == K_RIGHT or event.key == K_d):
                    direction = NONE     

        start = time.time()
        CollisionDetection(alienCoords, bullets, playerCoords, barricadeCoords) #Do that collision detection magic!
        end = time.time()
        print(end - start)
        
        TotalAliens = len(alienCoords)
        if len(alienCoords) < (TotalAliens * .75):
            WaitAmount = 9
        if len(alienCoords) < (TotalAliens * .50):
            WaitAmount = 8
        if len(alienCoords) < (TotalAliens * .25):
            WaitAmount = 6

        # move the player
        if direction == LEFT and playerCoords['x'] > 0:
            playerCoords['x'] = playerCoords['x'] - 1
        elif direction == RIGHT and playerCoords['x'] < (WINDOWWIDTH / CELLSIZE) -  1:
            playerCoords['x'] = playerCoords['x'] + 1          
        
        # Move the bullets that exist
        if len(bullets) > 0: # If there are bullets
            for bullet in bullets: # Loop through the bullets
                bullet.coords['y'] = bullet.coords['y'] + bullet.direction # Move it up

                if bullet.coords['y'] < 0 or bullet.coords['y'] > 48: # If the bullet has reached the end of the screen
                    bullets.remove(bullet) # Remove it

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
                
                if alienCoords[index]['x'] > (WINDOWWIDTH / CELLSIZE) -  2 or alienCoords[index]['x'] <  1: # Reached the end, signify a down and change direction
                    changeDir = True

            if movedDown: # Aliens have been moved down, now change their direction
                x = prevx * -1 # Switch the x direction
                y = 0 # Don't move down
                global AlienLowest
                AlienLowest += 1
                global AlienHighest
                AlienHighest += 1
                changeDir = False
                movedDown = False

                if AlienLowest > 38:
                    lose(alienCoords)
                    break

            alienWait = WaitAmount # Reset the timer
            AlienShoot(alienCoords) # Have the aliens shoot
            AlienShoot(alienCoords) # Shoot again
        
        alienWait -= 1 # Count down for the alien timer

        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()
        drawBarricade(barricadeCoords)
        drawPlayer(playerCoords)
        drawBullets(bullets)
        drawAliens(alienCoords)
        drawScore()
        pygame.display.update()
        FPSCLOCK.tick(FPS)

        if len(alienCoords) == 0: # Check if there are still aliens
            break # There are none left, end the game

def drawPressKeyMsg():
    pressKeySurf = BASICFONT.render('Press a key to play.', True, DARKGRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (WINDOWWIDTH - 200, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)

def terminate():
    pygame.quit()
    sys.exit()

def showGameOverScreen():
    top = 'Victory'
    bottom = 'Royale'
    if not Win:
        top = 'You'
        bottom = 'Died'

    gameOverFont = pygame.font.Font('freesansbold.ttf', 150)
    gameSurf = gameOverFont.render(top, True, WHITE)
    overSurf = gameOverFont.render(bottom, True, WHITE)
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

    global AlienHighest
    global AlienLowest
    AlienHighest = AlienCoords[1]['y']
    AlienLowest = AlienCoords[-1]['y']

    return AlienCoords


def drawBullets(bullets):
    for bullet in bullets:
        x = bullet.coords['x'] * CELLSIZE
        y = bullet.coords['y'] * CELLSIZE
        BulletRec = pygame.Rect(x,y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, bullet.color, BulletRec)

def drawAliens(alienCoords):
    for coord in alienCoords: # for each alien
        x = coord['x'] * CELLSIZE # Multiply location by its cell size
        y = coord['y'] * CELLSIZE
        Alien = pygame.Rect(x,y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, RED, Alien)

def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE): # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE): # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))

    pygame.draw.line(DISPLAYSURF, RED, (0, (38 * CELLSIZE)), (WINDOWWIDTH, (38 * CELLSIZE)))

def drawScore():
    scoreSurf = BASICFONT.render('Score: %s' % (Score), True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 120, 10)
    DISPLAYSURF.blit(scoreSurf, scoreRect)

def drawPlayer(playerCoords):
    x = playerCoords['x'] * CELLSIZE
    y = playerCoords['y'] * CELLSIZE
    Player = pygame.Rect(x,y, CELLSIZE, CELLSIZE)    
    pygame.draw.rect(DISPLAYSURF, DARKGREEN, Player)
    DISPLAYSURF.blit(PlayerImg, (x - 10, y))

def drawBarricade(barricadeCoords):
    for coord in barricadeCoords: # for each barricade part
        x = coord['x'] * CELLSIZE # Multiply location by its cell size
        y = coord['y'] * CELLSIZE
        barricadepart = pygame.Rect(x,y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, WHITE, barricadepart)

#Could this be improved?????
def AlienShoot(alienCoords):
    Columns = []
    LowestY = -1    

    for alien in alienCoords: # Loop through aliens
        alienX = alien['x'] * CELLSIZE # Get column value of each alien
        if alienX not in Columns: # if the current column value hasnt been recorded
            Columns.append(alienX) # add the current column to the list of clumns
    
    ShootingColumn = random.randint(0, len(Columns) - 1) # Pick a random column

    for alien in alienCoords: # Loop again to find the bottom row
        alienX = alien['x'] * CELLSIZE # get the column value of each alien
        if alienX == Columns[ShootingColumn]: # if the current alien is in the select column
            alienY = alien['y'] * CELLSIZE  # record current y value
            if alienY > LowestY: # See if this is the lowest down alien we have seen
                LowestY = alienY # This is the lowest down alien

    bullet = Bullet(BLUE, 1, {'x': Columns[ShootingColumn] / CELLSIZE, 'y': (LowestY / CELLSIZE) + 1}) # Create Alien bullet at the select column and the lowest down alien
    bullets.append(bullet) # Add to bullet list
        
def CollisionDetection(alienCoords, bullets, playerCoords, barricades):
    for bullet in bullets: # Loop through all the bullets
        Bulletx = bullet.coords['x']
        Bullety = bullet.coords['y']

        #Check if bullet is in range of aliens        
        if Bullety <= AlienLowest and Bullety >= AlienHighest:
            for Aliencoord in alienCoords: # Loop through all the aliens
                Alienx = Aliencoord['x']
                Alieny = Aliencoord['y']

                if abs(Alienx - Bulletx) < 1 and abs(Alieny - Bullety) < 1: # Check if a bullet is on the same cell as an alien
                    alienCoords.remove(Aliencoord) # Kill alien
                    bullets.remove(bullet) # Remove bullet
                    global Score 
                    Score += 10 # 10 points Gryffindor!!!
                    break

        #Check if bullet is in range of barricades
        elif Bullety > 38 and Bullety < 44:
            for barricade in barricades: # Loop through all the barricades
                barrx = barricade['x']
                barry = barricade['y']

                if abs(barrx - Bulletx) < 1 and abs(barry - Bullety) < 1: # Check if a bullet is on the same cell as a barricade part
                    barricades.remove(barricade) # remove barricade
                    bullets.remove(bullet) # Remove bullet
                    break

        #Check if bullet is in range of player
        elif Bullety == 45:            
            Playerx = playerCoords['x'] 
            Playery = playerCoords['y']
            if abs(Playerx - Bulletx) < 1 and abs(Playery - Bullety) < 1: # Check if a bullet is on the same cell as the player
                lose(alienCoords)
                break 

def CreateBarricades():
    x = 1
    while x < 70:
        barricadeCoords.append({'x': x + 2, 'y': 43})
        barricadeCoords.append({'x': x + 2, 'y': 42})
        barricadeCoords.append({'x': x + 2, 'y': 41})
        barricadeCoords.append({'x': x + 2, 'y': 40})
        barricadeCoords.append({'x': x + 3, 'y': 42})
        barricadeCoords.append({'x': x + 3, 'y': 41})
        barricadeCoords.append({'x': x + 3, 'y': 40})
        barricadeCoords.append({'x': x + 3, 'y': 39})
        barricadeCoords.append({'x': x + 4, 'y': 42})
        barricadeCoords.append({'x': x + 4, 'y': 41})
        barricadeCoords.append({'x': x + 4, 'y': 40})
        barricadeCoords.append({'x': x + 4, 'y': 39})
        barricadeCoords.append({'x': x + 5, 'y': 42})
        barricadeCoords.append({'x': x + 5, 'y': 41})
        barricadeCoords.append({'x': x + 5, 'y': 40})
        barricadeCoords.append({'x': x + 5, 'y': 39})
        barricadeCoords.append({'x': x + 6, 'y': 43})
        barricadeCoords.append({'x': x + 6, 'y': 42})
        barricadeCoords.append({'x': x + 6, 'y': 41})
        barricadeCoords.append({'x': x + 6, 'y': 40})        

        x += 9

def ClearAll():
    bullets.clear()
    alienCoords.clear()
    barricadeCoords.clear()

def lose(alienCoords):
    alienCoords.clear() # kill those filthy aliens to end the game
    bullets.clear()
    global Win
    Win = False # You did not win

if __name__ == '__main__':
    main()