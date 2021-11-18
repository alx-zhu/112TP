from cmu_112_graphics import *
import random
import copy
import math

################################################################################
##############################  PLAYER CLASS  ##################################
################################################################################

class Player(object):
    def __init__(self, app):
        #stats
        self.hp = 100
        self.armor = 0
        self.bonusDmg = 0
        self.walkSpeed = 1000
        #items/weapons
        self.weapon = BasicWeapon()
        #starting position
        self.cw = 20
        self.ch = 20
        self.cx = self.cw + self.cw
        self.cy = app.height - self.ch
        #velocity
        self.vy = 0
        self.vx = 0
        self.direction = 1
        #gravity
        self.g = 250
        #jump
        self.jumpAccel = -2500
        #acceleration
        self.ax = 0
        self.ay = 0
        #bools and other checks
        self.jumps = 2
        self.isJumping = False
        self.isFalling = False
    
    def aboveOrBelowPlatform(self, x1, x2, leftEdge, rightEdge):
        if leftEdge < x2 and rightEdge > x1:
            return True
        return False

    def moveCharY(self, app, dy):
        leftEdge = self.cx - self.cw
        rightEdge = self.cx + self.cw
        bottomEdge = self.cy + self.ch
        topEdge = self.cy - self.ch
        #for debugging falling
        for x1, y1, x2, y2 in app.platforms:
            if ((bottomEdge + dy > y1) and (topEdge < y1) and 
                    self.aboveOrBelowPlatform(x1, x2, leftEdge, rightEdge)):
                self.jumps = 2
                self.cy = y1 - self.ch
                self.isFalling = False
                self.vy = 0
                return
            #if below a platform and topEdge will go through, collide
            if((topEdge + dy < y2) and (bottomEdge > y2) and
                self.aboveOrBelowPlatform(x1, x2, leftEdge, rightEdge)):
                #if you hit the bottom of a platform stop moving, and fall.
                #set dy to 0 so the position does not update.
                self.cy = y2 + self.ch
                self.vy = 0
                dy = 0
                self.isFalling = True
        if self.isFalling or self.isJumping:
            self.cy += dy
        else:
            self.isFalling = True
            #print("I am Falling")
        #print(f"Jumping: {app.isJumping}, Falling: {app.isFalling}")

    def nextToPlatform(self, y1, y2, topEdge, bottomEdge):
        #if (y1 > topEdge and y1 < bottomEdge) or (y2 < bottomEdge and y2 > topEdge):
        if (((topEdge < y2 and topEdge > y1) or 
            (bottomEdge > y1 and bottomEdge < y2)) or
            ((y1 > topEdge and y1 < bottomEdge) or 
            (y2 < bottomEdge and y2 > topEdge))):
            return True
        return False 

    def moveCharX(self, app, dx):
        leftEdge = self.cx - self.cw
        rightEdge = self.cx + self.cw
        bottomEdge = self.cy + self.ch
        topEdge = self.cy - self.ch
        for x1, y1, x2, y2 in app.platforms:
            #print(nextToPlatform(y1, y2, topEdge, bottomEdge))
            if (self.nextToPlatform(y1, y2, topEdge, bottomEdge) and 
                ((rightEdge + dx >= x1 and leftEdge < x1) or 
                (leftEdge + dx <= x2 and rightEdge > x2))):
                #if on the left of a platform, stop right when the right side
                #touches, and vice versa
                if rightEdge <= x1:
                    self.cx = x1 - self.cw
                elif leftEdge >= x2:
                    self.cx = x2 + self.cw
                self.vx = 0
                dx = 0
                self.ax = 0
        self.cx += dx
        #if canMove: self.cx += dx

    def jump(self):
        if self.jumps > 0:
            self.vy = self.jumpAccel
            self.jumps -= 1

    def checkIfOffScreenAndUpdateRoom(self, app):
        roomRow, roomCol = app.currentRoom
        if (roomRow, roomCol) not in app.visited:
            app.visited.add((roomRow, roomCol))
        if self.cx < app.leftBorder:
            roomRow, roomCol = app.currentRoom
            roomCol -= 1
            app.currentRoom = (roomRow, roomCol)
            #update position
            self.cx = app.width - self.cw - 10
            loadRoom(app, roomRow, roomCol)
        elif self.cx > app.width:
            roomCol += 1
            app.currentRoom = (roomRow, roomCol)
            #update position
            self.cx = app.leftBorder + self.cw + 10
            #load new room
            loadRoom(app, roomRow, roomCol)
        elif self.cy < 0:
            roomRow -= 1
            app.currentRoom = (roomRow, roomCol)
            #update position
            self.cy = app.height - self.cw - 10
            loadRoom(app, roomRow, roomCol)
        elif self.cy > app.height:
            roomRow += 1
            app.currentRoom = (roomRow, roomCol)
            #update position
            self.cy = self.cw + 10
            loadRoom(app, roomRow, roomCol)
    
    def attack(self, app):
        #fire a projectile at the character's height
        speed = self.weapon.speed
        dmg = self.weapon.dmg + self.bonusDmg
        size = self.weapon.size
        color = self.weapon.color
        cx = self.cx + self.direction*self.cw
        app.projectiles.append(Projectile(speed, dmg, self.direction, 
                            cx, self.cy, size, color))

################################################################################
#########################  WEAPON/PROJECTILE CLASSES  ##########################
################################################################################
class Projectile(object):
    def __init__(self, speed, dmg, direction, xi, yi, size, color):
        self.speed = speed
        self.dmg = dmg
        self.direction = direction
        self.x = xi
        self.y = yi
        self.size = size

    def moveX(self, app):
        if self.x - self.speed < app.leftBorder or self.x + self.speed > app.width:
            self.destroy(app)
        else:
            for monster in app.monsters:
                if math.dist((self.x + self.direction*self.speed, self.y), 
                            (monster.cx, monster.cy)) < monster.cw + self.size:
                    self.destroy(app)
                    monster.takeDamage(app, self.dmg)

        if self.direction == 1:
            self.x += self.speed
        else:
            self.x -= self.speed

    def destroy(self, app):
        app.projectiles.remove(self)

#Each weapon has these stats predefined
class Weapon(object):
    def __init__(self, speed, dmg, reload, color):
        self.speed = speed
        self.dmg = dmg
        self.reload = reload
        self.color = color

class BasicWeapon(Weapon):
    def __init__(self):
        self.speed = 30
        self.dmg = 10
        self.reload = 10
        self.size = 6
        self.color = "yellow"

    

################################################################################
###############################  MONSTER CLASS  ################################
################################################################################

class Monster(object):
    def __init__(self, app, hp, dmg, cx, cy):
        self.hp = hp
        self.dmg = dmg
        self.walkSpeed = 1000
        #starting position
        self.cw = 20
        self.ch = 20
        self.cx = cx
        self.cy = cy - 4*self.ch
        #velocity
        self.vy = 0
        self.vx = int(600*random.random())
        #x-component of unit vector
        randDir = [-1, 1]
        self.direction = randDir[random.randint(0, 1)]
        #gravity
        self.g = 250
        #bools and other checks
        self.isJumping = False
        self.isFalling = False

    def aboveOrBelowPlatform(self, x1, x2, leftEdge, rightEdge):
        if leftEdge < x2 and rightEdge > x1:
            return True
        return False

    def moveY(self, app, dy):
        leftEdge = self.cx - self.cw
        rightEdge = self.cx + self.cw
        bottomEdge = self.cy + self.ch
        topEdge = self.cy - self.ch
        for x1, y1, x2, y2 in app.platforms:
            if ((bottomEdge + dy > y1) and (topEdge < y1) and 
                    self.aboveOrBelowPlatform(x1, x2, leftEdge, rightEdge)):
                self.cy = y1 - self.ch
                self.isFalling = False
                self.vy = 0
                return
        if self.isFalling:
            self.cy += dy
        else:
            self.isFalling = True

    def nextToPlatform(self, y1, y2, topEdge, bottomEdge):
        #if (y1 > topEdge and y1 < bottomEdge) or (y2 < bottomEdge and y2 > topEdge):
        if (((topEdge < y2 and topEdge > y1) or 
            (bottomEdge > y1 and bottomEdge < y2)) or
            ((y1 > topEdge and y1 < bottomEdge) or 
            (y2 < bottomEdge and y2 > topEdge))):
            return True
        return False 

    def moveX(self, app, dx):
        leftEdge = self.cx - self.cw
        rightEdge = self.cx + self.cw
        bottomEdge = self.cy + self.ch
        topEdge = self.cy - self.ch
        for x1, y1, x2, y2 in app.platforms:
            if (self.nextToPlatform(y1, y2, topEdge, bottomEdge) and 
                ((rightEdge + dx >= x1 and leftEdge < x1) or 
                (leftEdge - dx <= x2 and rightEdge > x2))):
                #print(f"TOUCHING A PLATFORM, leftEdge = {leftEdge}, x2 = {x2}")
                #if on the left of a platform, stop right when the right side
                #touches, and vice versa
                if rightEdge <= x1:
                    self.cx = x1 - self.cw - 5
                    self.direction = -1
                    #print("here")
                if leftEdge >= x2:
                    self.cx = x2 + self.cw + 5
                    self.direction = 1
                #self.vx = 0
        if self.direction == 1:
            self.cx += dx
        elif self.direction == -1:
            self.cx -= dx

    def takeDamage(self, app, dmg):
        self.hp -= dmg
        if self.hp <= 0:
            app.monsters.remove(self)

#outside of class
def spawnMonster(app, row, col):
        x1, y1, x2, y2 = getCellBounds(app, row, col)
        #place a monster at center of platform
        cx = x1 + (x2-x1)/2
        cy = y2
        return Monster(app, 100, 10, cx, cy)


################################################################################
###############################  MAZE GENERATOR  ###############################
################################################################################

#Original source: https://medium.com/swlh/fun-with-python-1-maze-generator-931639b4fb7e
#Code modified greatly, but original structure is based on the website

def printMaze(maze):
    p, w, u = 0, 1, -1
    for i in range(0, len(maze)):
        for j in range(0, len(maze[0])):
            if maze[i][j] == u:
                print(f'{maze[i][j]}', end = ' ')
            else:
                print(f' {maze[i][j]}', end = ' ')
        print()

def mazeToString(maze):
    p, w, u = 0, 'w', -1
    s = ""
    for i in range(0, len(maze)):
        for j in range(0, len(maze[0])):
            if maze[i][j] == u:
                s += f'{maze[i][j]} '
            else:
                s += f' {maze[i][j]} '
        s+='\n'
    return s

def checkSurr(maze, row, col):
    p, w, u = 0, 'w', -1
    total = 0
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    for drow, dcol in directions:
        newRow, newCol = row+drow, col+dcol
        if maze[newRow][newCol] == p:
            total += 1
    return total

def updateSurr(maze, walls, seen, row, col):
    p, w, u = 0, 'w', -1
    #m = copy.deepcopy(maze)
    rows = len(maze)
    cols = len(maze[0])
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    for drow, dcol in directions:
        newRow, newCol = row+drow, col+dcol
        if maze[newRow][newCol] == u:
            maze[newRow][newCol] = w
            #only add if wall isnt already in the list and it isnt an edge
            if((newRow, newCol) not in seen 
                and newRow > 0 and newRow < rows-1 
                and newCol > 0 and newCol < cols-1):
                walls.append((newRow, newCol))
                seen.add((newRow, newCol))
    return maze, walls

def fillInWalls(maze, rows, cols):
    p, w, u = 0, 'w', -1
    #m = copy.deepcopy(maze)
    for i in range(rows):
        for j in range(cols):
            #if there are any unchecked cells left, make them into walls
            if maze[i][j] == u:
                maze[i][j] = w
    return maze

def createEnterAndExit(maze, rows, cols):
    p, w, u = 0, 'w', -1
    #to make the entrance, search for the first point on edge that can 
    #enter into the maze
    for i in range(cols):
        if maze[1][i] == p:
            maze[0][i] = p
            break
    #vice versa for exit
    for i in range(cols-1, 0, -1):
        if maze[rows-2][i] == p:
            maze[rows-1][i] = p
            break
    return maze

def randomizeRooms(app, maze, rows, cols):
    p, w, u = 0, 'w', -1
    for i in range(rows):
        for j in range(cols):
            if maze[i][j] == p:
                maze[i][j] = random.randint(0, len(app.layouts)-1)
    return maze

def createMaze(app, rows, cols):
    maze = [[-1]*cols for row in range(rows)]
    walls = []
    #for searching for already seen
    seen = set()
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    #p is path, w is wall, u is unchecked
    p, w, u = 0, 'w', -1
    #cannot be on the edges of the maze (row 0, or rows)
    startRow = random.randint(1, rows-2)
    startCol = random.randint(1, cols-2)
    maze[startRow][startCol] = p
    #add the walls around this start point and set those points in the
    #maze to be walls
    for drow, dcol in directions:
        newRow, newCol = startRow + drow, startCol + dcol
        #do not add edges
        if newRow > 0 and newRow < rows-1 and newCol > 0 and newCol < cols-1:            
            walls.append((newRow,newCol))
            seen.add((newRow, newCol))
            maze[newRow][newCol] = w
    #while there are still walls to pick from, keep generating
    while len(walls) > 0:
        rWall = walls[random.randint(0, len(walls)-1)]
        wallRow = rWall[0]
        wallCol = rWall[1]
        #check the spots adjacent to the wall. If only one of them
        #has been visited before, and the other is a path, make the wall into 
        # a path
        for drow, dcol in directions:
            newRow, newCol = wallRow+drow, wallCol+dcol
            #checks the opposite direciton
            oppRow, oppCol = wallRow-drow, wallCol-dcol
            #one side of the wall is unchecked, the other side is a path
            if maze[newRow][newCol] == u and maze[oppRow][oppCol] == p:
                if checkSurr(maze, wallRow, wallCol) < 2:
                    maze[wallRow][wallCol] = p
                    #updates the maze, as well as the list of walls
                    maze, walls = updateSurr(maze, walls, seen, 
                                            wallRow, wallCol)
                    #walls.remove(rWall)
        #remove the wall after all checks are done. It is either now a path, or
        #is not a valid wall to change
        walls.remove(rWall)
        seen.remove(rWall)
    maze = fillInWalls(maze, rows, cols)
    maze = createEnterAndExit(maze, rows, cols)
    maze = randomizeRooms(app, maze, rows, cols)
    return maze

################################################################################
####################################  ROOM  ####################################
################################################################################

#creates the walls and floors necesarry for a room based on the rooms around it
def getWallsAndFloors(app, left, right, up, down):
    wallsAndFloors = []
    #left, right, up and down tell where the doors are.
    #will return a list of the coordinates of the walls.
    if left == True:
        wallsAndFloors.append((app.leftBorder, 0, app.leftBorder + 10, 
                        app.height/2 - 80))
        wallsAndFloors.append((app.leftBorder, app.height/2 + 80, 
                        app.leftBorder + 10, app.height))
    else: 
        wallsAndFloors.append((app.leftBorder, 0, app.leftBorder + 10, app.height))
    
    if right == True:
        wallsAndFloors.append((app.width-10, 0, app.width, app.height/2 - 80))
        wallsAndFloors.append((app.width-10, app.height/2 + 80, 
                                app.width, app.height))
    else:
        wallsAndFloors.append((app.width-10, 0, app.width, app.height))
    
    if up == True:
        wallsAndFloors.append((app.leftBorder, 0, 
                    app.leftBorder + app.gameWidth/2 - 80, 10))
        wallsAndFloors.append((app.leftBorder + app.gameWidth/2 + 80, 
                    0, app.width, 10))
    else:
        wallsAndFloors.append((app.leftBorder, 0, app.width, 10))
    
    if down == True:
        wallsAndFloors.append((app.leftBorder, app.height-20, 
                    app.leftBorder + app.gameWidth/2 - 80, app.height))
        wallsAndFloors.append((app.leftBorder + app.gameWidth/2 + 80, 
                    app.height-20, app.width, app.height))
    else:
        wallsAndFloors.append((app.leftBorder, app.height-20, app.width, app.height))
    return wallsAndFloors

def isLegal(app, row, col):
    if row < 0 or row >= len(app.map) or col < 0 or col >= len(app.map[0]):
        return False
    elif app.map[row][col] == 'w':
        return False
    else:
        return True

#makes the room with openings based on the rooms around them
def loadRoom(app, roomRow, roomCol):
    directions = [(0, -1), (0, 1), (1, 0), (-1, 0)]
    left = right = up = down = False
    for d in directions:
        drow, dcol = d
        row = roomRow + drow
        col = roomCol + dcol
        #tells which directions there are more rooms
        if isLegal(app, row, col):
            if drow == -1:
                up = True
            elif drow == 1:
                down = True
            elif dcol == -1:
                left = True
            elif dcol == 1:
                right = True
    #make the walls and floors
    app.platforms = getWallsAndFloors(app, left, right, up, down)
    #rooms will have randomized layouts generated by the maze initially
    layout = app.layouts[app.map[app.currentRoom[0]][app.currentRoom[1]]]
    #converts row cols into coordinates and combines long platforms
    combinedPlatforms = combinePlatforms(app, layout)
    #make the platforms
    '''for row, col in app.platRowCols:
        x1, y1, x2, y2 = getCellBounds(app, row, col)
        app.platforms.append((x1, y2-app.platformHeight, x2, y2))'''
    app.platforms.extend(combinedPlatforms)
    #spawn one monster on each platform (each platform is at least 2 grids long)
    app.monsters = []
    for i in range(0, len(layout), 3):
        #print(row, col)
        row, col = layout[i]
        app.monsters.append(spawnMonster(app, row, col))

#combines platforms since the long platformsa are actually 2 or 3 platforms
#put together. 
#May not be used in final game. Just to easily create new room layouts without
#having to calculate the x and y coordinates.
def combinePlatforms(app, rowColsList):
    plats = copy.copy(rowColsList)
    previous = plats[0]
    plats = plats[1:]
    #returns a list of lists of the combined platforms in format:
    #[[row, col, row, col, row, col], [row, col, row, col], etc.]
    combinedPlatformsRowCol = combinePlatsHelper(app, previous, plats, 
                                    [previous[0], previous[1]], [])
    print(combinedPlatformsRowCol)
    #makes each list of row, col, row, col into a single tuple of 
    # (x1, y1, x2, y2)
    combinedPlatforms = convertToXYCoords(app, combinedPlatformsRowCol)
    return combinedPlatforms

#combines adjacent platforms by storing them in lists, [row, col, row, col, etc]
#Stores these combined platforms in combinedList. They will then be changed to
#be only one platform later using getCellBounds
def combinePlatsHelper(app, previous, uncombined, combinedPlat, combinedList):
    if uncombined == []:
        if len(combinedPlat) != 0:
            combinedList.append(combinedPlat)
        return combinedList
    else:
        current = uncombined[0]
        currRow = current[0]
        currCol = current[1]
        #print(currRow, currCol, combinedPlat)
        prevRow = previous[0]
        prevCol = previous[1]
        #if they are in the same row, and adjacent cols, add to the combined
        #Tuple. Otherwise, add the combinedPlat to combinedList if it is not
        #empty. then empty the combinedPlat
        if currRow == prevRow and abs(currCol - prevCol) == 1:
            combinedPlat.append(currRow)
            combinedPlat.append(currCol)
        else:
            #if combinedPlat is actually a platform, add it to the list
            if len(combinedPlat) > 0:
                combinedList.append(combinedPlat)
                #now set combinedPlat to the new platform. The old platform
                #was just added to the list.
                combinedPlat = [currRow, currCol]
        return combinePlatsHelper(app, current, uncombined[1:], 
                                    combinedPlat, combinedList)

def convertToXYCoords(app, rowColList):
    xyCoordsList = []
    for platform in rowColList:
        #use the first and last platform to get dimensions for entire platform
        #only using x1 of first, and x2 and y2 of last platform
        x1, a, b, c = getCellBounds(app, platform[0], platform[1])
        a, b, x2, y2 = getCellBounds(app, platform[-2], platform[-1])
        xyCoordsList.append((x1, y2 - app.platformHeight, x2, y2))
    return xyCoordsList


################################################################################
###################################  GRID  #####################################
################################################################################

def getCell(app, x, y):
    gridWidth  = app.gameWidth - 2*app.margin
    gridHeight = app.height - 2*app.margin
    cellWidth  = gridWidth / app.cols
    cellHeight = gridHeight / app.rows
    row = int((y - app.margin) / cellHeight)
    col = int((x - app.margin) / cellWidth)
    return (row, col)

def getCellBounds(app, row, col):
    gridWidth  = app.gameWidth
    gridHeight = app.height
    cellWidth = gridWidth / app.cols
    cellHeight = gridHeight / app.rows
    x0 = app.margin + app.leftBorder + col * cellWidth
    x1 = app.margin + app.leftBorder + (col+1) * cellWidth
    y0 = app.margin + row * cellHeight
    y1 = app.margin + (row+1) * cellHeight
    return (x0, y0, x1, y1)

def drawGrid(app, canvas):
    for row in range(app.rows):
        for col in range(app.cols):
            (x0, y0, x1, y1) = getCellBounds(app, row, col)
            canvas.create_rectangle(x0, y0, x1, y1)
            midX = (x1-x0)/2
            midY = (y1-y0)/2
            canvas.create_text(x0 + midX, y0 + midY - 15, 
                    text = f"({row},{col})", font = "Arial 15", anchor = "n")

################################  Minimap Grid  ################################

def mapCellBounds(app, row, col):
    width = app.mapWidth
    height = app.mapWidth
    cellWidth = width/app.mapRows
    cellHeight = width/app.mapCols
    x0 = app.mapMargin + col * cellWidth
    x1 = app.mapMargin + (col+1) * cellWidth
    y0 = (app.height - height - app.mapMargin) + row * cellHeight
    y1 = (app.height - height - app.mapMargin) + (row+1) * cellHeight
    return (x0, x1, y0, y1)

def drawMapGrid(app, canvas):
    for row in range(app.mapRows):
        for col in range(app.mapCols):
            x0, x1, y0, y1 = mapCellBounds(app, row, col)
            if (row, col) == app.currentRoom:
                canvas.create_rectangle(x0, y0, x1, y1, fill = "red",
                outline = "red")
            elif (row, col) in app.visited:
                canvas.create_rectangle(x0, y0, x1, y1, fill = "white",
                outline = "white")
            else:
                canvas.create_rectangle(x0, y0, x1, y1, fill = "black",
                    outline = "red")



################################################################################
################################  CMU GRAPHICS  ################################
################################################################################

def appStarted(app):
    app.player = Player(app)
    app.monsters = []
    #grid
    app.rows = 10
    app.cols = 10
    app.leftBorder = 300
    app.gameWidth = app.width-app.leftBorder
    app.margin = 0
    app.mapMargin = 50
    app.mapWidth = 200
    #other
    app.timerDelay = 50
    #starting position
    app.player.cx = app.leftBorder + app.player.cw + 20
    app.player.cy = app.height - app.player.ch
    app.g = 250
    #list of platforms
    app.platformHeight = 20
    app.floor = (0, app.height - 20, app.width, app.height)
    app.layouts = [
                    #layout 0
                    [ (8, 1), (8, 2), 
                      (7, 4), (7, 5), 
                      (5, 8), (5, 9), 
                      (5, 0), (5, 1),
                      (3, 4), (3, 5), (3, 6), 
                      (2, 0), (2, 1),
                      (1, 4), (1, 5), 
                      (1, 8), (1, 9),
                      (8, 7), (8, 8), (8, 9) ],

                    #layout 1
                    [ (7, 2), (7, 3), (7, 4),
                      (8, 6), (8, 7),
                      (5, 6), (5, 7), (5, 8), (5, 9),
                      (4, 2), (4, 3),
                      (3, 8), (3, 9),
                      (2, 0), (2, 1), (2, 2),
                      (1, 5), (1, 6), (1, 7),
                      (5, 0)                
                    ],

                    #layout 2
                    [ (5, 0),
                      (5, 9),
                      (5, 3), 
                      (5, 6), 
                      (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7),
                      (3, 2), (3, 3), (3, 4), (3, 5),
                      (2, 8), (2, 9),
                      (1, 1), (1, 2), (1, 3), (1, 4), (1, 5)
                    ]
                ]
    app.platforms = []
    #map
    app.showMap = False
    app.mapRows = 8
    app.mapCols = app.mapRows
    app.map = createMaze(app, 8, 8)
    app.currentRoom = ()
    app.visited = set()
    #find the entrance
    for col in range(len(app.map[0])):
        if app.map[0][col] != 'w':
            app.currentRoom = (0, col)
            break
    app.visited.add(app.currentRoom)
    loadRoom(app, app.currentRoom[0], app.currentRoom[1])
    app.projectiles = []

############################### Draw Functions #################################

def drawChar(app, canvas):
    canvas.create_rectangle(app.player.cx - app.player.cw, 
                            app.player.cy - app.player.ch, 
                            app.player.cx + app.player.cw, 
                            app.player.cy + app.player.ch, fill = "black")
    if app.player.direction == 1:
        cx = app.player.cx + app.player.cw
        cy = app.player.cy
        canvas.create_rectangle(cx-5, cy-5, cx+10, cy+5, fill = app.player.weapon.color)
    else:
        cx = app.player.cx - app.player.cw
        cy = app.player.cy
        canvas.create_rectangle(cx-10, cy-5, cx+5, cy+5, fill = app.player.weapon.color)

def drawPlatforms(app, canvas):
    for x1, y1, x2, y2 in app.platforms:
        canvas.create_rectangle(x1, y1, x2, y2, fill = "black")

def drawMonsters(app, canvas):
    for monster in app.monsters:
        x = monster.cx
        y = monster.cy
        canvas.create_rectangle(x - monster.cw, y - monster.ch,
                                x + monster.cw, y + monster.cw, fill = "red")

def drawFloor(app, canvas):
    canvas.create_rectangle(0, app.height-10, app.width, app.height)

def drawMinimap(app, canvas):
    drawMapGrid(app, canvas)

def drawProjectiles(app, canvas):
    for proj in app.projectiles:
        canvas.create_oval(proj.x-proj.size, proj.y-proj.size, 
                    proj.x+proj.size, proj.y+proj.size, fill = app.player.weapon.color)

######################## Built-in Controller Functions #########################

def keyPressed(app, event):
    if event.key == "Left":
        app.player.vx = -1 * app.player.walkSpeed
        app.player.ax = 0
        app.player.movingX = True
        app.player.direction = -1
    elif event.key == "Right":
        app.player.vx = app.player.walkSpeed
        app.player.ax = 0
        app.player.movingX = True
        app.player.direction = 1
    elif event.key == "Up":
        app.player.isJumping = True
        app.player.jump()
    elif event.key == "r":
        appStarted(app)
    elif event.key == "m":
        if app.showMap:
            app.showMap = False
        else:
            app.showMap = True
    elif event.key == "Space":
        app.player.attack(app)

def keyReleased(app, event):
    #if the right or left key is released while on the ground, decelerate.
    if event.key == "Left":
        app.player.ax = app.player.walkSpeed*0.2
    elif event.key == "Right":
        app.player.ax = app.player.walkSpeed*-0.2
    elif event.key == "Up":
        app.player.isFalling = True
        app.player.isJumping = False

def timerFired(app):
    coeff = 0.01 #allows numbers to stay as integers

    #player movement
    if app.player.isFalling:
        app.player.vy += app.g
    app.player.moveCharY(app, app.player.vy*coeff)
    app.player.moveCharX(app, app.player.vx*coeff)
    if app.player.vx == 0:
        app.player.movingX = False
        app.player.ax = 0
    app.player.vx += app.player.ax
    app.player.checkIfOffScreenAndUpdateRoom(app)

    #monster movement
    for monster in app.monsters:
        if monster.isFalling:
            monster.vy += app.g
        monster.moveY(app, monster.vy*coeff)
        monster.moveX(app, monster.vx*coeff)

    #projectile movement
    for proj in app.projectiles:
        proj.moveX(app)

def redrawAll(app, canvas):
    #drawGrid(app, canvas)
    drawPlatforms(app, canvas)
    drawChar(app, canvas)
    drawMonsters(app, canvas)
    drawProjectiles(app, canvas)
    if app.showMap:
        drawMinimap(app, canvas)
    else:
        canvas.create_rectangle(2*app.mapMargin, (app.height - app.mapWidth/2 - 2*app.mapMargin),
                    2*app.mapMargin + app.mapWidth/2,
                    (app.height - 2*app.mapMargin),
                    fill = "black", outline = "red")
        canvas.create_text(app.mapMargin + app.mapWidth/2,
                            app.height - app.mapWidth/2 - app.mapMargin - 25, 
                            text = "Press 'm' to\n    toggle\n  minimap",
                            font = "Arial 10 bold",
                            fill = "white",
                            anchor = "n")
    canvas.create_text(app.leftBorder + app.gameWidth/2, app.height/2 - 30, 
        text = f"Room: ({app.currentRoom[0]},{app.currentRoom[1]})",
        font = "Arial 20")
    #canvas.create_text(app.leftBorder + app.gameWidth/2, app.height/2, 
    #    text = mazeToString(app.map), 
    #    font = "Arial 10",
    #    anchor = "n")

runApp(width = 1100, height = 800)