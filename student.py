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
                test(grid_state)
                break
                grid_state_edges = grid_state.split()
                grid_state_parsed = list(grid_state_edges[1])
                print("Grid state:")
                print(grid_state)
                print("Grid state edges:")
                print(grid_state_edges)
                print("Grid state parsed:")
                print(grid_state_parsed)
                print("generate_info:")
                generate_info(grid_state)
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
                print("Grid:")
                print(grid)
                print("Other cars:")
                print(otherCars)
                #print(cursor)
                #print(redCar_coord)
                #print(jumps)
                
                if notBlocked:
                    target = redCar_coord
                    direction = "d"
                    #jumps = redjumps
                    
                    
                else:
                    if grid[redCar_coord[1]][redCar_coord[0]+1] in otherCars and jumps == 0: 
                        predecessors = [grid[redCar_coord[1]][redCar_coord[0]+1]]   
                        print("Predecessors:")
                        print(predecessors)
                        nextMove = nextStep(grid, otherCars, grid[redCar_coord[1]][redCar_coord[0]+1], (redCar_coord[0]+1, redCar_coord[1]), predecessors)
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

def nextStep(grid, otherCars, car, obs, predecessors):
        positions = otherCars[car]
        size = len(positions) 
        if size > 2:
            size = size -1
        spaceToMoveUp =0
        spaceToMoveDown =0
        spaceToMoveleft =0
        spaceToMoveright =0
        x = positions[0][0]
        y = positions[0][1]
        print(predecessors)
        
        if positions[0][0] - positions[-1][0] == 0:
            if obs == positions[0] and positions[-1][1] + 1 < len(grid) and grid[positions[-1][1] +1][x] == "o":
                return (positions[-1], "s", 1)
   
            if obs == positions[-1] and positions[0][1] - 1>=0 and grid[positions[0][1] -1][x] == "o":
                return (positions[0], "w", 1)
                
                
            if positions[-1][1] + size < len(grid):
                valid=True
                for tempy in range(1, size+1):
                    if grid[positions[-1][1] + tempy][x] != "o":
                        valid = False
                    if grid[positions[-1][1] +tempy][x] in otherCars and grid[positions[-1][1] +tempy][x] != car and grid[positions[-1][1] +tempy][x] not in predecessors:
                        predecessors = predecessors + [grid[positions[-1][1] +tempy][x]]
                        next = nextStep(grid, otherCars, grid[positions[-1][1] +tempy][x], (x, positions[-1][1] +tempy), predecessors)
                        if next:
                            return next
                if valid:  
                    return (positions[-1], "s", size)
                    
            if positions[0][1] - size >= 0 and positions[0][1]  >= size:
                valid=True
                for tempy in range(1, size+1):
                    if grid[positions[0][1] - tempy][x] != "o":
                        valid = False
                    if grid[positions[0][1] - tempy][x] in otherCars and grid[positions[0][1] - tempy][x] != car and grid[positions[0][1] - tempy][x] not in predecessors:
                        predecessors = predecessors + [grid[positions[0][1] - tempy][x]]
                        next = nextStep(grid, otherCars, grid[positions[0][1] - tempy][x],(x, positions[-1][1] -tempy), predecessors)
                        if next:
                            return next
                if valid:  
                    return (positions[0], "w", size)
                        
    
        if positions[0][1] - positions[-1][1] == 0:
        
            if obs == positions[0] and positions[-1][0] + 1 < len(grid[y]) and grid[y][positions[-1][0] + 1] == "o":
                return (positions[-1], "d", 1)
            

                
            if obs == positions[-1] and positions[0][0] - 1 >= 0 and grid[y][positions[0][0] - 1] == "o":
                return (positions[-1], "a", 1)
                
                
            if positions[-1][0] + size < len(grid[y]):
                valid=True
                for tempx in range(1, size+1):
                    if grid[y][positions[-1][0] + tempx] != "o":
                        valid = False
                    if grid[y][positions[-1][0] + tempx] in otherCars and  grid[y][positions[-1][0] + tempx] != car and grid[y][positions[-1][0] + tempx] not in predecessors:
                        predecessors = predecessors + [grid[y][positions[-1][0] + tempx]]
                        next = nextStep(grid, otherCars, grid[y][positions[-1][0] + tempx], (positions[-1][0] + tempx, y), predecessors)
                        if next:
                            return next
                        
                if valid:  
                    return (positions[-1], "d", size)
                    
            if positions[0][0] - size >= 0  and positions[0][0]  >= size:
                valid=True
                for tempx in range(1, size+1):
                    if grid[y][positions[0][0] - tempx] != "o":
                        valid = False
                    if grid[y][positions[0][0] - tempx] in otherCars and grid[y][positions[0][0] - tempx] != car and grid[y][positions[0][0] - tempx] not in predecessors:
                        predecessors = predecessors + [grid[y][positions[0][0] - tempx]]
                        next = nextStep(grid, otherCars, grid[y][positions[0][0] - tempx], (positions[0][0] - tempx, y), predecessors)
                        if next:
                            return next
                if valid:  
                    return (positions[0], "a", size)  
        
        return None

def test(grid):
    problem = SearchProblem(generate_info(grid))
    t = SearchTree(problem)
    print(t.search())
    
    return None

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
                if x < 5 and bidimensional_grid[y][x] != 'o' and (bidimensional_grid[y][x] == bidimensional_grid[y][x+1]) and bidimensional_grid[y][x] not in veiculos_found:
                    veiculos_found.append(bidimensional_grid[y][x])
                    orientation = 'Horizontal'
                    length = grid_state_parsed.count(bidimensional_grid[y][x])
                    veiculos.append(Veiculo(bidimensional_grid[y][x], x, y, length, orientation))

                elif x < 6 and bidimensional_grid[y][x] != 'o' and bidimensional_grid[y][x] not in veiculos_found:
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
        print(self.points)
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
        self.moveFromParent = moveFromParent # (id, +/-1)
    
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
            elif v.y2 < 5 and self.state[v.y2+1][v.x1] == 'o':
                return True
        else:
            if direction > 0 and v.x2 < 5 and self.state[v.y1][v.x2+1] == 'o':
                return True
            elif v.x1 > 0 and self.state[v.y1][v.x1-1] == 'o':
                return True
        return False

    def next_moves(self):
        for v in self.veiculos:
            if self.can_move(v,1):
                move1 = SearchNode(copy.deepcopy(self.state),self,copy.deepcopy(self.veiculos),self.depth+1, None, None)
                if v.orientation == 'Vertical':
                    move1.remove(v)
                    temp = Veiculo(v.id, v.x1, v.y1-1, v.length, v.orientation)
                    move1.add(temp)
                    #move.move_vehicle(v,1)
                    move1.updateV(temp)
                    move1.moveFromParent = (v.id,1)
                    yield move1
                    #print("move:")
                    #print(move)
                else:
                    move1.remove(v)
                    temp = Veiculo(v.id, v.x1+1, v.y1, v.length, v.orientation)
                    move1.add(temp)
                    #move.move_vehicle(v,1)
                    move1.updateV(temp)
                    move1.moveFromParent = (v.id,1)
                    yield move1
            if self.can_move(v,-1):
                move2 = SearchNode(copy.deepcopy(self.state),self,copy.deepcopy(self.veiculos),self.depth+1, None, None)
                if v.orientation == 'Vertical':
                    move2.remove(v)
                    temp = Veiculo(v.id, v.x1, v.y1+1, v.length, v.orientation)
                    move2.add(temp)
                    #move.move_vehicle(v,-1)
                    move2.updateV(temp)
                    move2.moveFromParent = (v.id,-1)
                    yield move2
                else:
                    move2.remove(v)
                    temp = Veiculo(v.id, v.x1-1, v.y1, v.length, v.orientation)
                    move2.add(temp)
                    #move.move_vehicle(v,-1)
                    move2.updateV(temp)
                    move2.moveFromParent = (v.id,-1)
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
        root = problem.grid
        self.open_nodes = [root]
        self.closed_nodes = []
        self.solution = None
    
    def get_moves(self, node): 
        if node.depth == 0:
            return []
        moves = self.get_moves(node.parent)
        moves += [node.moveFromParent]
        return moves

    def search(self):
        while self.open_nodes != []:
            print("OPEN-------------------NODES")
            print(self.open_nodes)
            node = self.open_nodes.pop()
            self.closed_nodes.append(bidimensional_array_to_string(node.state))
            print("-----NOVO NODE-----")
            print(node)
            if node.goal_test():
                print("DONE----------------------------------")
                self.solution = node
                return self.get_moves(node)
            lnewnodes = []
            for child in node.next_moves():
                if bidimensional_array_to_string(child.state) not in self.closed_nodes:
                    child.heuristic = child.calcHeuristic()
                    print("-----CHILD-----")
                    print(child)
                    lnewnodes.append(child)
                    print("lnewnoode::::::::.")
                    print(lnewnodes)
            self.add_to_open(lnewnodes)
        return None

    def add_to_open(self,lnewnodes):
        print("on open")
        print(lnewnodes)
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
