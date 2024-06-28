"""
====================================================================================================
Program Name: FullPiPicaria

Description: This program implements a graphical user interface (GUI) and networking based version 
             of the traditional game Picaria. FullPiPicaria is designed to run on Raspberry Pi 4/5 
             computers, where players operate different systems and challenge each other through 
             the use of network protocols and simple end-to-end data transmission.

Author: C. Andrew Martinus

Last Edited: February 2, 2024

====================================================================================================
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
eCoordPicked = None  # this is the boolean for the enemy choosing coord to place
coordSelected = False  # this is the boolean for choosing a coord to select
coordDeselected = False  # this is the boolean for if a coord is deselected
x, y = None, None  # these are the placing coords
sX, sY = None, None  # these are the coords of selected pieces
dX, dY = None, None  # these are the coords of the desected pieces (basically used as a check)
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
oppPlaced = 0 # tracks if the opponent placed

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
    '''
    UDP_IP1 = input("Enter your IP: ")  # the user's ip
    UDP_IP2 = input("Enter your opponents IP: ")  # the opponent's ip
    playerName = input("Choose red or blue: ")  # player name is used to set turncounter
    '''
    
    UDP_IP1 = "[ENTER USER IP HERE]"
    UDP_IP2 = "[ENTER USER IP HERE]"
    playerName = "r"
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

    print("\nWelcome to Picaria.")
    print("To play, you take turns placing up to 3 colored pieces each")
    print("After there are 6 pieces on the board, you can move a piece to an adjacent are each turn")
    print("Like Tic Tac Toe, the goal is to match three of your pieces in a row")
    print("Use left click to place, select, and move, and right click to deselect")


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
    # print("success")


def drawPieces():  # draws the main grid pieces
    global piecesCoords, r, c, coordPicked, eCoordPicked, coordSelected, coordDeselected, validMove, turnCounter, pieceCounter, oppPlaced

    for r in range(3):
        for c in range(3):
            if grid[r][c] == 1:  # draws a circle where there are red pieces (1)
                mapCoords()
                pygame.draw.circle(gui, 'red', piecesCoords, pRad)
            if grid[r][c] == 2:  # draws a circle where there are blue pieces (2)
                mapCoords()
                pygame.draw.circle(gui, 'blue', piecesCoords, pRad)

    if (coordPicked and (turnCounter % 2 == 0 or turnCounter % 2 == 1)) or (
            oppPlaced == 1 and turnCounter % 2 == 1):  # only increments the counter if a coord is picked
        pieceCounter += 1
        turnCounter += 1
        coordPicked = False  # sets it to false after placing
        oppPlaced = 0


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
    global coordPicked, vX, vY, x, y, pieceCounter, UDP_IP1, UDP_IP2, UDP_PORT, firstPick, sendPacket, receivePacket, eCoordPicked
    # runs when player turn
    if turnCounter % 2 == 0:
        vY, vX = pygame.mouse.get_pos()
        vX = int(vX / (800 / 3))
        vY = int(vY / (800 / 3))

        if pygame.mouse.get_pressed()[0] and grid[vX][vY] == 0 and coordPicked is False:  # to place pieces
            firstPick += 1
            # gets coords from the very instant you clicked and saves them to x and y
            if firstPick == 1:
                x = vX
                y = vY
                coordPicked = True
                #print("xy", x, y)
                #print(coordPicked)

                # sets the sendpacket to be picked coords and coordPicked bool
                sendPacket = (str(str(x) + " " + str(y) + " 1")).encode()
        elif firstPick != 1 or coordPicked is False:
            coordPicked = False
            # sets the sendpacket to be general coords and coordPicked bool
            sendPacket = (str(str(vX) + " " + str(vY) + " 0")).encode()
        print("sender packet (vX, vY, cP)", sendPacket)
        # repeatedly sends the packet
        sock = socket.socket(socket.AF_INET,  # Internet
                             socket.SOCK_DGRAM)  # UDP
        sock.sendto(sendPacket, (UDP_IP2, UDP_PORT))
    # runs when enemy turn and other player hasnt picked placement coords
    if turnCounter % 2 == 1:
        sock = socket.socket(socket.AF_INET,  # Internet
                                 socket.SOCK_DGRAM)  # UDP
        sock.bind((UDP_IP1, UDP_PORT))
        receivePacket, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        
        print("reciever packet", str(receivePacket.decode()))
        vX, vY, eCoordPicked = (receivePacket.decode()).split()  # decodes it from bytes and splits the string
        print("eCP", eCoordPicked, type(eCoordPicked))
        if eCoordPicked is "0":
            coordPicked = False
        elif eCoordPicked is "1":
            coordPicked = True
        else:
            coordPicked = False
        print("coordPicked", coordPicked)
        
        if coordPicked:            
            x = int(vX)
            y = int(vY)
        else:
            vX = int(vX)
            vY = int(vY)

def getCoords():  # gets selected x and selected y
    global coordSelected, vX, vY

    vY, vX = pygame.mouse.get_pos()
    vX = int(vX / (800 / 3))
    vY = int(vY / (800 / 3))
    print("vXvY", vX, vY)


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
    global x, y, sX, sY, turnVar, selectedColor, coordPicked, eCoordPicked, coordSelected, \
        coordDeselected, validMove, pieceCounter, firstSelect, firstPick, oppPlaced

    if pieceCounter < 6:
        print("cP", coordPicked)
        if coordPicked:
            firstPick = 0
            grid[x][y] = turnVar  # updates values on the grid
            #print("Move grid:")
            #print(grid)

    if pieceCounter >= 6:
        if turnCounter % 2 == 0:
            if validMove is True:
                grid[sX][sY] = 0  # unhighlights selected values
                grid[x][y] = selectedColor  # sets the pciked move coords to the selected color
                coordSelected = False  # sets selected to false
                firstPick = 0  # resets the pick counter

                sendPacket = str(str(x) + " " + str(y) + " " + str(selectedColor) + " " + "1").encode()
                sock = socket.socket(socket.AF_INET,  # Internet
                                     socket.SOCK_DGRAM)  # UDP
                sock.sendto(sendPacket, (UDP_IP2, UDP_PORT))

            if coordSelected is True and firstSelect == 1:
                selectGrid[sX][sY] = 1  # makes a yellow highlight for the select grid
                selectedColor = grid[sX][sY]
                #print("Select grid:")
                #print(selectGrid)
            if (coordSelected is False) or (coordDeselected is True):  # if unselected/moved
                for r in range(3):  # blanket unhighlighting of highlighted values
                    for c in range(3):
                        selectGrid[r][c] = 0
                #print("Deselect grid:")
                #print(selectGrid)
                coordDeselected = False
                selectedColor = None  # unstores the color of highlighted piece
                firstSelect = 0  # resets the select counter to 0
        if turnCounter % 2 == 1:
            grid[x][y] = selectedColor


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

    while not setupDone:
        setup()
    print(turnCounter)

    baseBoard()  # displays the grid

    # figures out if it is players 1 or 2 turn
    if pieceCounter % 2 == 0:
        turnVar = 1  # red value
    else:
        turnVar = 2  # blue value
    #print("turnVar", turnVar)

    # place all 6 pieces
    if pieceCounter < 6:
        #print("prepc")
        placeCoords()
        #print("postpc")
        updateGrids()
        print(grid)
        drawPieces()
        lastMoveCoords = x, y

    # move pieces code
    elif pieceCounter >= 6 and validMove is False:
        print("moveturn")
        if turnCounter % 2 == 0:
            getCoords()  # selects the piece you want to move

            newSelectedCoords = vX, vY
            # to select pieces the user wants to move
            if pygame.mouse.get_pressed()[0] and (newSelectedCoords != lastMoveCoords) and grid[vX][
                vY] == chosenColor and (coordDeselected or not coordPicked) and turnCounter % 2 == 0:
                firstSelect += 1
                if firstSelect == 1:
                    sX = vX
                    sY = vY
                    coordSelected = True
                    coordDeselected = False
                    firstDeselect = 0
                    #print("(running) sX and sY: ", sX, sY)

                    updateGrids()  # updates the select grid

            # sets a dedicated deselect button (right mouse button)
            if coordSelected and coordDeselected is False and pygame.mouse.get_pressed()[2] and turnCounter % 2 == 0:
                firstDeselect += 1
                if firstDeselect == 1:
                    selectGrid[sX][sY] = 0
                    coordDeselected = True
                    coordSelected = False
                    coordPicked = False
                    validMove = False
                    firstSelect = 0
                    firstPick = 0
                    updateGrids()  # updates the select grid

            # to place pieces
            if pygame.mouse.get_pressed()[0] and grid[vX][
                vY] == 0 and coordSelected and coordDeselected is False and coordPicked is False and turnCounter % 2 == 0:
                firstPick += 1
                if firstPick == 1:
                    x = vX
                    y = vY
                    coordPicked = True
                    #print("x and y: ", x, y)
                    checkValid()  # checks to see if coords are valid
                    updateGrids()  # upgrades the moving/placing grid
                    lastMoveCoords = x, y

        if turnCounter % 2 == 1:
            sock = socket.socket(socket.AF_INET,  # Internet
                                 socket.SOCK_DGRAM)  # UDP
            sock.bind((UDP_IP1, UDP_PORT))

            receivePacket, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
            x, y, chosenColor, oppPlaced = (
                receivePacket.decode()).split()  # decodes it from bytes and splits the string
            x = int(x)
            y = int(y)
            chosenColor = int(chosenColor)
            oppPlaced = int(oppPlaced)

            if oppPlaced == 1:
                updateGrids()  # upgrades the moving/placing grid

        drawPieces()  # draws/moves the pieces
        highlightPieces()  # recalls the draw highlight to remove the highlighted piece
        pygame.display.flip()  # updates the board to compensate for highlights

    validMove = False
    checkWin()  # checks for a win

    pygame.time.Clock().tick(60)
    pygame.display.flip()  # updates board

pygame.quit()
