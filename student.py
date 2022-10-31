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

        while True:
            try:
                state = json.loads(
                    await websocket.recv()
                )  # receive game update, this must be called timely or your game will get out of sync with the server
                key = ""
                #print(state)
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
                        elif redCar_coord != "" and y == redCar_coord[1] and x == redCar_coord[0] + 1:
                            if grid_state_parsed[i] != "A" and grid_state_parsed[i] != "o":
                                notBlocked = False
                                if cursor == redCar_coord and select != "":
                                    key=" "
                        i=i+1
                    grid.append(row)
                print(grid)   
               
                print(cursor)
                print(redCar_coord)
                if notBlocked:
                    if select != "":
                        key="d"
                    else:
                        if cursor[0] > redCar_coord[0]:
                            key="a" 
                        if cursor[0] < redCar_coord[0]:
                            key="d"
                        if cursor[1] > redCar_coord[1]:
                            key="w" 
                        if cursor[1] < redCar_coord[1]:
                            key="s"
                        if cursor == redCar_coord:
                            key=" "
                await websocket.send(
                    json.dumps({"cmd": "key", "key": key})
                )  # send key command to server - you must implement this send in the AI agent
                #else:
                    
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


# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))
