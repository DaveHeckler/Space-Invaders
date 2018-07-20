import random, pygame, sys, time
from pygame.locals import *

PlayerImg = pygame.image.load("player.png")
HeartImg = pygame.image.load('heart.png')

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

#Ditch?
LEFT = 'left'
RIGHT = 'right'
NONE = 'none'

#Game Vars
Score = 0
Lives = 3
Win = True;

#Lists and such
bullets = []
aliens = []
barricadeCoords = []

#Alien Vars
alienLowest = -1
alienHighest = -1

class Bullet:
    def __init__(self, color, direction, coords):
        self.color = color
        self.direction = direction
        self.coords = coords

class Alien:
    def __init__(self, level, coords):
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
    playerCoords = {'x': 5, 'y': 45}
    direction = NONE     

    # Alien Vars
    global aliens
    aliens = CreateAliens()
    TotalAliens = len(aliens)
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
                    bullet = Bullet(YELLOW, -1, {'x': playerCoords['x'], 'y': playerCoords['y'] - 1}) # Create the bullet
                    bullets.append(bullet) #Add to bullet list
                elif event.key == K_k: # if 'k' is pressed 
                   aliens.clear() # kill those filthy aliens!
                   bullets.clear()
            elif event.type == KEYUP: # Signify that the movement should stop
                if (event.key == K_LEFT or event.key == K_a):
                    direction = NONE
                elif (event.key == K_RIGHT or event.key == K_d):
                    direction = NONE     

        start = time.time()
        CollisionDetection(aliens, bullets, playerCoords, barricadeCoords) # Do that collision detection magic!
        end = time.time()
        print('Collision detection time: ' + str(end - start))       
        
        if len(aliens) < (TotalAliens * .75):
            WaitAmount = 9
        if len(aliens) < (TotalAliens * .50):
            WaitAmount = 8
        if len(aliens) < (TotalAliens * .25):
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
        if len(aliens) > 0 and alienWait == 0: #If wait is up and there are aliens
            if changeDir: # Aliens reached the end, move them down
                prevx = x # Save old direction to flip later
                x = 0 # Dont move left or right
                y = 1 # Move down 1
                movedDown = True

            for alien in aliens: # Loop through each alien
                alien.coords = {'x': alien.coords['x'] + x, 'y': alien.coords['y'] + y} # Move the alien
                
                if alien.coords['x'] > (WINDOWWIDTH / CELLSIZE) -  2 or alien.coords['x'] <  1: # Reached the end, signify a down and change direction
                    changeDir = True

            if movedDown: # Aliens have been moved down, now change their direction
                x = prevx * -1 # Switch the x direction
                y = 0 # Don't move down
                global alienLowest
                alienLowest += 1
                global alienHighest
                alienHighest += 1
                changeDir = False
                movedDown = False

                if alienLowest > 38:
                    lose(aliens)
                    break

            alienWait = WaitAmount # Reset the timer
            AlienShoot(aliens) # Have the aliens shoot
            AlienShoot(aliens) # Shoot again
        
        alienWait -= 1 # Count down for the alien timer
        
        #Draw Everything!
        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()
        drawBarricade(barricadeCoords)
        drawPlayer(playerCoords)
        drawBullets(bullets)
        drawAliens(aliens)
        drawScore()
        drawLives()
        pygame.display.update()
        FPSCLOCK.tick(FPS)

        if len(aliens) == 0: # Check if there are still aliens
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

    if (Lives == 0):
        terminate()

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
    # Setup the AlienCoord Datastructure (List of objects)
    Aliens = []
    alien = {}

    # Loop through the portion of the window where there should be aliens
    for y in range(int((WINDOWHEIGHT / CELLSIZE))):
        for x in range(int((WINDOWWIDTH / CELLSIZE))):
            if (x % 2) == 0 and (y % 2) == 0 and x > 8 and x < 56 and y < 20 and y > 1: # Even cells only
                alien = Alien(1, {'x': x,     'y': y}) #Create Alien
                Aliens.append(alien) #Add Alien to list

    # Record the top and bottom of the aliens, used for collision detection
    global alienHighest
    global alienLowest
    alienHighest = Aliens[1].coords['y']
    alienLowest = Aliens[-1].coords['y']

    return Aliens


def drawBullets(bullets):
    for bullet in bullets:
        x = bullet.coords['x'] * CELLSIZE
        y = bullet.coords['y'] * CELLSIZE
        BulletRec = pygame.Rect(x,y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, bullet.color, BulletRec)

def drawAliens(aliens):
    for alien in aliens: # for each alien
        x = alien.coords['x'] * CELLSIZE # Multiply location by its cell size
        y = alien.coords['y'] * CELLSIZE
        alien = pygame.Rect(x,y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, RED, alien)

def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE): # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE): # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))

    pygame.draw.line(DISPLAYSURF, RED, (0, (38 * CELLSIZE)), (WINDOWWIDTH, (38 * CELLSIZE)))

def drawScore():
    scoreSurf = BASICFONT.render('Score: %s' % (Score), True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 120, 1)
    DISPLAYSURF.blit(scoreSurf, scoreRect)

def drawLives():
    x = 1
    for i in range(Lives):
        DISPLAYSURF.blit(HeartImg, (x, 1))
        x += 3 * CELLSIZE

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
def AlienShoot(aliens):
    Columns = []
    LowestY = -1    

    for alien in aliens: # Loop through aliens
        alienX = alien.coords['x'] * CELLSIZE # Get column value of each alien
        if alienX not in Columns: # if the current column value hasnt been recorded
            Columns.append(alienX) # add the current column to the list of clumns
    
    ShootingColumn = random.randint(0, len(Columns) - 1) # Pick a random column

    for alien in aliens: # Loop again to find the bottom row
        alienX = alien.coords['x'] * CELLSIZE # get the column value of each alien
        if alienX == Columns[ShootingColumn]: # if the current alien is in the select column
            alienY = alien.coords['y'] * CELLSIZE  # record current y value
            if alienY > LowestY: # See if this is the lowest down alien we have seen
                LowestY = alienY # This is the lowest down alien

    bullet = Bullet(BLUE, 1, {'x': Columns[ShootingColumn] / CELLSIZE, 'y': (LowestY / CELLSIZE) + 1}) # Create Alien bullet at the select column and the lowest down alien
    bullets.append(bullet) # Add to bullet list
        
def CollisionDetection(aliens, bullets, playerCoords, barricades):
    for bullet in bullets: # Loop through all the bullets
        Bulletx = bullet.coords['x']
        Bullety = bullet.coords['y']

        #Check if bullet is in range of aliens        
        if Bullety <= alienLowest and Bullety >= alienHighest:
            for alien in aliens: # Loop through all the aliens
                Alienx = alien.coords['x']
                Alieny = alien.coords['y']

                if abs(Alienx - Bulletx) < 1 and abs(Alieny - Bullety) < 1: # Check if a bullet is on the same cell as an alien
                    aliens.remove(alien) # Kill alien
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
                lose(aliens) # you lost
                break 

def CreateBarricades():
    barricadeCoords.clear()
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
    aliens.clear()
    barricadeCoords.clear()

def lose(aliens):
    aliens.clear() # kill those filthy aliens to end the game
    bullets.clear()
    global Win
    Win = False # You did not win
    global Lives
    Lives -= 1

if __name__ == '__main__':
    main()