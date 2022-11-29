"""Example client."""
import asyncio
from calendar import c
import getpass
import json
import os
import time

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
        
        level = 0
        target=""
        direction=""
        key = ""
        next_moves = []
        state = json.loads(await websocket.recv())  # receive game update, this must be called timely or your game will get out of sync with the server
        grid_state = state.get("grid")
        cursor = state.get("cursor")
        select = state.get("selected")

        while True:
            try:
                if next_moves == []:
                    state = json.loads(await websocket.recv())  # receive game update, this must be called timely or your game will get out of sync with the server
                    grid = state.get("grid")
                    grid_state = grid.split()
                    grid_state_parsed = list(grid_state[1])
                    if grid_state[0] != level:
                        level = grid_state[0]
                        print("Level: ",level)
                        problem = SearchProblem(generate_info(grid_state_parsed))
                        t = SearchTree(problem)
                        next_moves = t.search()
                        print(next_moves)
                        print(len(next_moves)," moves")

                        state = json.loads(await websocket.recv())  # receive game update, this must be called timely or your game will get out of sync with the server
                        move = next_moves.pop(0)
                        move_done = False

                else:
                    while next_moves != []:
                        
                        state = json.loads(await websocket.recv())  # receive game update, this must be called timely or your game will get out of sync with the server
                        cursor = state.get("cursor")

                        if move_done:
                            move = next_moves.pop(0)
                            move_done = False
                        print("Next move: ", move)
                        target = move[1]
                        direction = move[2]

                        if cursor != target:
                            cursor_moves = list(cursor_to_target(cursor,target))

                            for m in cursor_moves:
                                key = m
                                await websocket.send(json.dumps({"cmd": "key", "key": key}))  # send key command to server - you must implement this send in the AI agent
                                state = json.loads(await websocket.recv())  # receive game update, this must be called timely or your game will get out of sync with the server
                        
                        grid_state = state.get("grid")
                        grid_state_edges = grid_state.split()
                        compare = grid_state_edges[1]
                        select = state.get("selected")
                        
                        if move[3] is not None and compare != move[3]: # check if crazy driver happened
                            print("Crazy Driver")
                            if select != "":
                                key=" "
                                await websocket.send(json.dumps({"cmd": "key", "key": key}))  # send key command to server - you must implement this send in the AI agentstate = json.loads(await websocket.recv())  # receive game update, this must be called timely or your game will get out of sync with the server
                            crazy_moves = get_crazy_moves(move[3],generate_info(move[3])[1], compare, generate_info(compare)[1])
                            if len(crazy_moves) > 1:
                                crazy_moves.reverse()
                            #print("CRAZY MOVES-------------------------------------")
                            #print(crazy_moves)
                            next_moves.insert(0, move)
                            if crazy_moves != None:
                                for m in crazy_moves:
                                    next_moves.insert(0,m)
                            #print("NEXT_MOVES -----------------------------------------")
                            #print(next_moves)
                            move = next_moves.pop(0)
                            break
                        
                        if select == "":
                            key=" "
                            await websocket.send(json.dumps({"cmd": "key", "key": key}))  # send key command to server - you must implement this send in the AI agentstate = json.loads(await websocket.recv())  # receive game update, this must be called timely or your game will get out of sync with the server
                            state = json.loads(await websocket.recv())  # receive game update, this must be called timely or your game will get out of sync with the server
                        
                        state = json.loads(await websocket.recv())  # receive game update, this must be called timely or your game will get out of sync with the server
                        grid_state = state.get("grid")
                        grid_state_edges = grid_state.split()
                        compare = grid_state_edges[1]

                        if move[3] is not None and move[3] != compare:
                            if select != "":
                                key=" "
                                await websocket.send(json.dumps({"cmd": "key", "key": key}))  # send key command to server - you must implement this send in the AI agentstate = json.loads(await websocket.recv())  # receive game update, this must be called timely or your game will get out of sync with the server
                            break

                        key = direction
                        await websocket.send(json.dumps({"cmd": "key", "key": key}))  # send key command to server - you must implement this send in the AI agentstate = json.loads(await websocket.recv())  # receive game update, this must be called timely or your game will get out of sync with the server
                        state = json.loads(await websocket.recv())  # receive game update, this must be called timely or your game will get out of sync with the server
                        grid_state = state.get("grid")
                        grid_state_edges = grid_state.split()
                        compare = grid_state_edges[1]
                        if next_moves == [] and move[4] is not None and move[4] != compare:
                            break
                        move_done = True

                        if next_moves != [] and next_moves[0][0] != move[0]:
                            key=" "
                            await websocket.send(json.dumps({"cmd": "key", "key": key}))  # send key command to server - you must implement this send in the AI agentstate = json.loads(await websocket.recv())  # receive game update, this must be called timely or your game will get out of sync with the server
                            

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

def cursor_to_target(cursor, target):
    x = cursor[0] - target[0]
    y = cursor[1] - target[1]

    if x > 0:
        x = "a" * x
    elif x < 0:
        x = "d" * abs(x)
    elif x == 0:
        x = ""
    if y > 0:
        y = "w" * y
    elif y < 0:
        y = "s" * abs(y)
    elif y == 0:
        y = ""
    return x+y

def get_crazy_moves(previous_grid, previous_vehicles, crazy_grid, crazy_vehicles):
    moved_vehicles = []
    moves_to_undo = []

    for i in range(0,len(previous_vehicles)):
        if (previous_vehicles[i][1] != crazy_vehicles[i][1]) or (previous_vehicles[i][2] != crazy_vehicles[i][2]):
            moved_vehicles.append((previous_vehicles[i],crazy_vehicles[i]))

    for pair in moved_vehicles:
        if pair[1][1] > pair[0][1]:
            move = (pair[1][0], [pair[1][1], pair[1][2]], "a", None, None)
            moves_to_undo.append(move)

        elif pair[1][1] < pair[0][1]:
            move = (pair[1][0], [pair[1][1], pair[1][2]], "d", None, None)
            moves_to_undo.append(move)
            
        elif pair[1][2] > pair[0][2]:
            move = (pair[1][0], [pair[1][1], pair[1][2]], "w", None, None)
            moves_to_undo.append(move)
           
        elif pair[1][2] < pair[0][2]:
            move = (pair[1][0], [pair[1][1], pair[1][2]], "s", None, None)
            moves_to_undo.append(move)
            
    
        print("Moves to undo")
        print(moves_to_undo)
    return moves_to_undo

def generate_info(grid):
    bidimensional_grid = [grid[e:e+6] for e in range(0,36,6)]
    veiculos = []
    veiculos_found = []

    for y in range(0,6):
        if bidimensional_grid[y].count('o') != 6:
            for x in range(0,6):
                if x < 5 and bidimensional_grid[y][x] != 'o' and bidimensional_grid[y][x] != 'x' and (bidimensional_grid[y][x] == bidimensional_grid[y][x+1]) and bidimensional_grid[y][x] not in veiculos_found:
                    veiculos_found.append(bidimensional_grid[y][x])
                    orientation = 'Horizontal'
                    length = grid.count(bidimensional_grid[y][x])
                    veiculos.append([bidimensional_grid[y][x], x, y, length, orientation])

                elif x < 6 and bidimensional_grid[y][x] != 'o' and bidimensional_grid[y][x] != 'x' and bidimensional_grid[y][x] not in veiculos_found:
                    veiculos_found.append(bidimensional_grid[y][x])
                    orientation = 'Vertical'
                    length = grid.count(bidimensional_grid[y][x])
                    veiculos.append([bidimensional_grid[y][x], x, y, length, orientation])
    
    veiculos.sort(key = lambda v: v[0])
    return [bidimensional_grid, veiculos]

class SearchProblem:
    def __init__(self, info):
        grid, veiculos = info
        self.grid = SearchNode(grid, None, veiculos, 0, None, None)
        self.grid.heuristic = self.grid.calcHeuristic()
        self.veiculos = veiculos

class SearchNode:
    def __init__(self, state, parent, veiculos, depth, heuristic, moveFromParent):
        self.state = state
        self.parent = parent
        self.veiculos = veiculos
        self.depth = depth
        self.heuristic = heuristic
        self.moveFromParent = moveFromParent # (id, w or a or s or d)
    
    def goal_test(self):
        return self.veiculos[0][1] + self.veiculos[0][3] - 1 == 5

    def move_vehicle(self, v, direction):
        v_id, v_x, v_y, v_length, v_orientation = v
        v_x2 = v_x + v_length-1
        v_y2 = v_y + v_length-1
        index = self.veiculos.index(v)
        if v_orientation == "Vertical":
            if direction > 0:
                self.state[v_y2][v_x] = 'o'
                self.state[v_y-1][v_x] = v_id
                self.veiculos[index][2] -= 1
            else:
                self.state[v_y][v_x] = 'o'
                self.state[v_y2+1][v_x] = v_id
                self.veiculos[index][2] += 1
        else:
            if direction > 0:
                self.state[v_y][v_x] = 'o'
                self.state[v_y][v_x2+1] = v_id
                self.veiculos[index][1] += 1
            else:
                self.state[v_y][v_x2] = 'o'
                self.state[v_y][v_x-1] = v_id
                self.veiculos[index][1] -= 1
        return None
    
    def can_move(self, v, direction):
        v_id, v_x, v_y, v_length, v_orientation = v
        v_x2 = v_x + v_length-1
        v_y2 = v_y + v_length-1
        if v_orientation == "Vertical":
            if direction > 0 and v_y > 0 and self.state[v_y-1][v_x] == 'o':
                return True
            elif direction < 0 and v_y2 < 5 and self.state[v_y2+1][v_x] == 'o':
                return True
        else:
            if direction > 0 and v_x2 < 5 and self.state[v_y][v_x2+1] == 'o':
                return True
            elif direction < 0 and v_x > 0 and self.state[v_y][v_x-1] == 'o':
                return True
        return False

    def next_moves(self):
        for v in self.veiculos:
            if self.can_move(v,1):
                move = SearchNode([list(x) for x in self.state],self,[list(x) for x in self.veiculos],self.depth+1, 0, None)
                if v[4] == 'Vertical':
                    move.move_vehicle(v,1)
                    move.moveFromParent = (v[0], "w")
                    move.heuristic = move.calcHeuristic()
                    yield move
                else:
                    move.move_vehicle(v,1)
                    move.moveFromParent = (v[0], "d")
                    move.heuristic = move.calcHeuristic()
                    yield move
            if self.can_move(v,-1):
                move = SearchNode([list(x) for x in self.state],self,[list(x) for x in self.veiculos],self.depth+1, 0, None)
                if v[4] == 'Vertical':
                    move.move_vehicle(v,-1)
                    move.moveFromParent = (v[0], "s")
                    move.heuristic = move.calcHeuristic()
                    yield move
                else:
                    move.move_vehicle(v,-1)
                    move.moveFromParent = (v[0], "a")
                    if v[0] == "A":
                        move.heuristic = self.heuristic
                    else:
                        move.heuristic = move.calcHeuristic() 
                    yield move
    
    def calcHeuristic(self):
        goal_row = self.state[2]
        red_car = self.veiculos[0]
        distance_to_goal = 5 - (red_car[1] + red_car[3])
        blocking_goal = []
        top = 0
        bottom = 0

        for x in range(red_car[1] + red_car[3] + 1, 6):
            if goal_row[x] != 'x' and goal_row[x] not in blocking_goal:
                blocking_goal.append((goal_row[x],x))

        for i in range(len(blocking_goal)):
            v, x = blocking_goal[i]
            column = []
            top = 0
            bottom = 0
            for y in range(0,6):
                column.append(self.state[y][x])
            y = 0
            while column[y] != v:
                if column[y] != 'o' and column[y] != 'x':
                    top += 1
                else:
                    top = 0
                y += 1
            y = 5
            while column [y] != v:
                if column[y] != 'o' and column[y] != 'x':
                    bottom += 1
                else:
                    bottom = 0
                y -= 1

        return distance_to_goal + len(blocking_goal) + min(top, bottom)  
    
    def __str__(self):
        return "State:\n " + str(self.state) + "\nRed Car: " + str(self.veiculos[0]) + "\nVeiculos: " + str(self.veiculos) + "\nDepth: " + str(self.depth) + "\nHeuristic: " + str(self.heuristic) + "\nMove from parent: " + str(self.moveFromParent)
    
    def __repr__(self):
        return str(self)

class SearchTree:
    def __init__(self, problem):
        self.problem = problem
        self.root = problem.grid
        self.open_nodes = [self.root]
        self.open_states = [bidimensional_array_to_string(self.root.state)]
        self.solution = None
        self.t0 = time.process_time()

    def get_moves(self, node): 
        if node.depth == 0:
            return []
        moves = self.get_moves(node.parent)
        car = node.moveFromParent[0]
        index = None
        for v in node.parent.veiculos:
            if v[0] == car:
                index = node.parent.veiculos.index(v)
        coord = [node.parent.veiculos[index][1],node.parent.veiculos[index][2]]
        state = bidimensional_array_to_string(node.parent.state)
        after_state = bidimensional_array_to_string(node.state)
        move = (car, coord, node.moveFromParent[1], state, after_state)
        moves.append(move) 

        return moves

    def search(self):
        while self.open_nodes != []:
            node = self.open_nodes.pop(0)
            if node.goal_test():
                print("Time: ", time.process_time()-self.t0)
                self.solution = node
                return self.get_moves(node)
            lnewnodes = []
            for child in node.next_moves():
                state = bidimensional_array_to_string(child.state)
                if state not in self.open_states:
                    self.open_states.append(state)
                    lnewnodes.append(child)
            self.add_to_open(lnewnodes)
        return None

    def add_to_open(self,lnewnodes):
        self.open_nodes.extend(lnewnodes)
        self.open_nodes.sort(key = lambda node: node.heuristic + node.depth)
    
def bidimensional_array_to_string(barray):
    array = []
    string = ""
    for i in barray:
        array += i
    for j in array:
        string += j
    return string

# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))