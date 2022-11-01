"""Example client."""
import asyncio
import getpass
import json
import os

# Next 4 lines are not needed for AI agents, please remove them from your code!
import pygame
import websockets

pygame.init()
program_icon = pygame.image.load("data/icon2.png")
pygame.display.set_icon(program_icon)


async def agent_loop(server_address="localhost:8000", agent_name="student"):
    """Example client loop."""
    async with websockets.connect(f"ws://{server_address}/player") as websocket:

        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))

        # Next 3 lines are not needed for AI agent
        SCREEN = pygame.display.set_mode((299, 123))
        SPRITES = pygame.image.load("data/pad.png").convert_alpha()
        SCREEN.blit(SPRITES, (0, 0))
        
        target=""
        direction=""
        jumps=0
        while True:
            try:
                state = json.loads(
                    await websocket.recv()
                )  # receive game update, this must be called timely or your game will get out of sync with the server
                key = ""
                
                #print(state)
                redjumps=0
                otherCars = {}
                redCar_coord = ""
                notBlocked=True
                grid_state = state.get("grid")
                grid_state_edges = grid_state.split()
                grid_state_parsed = list(grid_state_edges[1])
                #print(grid_state_parsed)
                grid_size = state.get("dimensions")
                cursor = state.get("cursor")  
                select = state.get("selected") 
                i=0
                grid = []
                for y in range(grid_size[0]):
                    row=[]
                    for x in range(grid_size[1]):
                        row.append(grid_state_parsed[i])
                        if grid_state_parsed[i] == "A":
                            redCar_coord = [x,y]
                        if grid_state_parsed[i] == "o" and redCar_coord != "" and y == redCar_coord[1]:
                            redjumps = redjumps +1
                        elif grid_state_parsed[i] != "A" and grid_state_parsed[i] != "o" and grid_state_parsed[i] != "x":
                            if redCar_coord != "" and y == redCar_coord[1] and x == redCar_coord[0] + 1:
                                notBlocked = False
                                redjumps=0
                                if cursor == redCar_coord and select != "":
                                    key=" "
                            if grid_state_parsed[i] in otherCars:
                               otherCars[grid_state_parsed[i]] += [(x,y)]
                            else:
                                otherCars[grid_state_parsed[i]] = [(x,y)]
                        i=i+1
                    grid.append(row)
                print(grid)   
                print(otherCars)
                #print(cursor)
                #print(redCar_coord)
                print(jumps)
                
                if notBlocked:
                    target = redCar_coord
                    direction = "d"
                    #jumps = redjumps
                    
                    
                else:
                    if grid[redCar_coord[1]][redCar_coord[0]+1] in otherCars and jumps == 0:    
                        nextMove = nextStep(grid, otherCars, grid[redCar_coord[1]][redCar_coord[0]+1])
                        target = [nextMove[0][0], nextMove[0][1]]
                        direction = nextMove[1]
                        jumps = nextMove[2]
                        print(nextMove)
                if target != "" and cursor != target: 
                    if select != "":
                         key = " "
                    elif cursor[0] > target[0]:
                        key="a" 
                    elif cursor[0] < target[0]:
                        key="d"
                    elif cursor[1] > target[1]:
                        key="w" 
                    elif cursor[1] < target[1]:
                        key="s"
                elif select != "" and cursor == target:
                        key=direction
                        if jumps != 0:
                            jumps = jumps-1
                elif cursor == target:
                    key=" "
                await websocket.send(
                    json.dumps({"cmd": "key", "key": key})
                )  # send key command to server - you must implement this send in the AI agent
                
                    
                # Next lines are only for the Human Agent, the key values are nonetheless the correct ones!
                key = ""
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            key = "w"
                        elif event.key == pygame.K_LEFT:
                            key = "a"
                        elif event.key == pygame.K_DOWN:
                            key = "s"
                        elif event.key == pygame.K_RIGHT:
                            key = "d"
                        elif event.key == pygame.K_SPACE:
                            key = " "

                        elif event.key == pygame.K_d:
                            import pprint

                            pprint.pprint(state)

                        await websocket.send(
                            json.dumps({"cmd": "key", "key": key})
                        )  # send key command to server - you must implement this send in the AI agent
                        break
            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return

            # Next line is not needed for AI agent
            pygame.display.flip()

def nextStep(grid, otherCars, car):
        positions = otherCars[car]
        size = len(positions) 
        spaceToMoveUp =0
        spaceToMoveDown =0
        spaceToMoveleft =0
        spaceToMoveright =0
        x = positions[0][0]
        y = positions[0][1]
        
        if positions[0][0] - positions[-1][0] == 0:

            if positions[-1][1] + 1 < len(grid) and grid[positions[-1][1] + 1][x] == "o" and len(grid)-positions[-1][1] >= size-1:
                return (positions[-1], "s", 1)
                
            
            if positions[0][1] - 1 >= 0 and grid[positions[0][1] - 1][x] == "o" and positions[0][1] >= size-1:
                return (positions[0], "w", 1)
                
                
        if positions[0][1] - positions[-1][1] == 0:
            
            
            if positions[-1][0] + 1 < len(grid[y]) and grid[y][positions[-1][0] + 1] == "o" and len(grid[y])-positions[-1][0] >= size-1:
                return (positions[-1], "d", 1)
                
            if positions[0][0] - 1 >= 0 and grid[y][positions[0][0] - 1] == "o" and positions[0][0] >= size-1:
                return (positions[0], "a", 1)
                
                    
        if positions[0][0] - positions[-1][0] == 0:
        
            if grid[positions[0][1] - 1][x] in otherCars and grid[positions[0][1] - 1][x] != car:
                next = nextStep(grid, otherCars, grid[positions[0][1] - 1][x])
                if next:
                    return next
        
            if grid[positions[-1][1] +1][x] in otherCars and grid[positions[-1][1] +1][x] != car:
                next = nextStep(grid, otherCars, grid[positions[-1][1] +1][x])
                if next:
                    return next
            
                
        if positions[0][1] - positions[-1][1] == 0:
        
            if grid[y][positions[-1][0] + 1] in otherCars and grid[y][positions[-1][0] + 1] != car:
                next = nextStep(grid, otherCars, grid[y][positions[-1][0] + 1])
                if next:
                    return next
            if grid[y][positions[0][0] - 1] in otherCars and grid[y][positions[0][0] - 1] != car:
                next = nextStep(grid, otherCars, grid[y][positions[0][0] - 1])
                if next:
                    return next
        return None






# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))
