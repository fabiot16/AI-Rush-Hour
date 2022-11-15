"""Example client."""
import asyncio
from calendar import c
import getpass
import json
import os
import copy

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
                state = json.loads(await websocket.recv())  # receive game update, this must be called timely or your game will get out of sync with the server
                key = ""
                grid_state = state.get("grid")
                next_moves = []
                # Search Tree resolution

                problem = SearchProblem(generate_info(grid_state))
                t = SearchTree(problem)
                next_moves = t.search()
                print(next_moves)

                cursor = state.get("cursor")
                select = state.get("selected")
                move = next_moves.pop(0)
                print(move)

                target = [move[1], move[2]]
                direction = move[3]

                if target != "" and cursor != target:
                    if select != "":
                        key = " "
                    elif cursor[0] > target[0]:
                        key = "a" 
                    elif cursor[0] < target[0]:
                        key = "d"
                    elif cursor[1] > target[1]:
                        key = "w"
                    elif cursor[1] < target[1]:
                        key = "s"
                    
                if select != "" and cursor == target:
                    key = direction
                elif cursor == target:
                    key=" "
                await websocket.send(json.dumps({"cmd": "key", "key": key}))  # send key command to server - you must implement this send in the AI agent

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

def generate_info(grid):
    grid_state = grid.split()
    num_v = grid_state[0]
    grid_state_parsed = list(grid_state[1])
    bidimensional_grid = [grid_state_parsed[e:e+6] for e in range(0,36,6)]
    veiculos = []
    veiculos_found = []

    for y in range(0,6):
        if bidimensional_grid[y].count('o') != 6:
            for x in range(0,6):
                if x < 5 and bidimensional_grid[y][x] != 'o' and bidimensional_grid[y][x] != 'x' and (bidimensional_grid[y][x] == bidimensional_grid[y][x+1]) and bidimensional_grid[y][x] not in veiculos_found:
                    veiculos_found.append(bidimensional_grid[y][x])
                    orientation = 'Horizontal'
                    length = grid_state_parsed.count(bidimensional_grid[y][x])
                    veiculos.append(Veiculo(bidimensional_grid[y][x], x, y, length, orientation))

                elif x < 6 and bidimensional_grid[y][x] != 'o' and bidimensional_grid[y][x] != 'x' and bidimensional_grid[y][x] not in veiculos_found:
                    veiculos_found.append(bidimensional_grid[y][x])
                    orientation = 'Vertical'
                    length = grid_state_parsed.count(bidimensional_grid[y][x])
                    veiculos.append(Veiculo(bidimensional_grid[y][x], x, y, length, orientation))
    
    veiculos.sort(key = lambda v: v.id)
    return [bidimensional_grid, num_v, veiculos]

class Veiculo:
    def __init__(self, identification, x1, y1, length, orientation):
        self.id = identification
        self.x1 = x1
        self.y1 = y1
        self.length = length
        self.orientation = orientation
        self.points = []

        if orientation == "Vertical":
            self.x2 = self.x1
            self.y2 = self.y1 + self.length-1

            for i in range(self.y1,self.y2+1):
                self.points.append([self.x1,i])

        else:
            self.x2 = self.x1 + self.length-1
            self.y2 = self.y1

            for i in range(self.x1,self.x2+1):
                self.points.append([i,self.y2])
        return None

    def __str__(self):
        return "[" + str(self.id) + " - " + "(" + str(self.x1) + "," + str(self.y1) + ") " + "(" + str(self.x2) + "," + str(self.y2) + ")" + ", " + str(self.length) + ", " + str(self.orientation) + "]"
    
    def __repr__(self):
        return str(self)

class SearchProblem:
    def __init__(self, info):
        grid, num_v, veiculos = info
        self.grid = SearchNode(grid, None, veiculos, 0, None, None)
        self.veiculos = veiculos
        self.red_car = veiculos[0]
        self.num_v = num_v

class SearchNode:
    def __init__(self, state, parent, veiculos, depth, heuristic, moveFromParent):
        self.state = state
        self.parent = parent
        self.veiculos = veiculos
        self.depth = depth
        self.heuristic = heuristic
        self.moveFromParent = moveFromParent # (id, w or a or s or d)
    
    def goal_test(self):
        return self.veiculos[0].x2 == 5

    def add(self, v):
        for p in v.points:
            x,y = p
            self.state[y][x] = v.id
        
        return None

    def remove(self, v):
        for p in v.points:
            x,y = p
            self.state[y][x] = 'o'
        return None

    def updateV(self, v):
        for i in range(0, len(self.veiculos)):
            if self.veiculos[i].id == v.id:
                self.veiculos[i] = v
                break
            
        return None

    def move_vehicle(self, v, direction):
        if v.orientation == "Vertical":
            if direction > 0:
                self.state[v.y2][v.x1] = 'o'
                self.state[v.y1-1][v.x1] = v.id
            else:
                self.state[v.y1][v.x1] = 'o'
                self.state[v.y2+1][v.x1] = v.id
        else:
            if direction > 0:
                self.state[v.y1][v.x1] = 'o'
                self.state[v.y2][v.x2+1] = v.id
            else:
                self.state[v.y2][v.x2] = 'o'
                self.state[v.y1][v.x1-1] = v.id
        return None
    
    def can_move(self, v, direction):
        if v.orientation == "Vertical":
            if direction > 0 and v.y1 > 0 and self.state[v.y1-1][v.x1] == 'o':
                return True
            elif direction < 0 and v.y2 < 5 and self.state[v.y2+1][v.x1] == 'o':
                return True
        else:
            if direction > 0 and v.x2 < 5 and self.state[v.y1][v.x2+1] == 'o':
                return True
            elif direction < 0 and v.x1 > 0 and self.state[v.y1][v.x1-1] == 'o':
                return True
        return False

    def next_moves(self):
        for v in self.veiculos:
            if self.can_move(v,1):
                move1 = SearchNode(copy.deepcopy(self.state),self,copy.deepcopy(self.veiculos),self.depth+1, None, None)
                if v.orientation == 'Vertical':
                    if v.length < 3:
                        #move1.remove(v)
                        temp = Veiculo(v.id, v.x1, v.y1-1, v.length, v.orientation)
                        #move1.add(temp)
                        move1.move_vehicle(v,1)
                        move1.updateV(temp)
                        move1.moveFromParent = (v.id, v.x1, v.y1,"w")
                        yield move1
                        #print("move:")
                        #print(move)
                else:
                    #move1.remove(v)
                    temp = Veiculo(v.id, v.x1+1, v.y1, v.length, v.orientation)
                    #move1.add(temp)
                    move1.move_vehicle(v,1)
                    move1.updateV(temp)
                    move1.moveFromParent = (v.id, v.x1, v.y1,"d")
                    yield move1
            if self.can_move(v,-1):
                move2 = SearchNode(copy.deepcopy(self.state),self,copy.deepcopy(self.veiculos),self.depth+1, None, None)
                if v.orientation == 'Vertical':
                    #move2.remove(v)
                    temp = Veiculo(v.id, v.x1, v.y1+1, v.length, v.orientation)
                    #move2.add(temp)
                    move2.move_vehicle(v,-1)
                    move2.updateV(temp)
                    move2.moveFromParent = (v.id, v.x1, v.y1,"s")
                    yield move2
                else:
                    #move2.remove(v)
                    temp = Veiculo(v.id, v.x1-1, v.y1, v.length, v.orientation)
                    #move2.add(temp)
                    move2.move_vehicle(v,-1)
                    move2.updateV(temp)
                    move2.moveFromParent = (v.id, v.x1, v.y1,"a")
                    yield move2
    
    def calcHeuristic(self):
        goal_row = self.state[2]
        distance_to_goal = 5 - self.veiculos[0].x2
        blocking_goal = []
        blocking_blockers = []

        for x in range(self.veiculos[0].x2 + 1, 6):
            if goal_row[x] != 'o' and goal_row[x] not in blocking_goal:
                blocking_goal.append((goal_row[x],x))

        for i in range(len(blocking_goal)):
            x = blocking_goal[i][1]
            for y in range(0,6):
                if self.state[y][x] != 'o' and self.state[y][x] not in blocking_goal and self.state[y][x] not in blocking_blockers:
                    blocking_blockers.append(self.state[y][x])

        return distance_to_goal + len(blocking_goal) + len(blocking_blockers)  
    
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
        self.closed_nodes = []
        self.solution = None
    
    def get_moves(self, node): 
        if node.depth == 0:
            return []
        moves = self.get_moves(node.parent)
        moves += [node.moveFromParent]
        return moves

    def search(self, limit = 18):
        while self.open_nodes != []:
            #print("OPEN-------------------NODES")
            #print(self.open_nodes)
            node = self.open_nodes.pop(0)
            self.closed_nodes.append(bidimensional_array_to_string(node.state))
            #print("-----NOVO NODE-----")
            #print(node)
            if node.goal_test() and node.depth <= limit:
                print("DONE----------------------------------")
                print(node.depth)
                self.solution = node
                print(len(self.closed_nodes))
                print(len(self.open_nodes))
                return self.get_moves(node)
            lnewnodes = []
            for child in node.next_moves():
                state = bidimensional_array_to_string(child.state)
                if state not in self.closed_nodes and state not in self.open_states:
                    self.open_states.append(state)
                    child.heuristic = child.calcHeuristic()
                    #print("-----CHILD-----")
                    #print(child)
                    lnewnodes.append(child)
                    #print("lnewnoode::::::::.")
                    #print(lnewnodes)
            self.add_to_open(lnewnodes)
        return None

    def add_to_open(self,lnewnodes):
        #print("on open")
        #print(lnewnodes)
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
