"""
==================================================================================================
Program Name: PiPicaria

Description: This program implements a graphical user interface (GUI) version of the traditional 
             game Picaria. Picaria is a two-player abstract strategy game played on a small grid.
             Players take turns moving their pieces with the goal of forming a straight line of 
             three pieces, either horizontally, vertically, or diagonally.

Author: [Your Name]

Last Edited: [Last Edited Date]

==================================================================================================
"""

import pygame
from pygame.locals import *
import socket
import math, sys, os

pygame.init()

# GUI Code
guiSize = 800, 800
pRad = 65
gui = pygame.display.set_mode(guiSize)
board = Rect(100, 100, 600, 600)

# Initialization code
UDP_PORT = 5005
setupDone = False  # checks to see if ip and color is entered

# Game Code
grid = [[0, 0, 0],
        [0, 0, 0],
        [0, 0, 0]]
selectGrid = [[0, 0, 0],
              [0, 0, 0],
              [0, 0, 0]]
pieceCounter = 0  # keeps track of the board pieces
turnCounter = 0  # keeps track of the turn, user can only act when %2=0
piecesCoords = None, None  # used to translate array coords to gui coords
coordPicked = False  # this is the boolean for choosing a coord to place
coordSelected = False  # this is the boolean for choosing a coord to select
coordDeselected = False  # this is the boolean for if a coord is deselected
x, y = None, None  # these are the placing coords
sX, sY = None, None  # these are the coords of selected pieces
dX, dY = None, None # these are the coords of the desected pieces (basically used as a check)
vX, vY = None, None  # variable coordinates, always get the coords
lastMoveCoords = x, y
newSelectedCoords = vX, vY
validMove = None  # checks to see if the move is valid
selectedColor = None  # stores the color of selected coords
chosenColor = 1  # None # stores the user's color
moveStart = False
firstSelect = 0  # tracks if it is the first valid select
firstDeselect = 0  # tracks if it is the first valid deselect
firstPick = 0  # tracks if it is the first valid pick

# Mapping variables
A1 = 100, 100
A2 = 400, 100
A3 = 700, 100
B1 = 100, 400
B2 = 400, 400
B3 = 700, 400
C1 = 100, 700
C2 = 400, 700
C3 = 700, 700

def setup():
    global turnCounter, playerName, UDP_IP1, UDP_IP2, setupDone
    UDP_IP1 = input("Enter your IP: ")  # the user's ip
    UDP_IP2 = input("Enter your opponents IP: ")  # the opponent's ip
    playerName = input("Choose red or blue: ")  # player name is used to set turncounter
    while (playerName != "Red" and playerName != "Blue" and
           playerName != "RED" and playerName != "BLUE" and
           playerName != "red" and playerName != "blue" and
           playerName != "r" and playerName != "b"):
        playerName = input("Not an option, choose red or blue: ")  # checks valid color

    if (playerName == "Red" or playerName == "RED" or
            playerName == "red" or playerName == "r"):
        turnCounter = 0  # player can only input on %2=0, so if red goes first, start at 0
        setupDone = True
    elif (playerName == "Blue" or playerName == "BLUE" or
          playerName == "blue" or playerName == "b"):
        turnCounter = 1  # player can only input on %2=0, so if blue goes second, start at 1
        setupDone = True


def baseBoard():
    gui.fill('black')
    # pygame.draw.[SHAPE](SURFACE, COLOR, COORDS/POS, THICKNESS)
    pygame.draw.rect(gui, 'white', board, 5)
    pygame.draw.line(gui, 'white', (105, 105), (695, 695), 7)
    pygame.draw.line(gui, 'white', (105, 695), (695, 105), 7)
    pygame.draw.line(gui, 'white', (400, 105), (400, 695), 5)
    pygame.draw.line(gui, 'white', (105, 400), (695, 400), 5)
    pygame.draw.line(gui, 'white', (105, 400), (400, 695), 7)
    pygame.draw.line(gui, 'white', (400, 695), (695, 400), 7)
    pygame.draw.line(gui, 'white', (400, 105), (695, 400), 7)
    pygame.draw.line(gui, 'white', (400, 105), (105, 400), 7)


def drawPieces():  # draws the main grid pieces
    global piecesCoords, r, c, coordPicked, coordSelected, coordDeselected, validMove, turnCounter, pieceCounter

    for r in range(3):
        for c in range(3):
            if grid[r][c] == 1:  # draws a circle where there are red pieces (1)
                mapCoords()
                pygame.draw.circle(gui, 'red', piecesCoords, pRad)
            if grid[r][c] == 2:  # draws a circle where there are blue pieces (2)
                mapCoords()
                pygame.draw.circle(gui, 'blue', piecesCoords, pRad)

    if coordPicked is True:  # only increments the counter if a coord is picked
        pieceCounter += 1
        #turnCounter += 1
        coordPicked = False  # sets it to false after placing


def highlightPieces():
    global r, c, piecesCoords

    drawPieces()

    for r in range(3):
        for c in range(3):
            if selectGrid[r][c] == 1:  # draws a circle where there are red pieces (1)
                mapCoords()
                pygame.draw.circle(gui, 'yellow', piecesCoords, pRad)


def mapCoords():  # maps the grid array to the gui coords
    global piecesCoords, r, c

    if r == 0 and c == 0:
        piecesCoords = A1
    elif r == 0 and c == 1:
        piecesCoords = A2
    elif r == 0 and c == 2:
        piecesCoords = A3
    elif r == 1 and c == 0:
        piecesCoords = B1
    elif r == 1 and c == 1:
        piecesCoords = B2
    elif r == 1 and c == 2:
        piecesCoords = B3
    elif r == 2 and c == 0:
        piecesCoords = C1
    elif r == 2 and c == 1:
        piecesCoords = C2
    elif r == 2 and c == 2:
        piecesCoords = C3


def placeCoords():  # gets x and y
    global coordPicked, vX, vY, x, y, pieceCounter, UDP_IP1, UDP_IP2, UDP_PORT, firstPick

    vY, vX = pygame.mouse.get_pos()
    vX = int(vX / (800 / 3))
    vY = int(vY / (800 / 3))
    if pygame.mouse.get_pressed()[0] and grid[vX][vY] == 0 and coordPicked is False: # and turnCounter % 2 == 0:  # to place pieces
        firstPick += 1
        if firstPick == 1:
            x = vX
            y = vY
            coordPicked = True
            print("xy", x, y)
            print(coordPicked)

    # elif turnCounter % 2 == 1:
        # receive code

def getCoords():  # gets selected x and selected y
    global coordSelected, vX, vY

    # if (turnCounter % 2 == 0):
    vY, vX = pygame.mouse.get_pos()
    vX = int(vX / (800 / 3))
    vY = int(vY / (800 / 3))
        # send coords
    # elif (turnCounter % 2 == 1):
        # receive code

def checkValid():
    global coordPicked, coordSelected, coordDeselected, x, y, sX, sY, pieceCounter, validMove, firstSelect, firstPick

    if coordPicked and coordSelected:
        if abs(int(x) - int(sX)) > 1 or abs(int(y) - int(sY)) > 1:
            validMove = False
            coordPicked = False
            firstPick = 0
        else:
            validMove = True
            firstSelect = 0
            firstPick = 0
        print(coordPicked, coordSelected, coordDeselected, validMove)


def updateGrids():
    global x, y, sX, sY, turnVar, selectedColor, coordPicked, coordSelected, \
        coordDeselected, validMove, pieceCounter, firstSelect, firstPick

    if pieceCounter < 6:
        if coordPicked:
            firstPick = 0
            grid[x][y] = turnVar  # updates values on the grid
            print("Move grid:")
            print(grid)

    if pieceCounter >= 6:
        if validMove is True:
            grid[sX][sY] = 0  # unhighlights selected values
            grid[x][y] = selectedColor  # sets the pciked move coords to the selected color
            coordSelected = False  # sets selected to false
            firstPick = 0  # resets the pick counter
        if coordSelected is True and firstSelect == 1:
            selectGrid[sX][sY] = 1  # makes a yellow highlight for the select grid
            selectedColor = grid[sX][sY]
            print("Select grid:")
            print(selectGrid)
        if (coordSelected is False) or (coordDeselected is True):  # if unselected/moved
            for r in range(3):  # blanket unhighlighting of highlighted values
                for c in range(3):
                    selectGrid[r][c] = 0
            print("Deselect grid:")
            print(selectGrid)
            coordDeselected = False
            selectedColor = None  # unstores the color of highlighted piece
            firstSelect = 0  # resets the select counter to 0


def checkWin():  # checks for win condition
    global running, pieceCounter
    if ((grid[0][0] != 0 and grid[0][0] == grid[0][1] and grid[0][0] == grid[0][2]) or
            (grid[1][0] != 0 and grid[1][0] == grid[1][1] and grid[1][0] == grid[1][2]) or
            (grid[2][0] != 0 and grid[2][0] == grid[2][1] and grid[2][0] == grid[2][2]) or
            (grid[0][0] != 0 and grid[0][0] == grid[1][0] and grid[0][0] == grid[2][0]) or
            (grid[0][1] != 0 and grid[0][1] == grid[1][1] and grid[0][1] == grid[2][1]) or
            (grid[0][2] != 0 and grid[0][2] == grid[1][2] and grid[0][2] == grid[2][2]) or
            (grid[0][0] != 0 and grid[0][0] == grid[1][1] and grid[0][0] == grid[2][2]) or
            (grid[0][2] != 0 and grid[0][2] == grid[1][1] and grid[0][2] == grid[2][0])):
        if pieceCounter % 2 == 1:  # piececounter updates after checkwin() so it is offset by 1
            print("Red wins")
        else:
            print("Blue wins")

        running = False


running = True
while running:
    for event in pygame.event.get():  # exit code
        if event.type == QUIT:
            running = False

    '''
    while not setupDone:
        setup()
    '''
    baseBoard()  # displays the grid

    # figures out if it is players 1 or 2 turn
    if pieceCounter % 2 == 0:
        turnVar = 1  # red value
    else:
        turnVar = 2  # blue value

    # place all 6 pieces
    if pieceCounter < 6:
        placeCoords()
        updateGrids()
        drawPieces()
        lastMoveCoords = x, y

    # move pieces code
    elif pieceCounter >= 6 and validMove is False:
        getCoords()  # selects the piece you want to move
        print("Last x, y:", x, y)
        print("Last vX, vY:", vX, vY)
        newSelectedCoords = vX, vY
        #if (pygame.mouse.get_pressed()[0] and grid[vX][vY] == chosenColor and (vX != x and vY != y)) and (coordDeselected or coordSelected is False):  # to select pieces
        if pygame.mouse.get_pressed()[0] and (newSelectedCoords != lastMoveCoords) and grid[vX][vY] == turnVar and (coordDeselected or not coordPicked):
            firstSelect += 1
            if firstSelect == 1:
                sX = vX
                sY = vY
                coordSelected = True
                coordDeselected = False
                firstDeselect = 0
                print("(running) sX and sY: ", sX, sY)
                updateGrids()  # updates the select grid

        # sets a dedicated deselect button (right mouse button)
        if coordSelected and coordDeselected is False and pygame.mouse.get_pressed()[2]:
            firstDeselect += 1
            if firstDeselect == 1:
                dX = vX
                dY = vY

                selectGrid[sX][sY] = 0
                coordDeselected = True
                coordSelected = False
                coordPicked = False
                validMove = False
                firstSelect = 0
                firstPick = 0
                print("dX and dY == sX and sY: ", dX, dY)
                updateGrids()  # updates the select grid

        # to place pieces
        if pygame.mouse.get_pressed()[0] and grid[vX][vY] == 0 and coordSelected and coordDeselected is False and coordPicked is False:
            firstPick += 1
            if firstPick == 1:
                x = vX
                y = vY
                coordPicked = True
                print("x and y: ", x, y)
                checkValid()  # checks to see if coords are valid
                updateGrids()  # upgrades the moving/placing grid
                lastMoveCoords = x, y

        drawPieces()  # draws/moves the pieces
        highlightPieces()  # recalls the draw highlight to remove the highlighted piece
        pygame.display.flip()  # updates the board to compensate for highlights

    validMove = False
    checkWin()  # checks for a win

    pygame.time.Clock().tick(60)
    pygame.display.flip()  # updates board

# pygame.quit()