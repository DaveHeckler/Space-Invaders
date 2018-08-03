import random, pygame, sys, time
from pygame.locals import *

class Game:
    def __init__(self, Score, Lives, WinStatus, GameOver):
        self.Score = Score
        self.Lives = Lives
        self.WinStatus = WinStatus
        self.GameOver = GameOver

class Level:
    def __init__(self, levelNum, orangeAliens, purpleAliens, alienSpeed):
        self.levelNum = levelNum
        self.orangeAliens = orangeAliens
        self.purpleAliens = purpleAliens
        self.alienSpeed = alienSpeed

class Bullet:
    def __init__(self, color, direction, coords):
        self.color = color
        self.direction = direction
        self.coords = coords

    def draw(self):    
        x = self.coords['x'] * CELLSIZE
        y = self.coords['y'] * CELLSIZE
        BulletRec = pygame.Rect(x,y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, self.color, BulletRec)

    def move(self):
        self.coords['y'] = self.coords['y'] + self.direction # Move it up
        if self.coords['y'] < 0 or self.coords['y'] > 48: # If the bullet has reached the end of the screen
            bullets.remove(self) # Remove it

class Alien:
    def __init__(self, level, coords, color):
        self.level = level
        self.coords = coords
        self.color = color

    def draw(self):
        x = self.coords['x'] * CELLSIZE # Multiply location by its cell size
        y = self.coords['y'] * CELLSIZE
        alienRec = pygame.Rect(x,y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, self.color, alienRec)

    def LowerLevel(self):
        self.level = self.level - 1 
        
        #Reset to the correct color for the new level
        if self.level == 1:
            self.color = RED
        elif self.level == 2:
            self.color = PURPLE      
            

    

class Barricade:
    def __init__(self, level, coords, color):
        self.level = level
        self.coords = coords
        self.color = color

    def draw(self):    
        x = self.coords['x'] * CELLSIZE # Multiply location by its cell size
        y = self.coords['y'] * CELLSIZE
        barricadepart = pygame.Rect(x,y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, self.color, barricadepart)

PlayerImg = pygame.image.load('player.png')
HeartImg = pygame.image.load('heart.png')

FPS = 15
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
CELLSIZE = 10
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)

#Colors
#             R    G    B
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
RED       = (255,   0,   0)
GREEN     = (  0, 255,   0)
DARKGREEN = (  0, 155,   0)
DARKGRAY  = ( 40,  40,  40)
YELLOW    = (239, 255,  96)
BLUE      = ( 66, 194, 244)
PURPLE    = (185,  66, 244)
ORANGE    = (242, 169,  53)
BGCOLOR = BLACK

#Setup Game Object
game = Game(0, 3, False, False)
currentLevel = -1

#Lists
bullets = []
aliens = []
barricades = []
levels = []

#Alien Vars
alienLowest = -1
alienHighest = -1
TotalAliens = -1

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, aliens, TotalAliens, game, currentLevel, bullets, levels
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('Space Invaders')

    #Create populate the level definitions
    levelNum = 0
    levels = createLevels()
    currentLevel = levels[levelNum]
    #Create aliens and 
    CreateAliens()
    TotalAliens = len(aliens)
    CreateBarricades()

    while True:
        runGame()
        showGameOverScreen()
        bullets.clear()
        game.GameOver = False
        
        if game.WinStatus:
            if levelNum >= len(levels) - 1:
                break
            levelNum += 1
            currentLevel = levels[levelNum]
            aliens.clear
            barricades.clear
            CreateAliens()
            TotalAliens = len(aliens)
            CreateBarricades()

    VictoryRoyale()

def createLevels():    
    levels = []
    # Open the levels text file
    with open("Levels.txt") as f:
        for line in f: # Loop through the lines
            levelNum = int(line.rstrip())                        
            orangeNum = int(f.readline().rstrip())
            purpleNum = int(f.readline().rstrip())
            alienSpeed = int(f.readline().rstrip())
            level = Level(levelNum, orangeNum, purpleNum, alienSpeed)
            levels.append(level)
            blank = f.readline().rstrip()

    return levels

def runGame():
    global game, alienLowest, alienHighest
    # Player Vars
    playerCoords = {'x': 5, 'y': 45}
    direction = 'none'     

    # Alien Vars
    changeDir = False
    movedDown = False
    WaitAmount = currentLevel.alienSpeed # Number of game loops to wait until moving the aliens
    alienWait = WaitAmount
    CurrentAlienCount = 0
    x = 1
    y = 0

    while True: # main game loop
        direction = eventLoop(playerCoords, direction)
        
        # Record collision detection time for science
        start = time.time()
        CollisionDetection(aliens, bullets, playerCoords, barricades) # Do that collision detection magic!
        end = time.time()
        print('Collision detection time: ' + str(end - start))       
        
        WaitAmount = speedUp(WaitAmount)

        movePlayer(playerCoords, direction)    
        
        for bullet in bullets:
            bullet.move()

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
                alienLowest += 1
                alienHighest += 1
                changeDir = False
                movedDown = False

                if alienLowest > 38:
                    lose(aliens)
                    break

            alienWait = WaitAmount # Reset the timer
            AlienShoot(aliens) # Have the aliens shoot
        
        alienWait -= 1 # Count down for the alien timer             

        drawScreen(playerCoords)

        if len(aliens) == 0: # Check if there are still aliens
            game.WinStatus = True
            break # There are none left, next level
        if game.GameOver:
            break

def drawScreen(playerCoords):
    #Draw Everything!
    DISPLAYSURF.fill(BGCOLOR)
    drawGrid()
    drawPlayer(playerCoords)
    for barricade in barricades: # for each barricade part    
        barricade.draw()
    for bullet in bullets: # for each bullet
        bullet.draw()
    for alien in aliens: # for each alien
        alien.draw()
    drawScore()
    drawLivesAndLevel()
    pygame.display.update()
    FPSCLOCK.tick(FPS)

def movePlayer(playerCoords, direction):
    # move the player
    if direction == 'left' and playerCoords['x'] > 0:
        playerCoords['x'] = playerCoords['x'] - 1
    elif direction == 'right' and playerCoords['x'] < (WINDOWWIDTH / CELLSIZE) -  1:
        playerCoords['x'] = playerCoords['x'] + 1 

def speedUp(WaitAmount):
    # Speed up the aliens depending on how many are left    
    if len(aliens) < (TotalAliens * .75):
        WaitAmount = currentLevel.alienSpeed - 1
    if len(aliens) < (TotalAliens * .50): 
        WaitAmount = currentLevel.alienSpeed - 2
    if len(aliens) < (TotalAliens * .25):
        WaitAmount = currentLevel.alienSpeed - 4
    return WaitAmount

def eventLoop(playerCoords, direction):
    global game
    for event in pygame.event.get(): # event handling loop
        if event.type == QUIT:
            terminate()
        elif event.type == KEYDOWN: # Signify which direction to move the player
            if (event.key == K_LEFT or event.key == K_a):
                direction = 'left'
            elif (event.key == K_RIGHT or event.key == K_d):
                direction = 'right'
            elif event.key == K_ESCAPE:
                terminate()
            elif event.key == K_SPACE:                    
                bullet = Bullet(YELLOW, -1, {'x': playerCoords['x'] + 1, 'y': playerCoords['y'] - 1}) # Create the bullet
                bullets.append(bullet) #Add to bullet list
            elif event.key == K_k: # if 'k' is pressed 
                aliens.clear()
        elif event.type == KEYUP: # Signify that the movement should stop
            if (event.key == K_LEFT or event.key == K_a):
                direction = 'none'
            elif (event.key == K_RIGHT or event.key == K_d):
                direction = 'none'     
    return direction

def drawPressKeyMsg():
    pressKeySurf = BASICFONT.render('Press a key to play.', True, DARKGRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (WINDOWWIDTH - 200, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)

def terminate():
    pygame.quit()
    sys.exit()

def showGameOverScreen():
    #Default victory message
    top = 'KEEP'
    bottom = 'GOING'

    #Loss message
    if not game.WinStatus:
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

    if (game.Lives == 0):
        terminate()

    checkForKeyPress() #clear out any key presses in the event queue

    while True:
        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return

def VictoryRoyale():
    #Default victory message
    top = 'Victory'
    bottom = 'Royale'    

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
        blank = 0

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
    global aliens, alienHighest, alienLowest
    # Setup the AlienCoord Datastructure (List of objects)
    alien = {}
    orangeNum = currentLevel.orangeAliens
    purpleNum = currentLevel.purpleAliens

    # Loop through the portion of the window where there should be aliens
    for y in range(int((WINDOWHEIGHT / CELLSIZE))):
        for x in range(int((WINDOWWIDTH / CELLSIZE))):
            if (x % 2) == 0 and (y % 2) == 0 and x > 8 and x < 56 and y < 20 and y > 1: # Even cells only
                # Check what type of alien to create
                if orangeNum > 0:
                    lvl = 3
                    color = ORANGE
                    orangeNum -= 1
                elif purpleNum > 0:
                    lvl = 2
                    color = PURPLE  
                    purpleNum -= 1
                else:
                    lvl = 1
                    color = RED  

                alien = Alien(lvl, {'x': x,'y': y}, color) # Create Alien
                aliens.append(alien) # Add Alien to list

    # Record the top and bottom of the aliens, used for collision detection
    alienHighest = aliens[1].coords['y']
    alienLowest = aliens[-1].coords['y']

def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE): # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE): # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))

    # Draw the line that the aliens can't cross
    pygame.draw.line(DISPLAYSURF, RED, (0, (38 * CELLSIZE)), (WINDOWWIDTH, (38 * CELLSIZE)))

def drawScore():
    scoreSurf = BASICFONT.render('Score: %s' % (game.Score), True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 120, 1)
    DISPLAYSURF.blit(scoreSurf, scoreRect)

def drawLivesAndLevel():
    x = 1
    for i in range(game.Lives):
        DISPLAYSURF.blit(HeartImg, (x, 1))
        x += 3 * CELLSIZE

    levelSurf = BASICFONT.render('Level: %s' % (currentLevel.levelNum), True, WHITE)
    levelRect = levelSurf.get_rect()
    levelRect.topleft = (x + CELLSIZE, 1)
    DISPLAYSURF.blit(levelSurf, levelRect)

def drawPlayer(playerCoords):
    x = playerCoords['x'] * CELLSIZE
    y = playerCoords['y'] * CELLSIZE  
    DISPLAYSURF.blit(PlayerImg, (x, y))

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
    global game
    for bullet in bullets: # Loop through all the bullets
        #Check if bullet is in range of aliens        
        if bullet.coords['y'] <= alienLowest and bullet.coords['y'] >= alienHighest:
            for alien in aliens: # Loop through all the aliens
                if abs(alien.coords['x'] - bullet.coords['x']) < 1 and abs(alien.coords['y'] - bullet.coords['y']) < 1: # Check if a bullet is on the same cell as an alien
                    if alien.level > 1:
                        alien.LowerLevel()
                    else:
                        aliens.remove(alien) # Kill alien
                    bullets.remove(bullet) # Remove bullet
                    game.Score += 10 # 10 points Gryffindor!!!                                
                    break

        #Check if bullet is in range of barricades
        elif bullet.coords['y'] > 38 and bullet.coords['y'] < 44:
            for barricade in barricades: # Loop through all the barricades
                if abs(barricade.coords['x'] - bullet.coords['x']) < 1 and abs(barricade.coords['y'] - bullet.coords['y']) == 0: # Check if a bullet is on the same cell as a barricade part
                    barricades.remove(barricade) # remove barricade
                    bullets.remove(bullet) # Remove bullet
                    break

        #Check if bullet is in range of player
        elif bullet.coords['y'] == 45:            
            if abs((playerCoords['x'] + 1) - bullet.coords['x']) <= 1: # Check if a bullet is on the same cell as the player
                PlayerHasBeenHit()
                break 

def CreateBarricades():
    barricades.clear()
    x = 1
    while x < 70:
        # God this is ugly
        barricades.append(Barricade(1,{'x': x + 2, 'y': 43}, WHITE))
        barricades.append(Barricade(1,{'x': x + 2, 'y': 42}, WHITE))
        barricades.append(Barricade(1,{'x': x + 2, 'y': 41}, WHITE))
        barricades.append(Barricade(1,{'x': x + 2, 'y': 40}, WHITE))
        barricades.append(Barricade(1,{'x': x + 3, 'y': 42}, WHITE))
        barricades.append(Barricade(1,{'x': x + 3, 'y': 41}, WHITE))
        barricades.append(Barricade(1,{'x': x + 3, 'y': 40}, WHITE))
        barricades.append(Barricade(1,{'x': x + 3, 'y': 39}, WHITE))
        barricades.append(Barricade(1,{'x': x + 4, 'y': 42}, WHITE))
        barricades.append(Barricade(1,{'x': x + 4, 'y': 41}, WHITE))
        barricades.append(Barricade(1,{'x': x + 4, 'y': 40}, WHITE))
        barricades.append(Barricade(1,{'x': x + 4, 'y': 39}, WHITE))
        barricades.append(Barricade(1,{'x': x + 5, 'y': 42}, WHITE))
        barricades.append(Barricade(1,{'x': x + 5, 'y': 41}, WHITE))
        barricades.append(Barricade(1,{'x': x + 5, 'y': 40}, WHITE))
        barricades.append(Barricade(1,{'x': x + 5, 'y': 39}, WHITE))
        barricades.append(Barricade(1,{'x': x + 6, 'y': 43}, WHITE))
        barricades.append(Barricade(1,{'x': x + 6, 'y': 42}, WHITE))
        barricades.append(Barricade(1,{'x': x + 6, 'y': 41}, WHITE))
        barricades.append(Barricade(1,{'x': x + 6, 'y': 40}, WHITE))        

        x += 9

def PlayerHasBeenHit():
    global game
    game.Lives -= 1                    
    game.GameOver = True    
    game.WinStatus = False

if __name__ == '__main__':
    main()