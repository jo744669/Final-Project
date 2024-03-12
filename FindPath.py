########################################
# Jillian O'Connell and Luke Mcginley
# Artificial Intelligence
# May 7, 2024
# Final Project
# Purpose: This project should simulate a robot in a hospital delivering medicine to different patients in different wards
# dependent upon the priority of the destination ward. It should be implemented using A* and Dijkstra's Algorithms.
########################################

from queue import PriorityQueue


######################################################
#### A cell stores f(), g() and h() values
#### A cell is either open or part of a wall
######################################################
class Cell:
    #### Initially, arre maze cells have g() = inf and h() = 0
    def __init__(self, x, y, is_wall=False):
        self.x = x
        self.y = y
        self.is_wall = is_wall
        self.g = float("inf")
        self.h = 0
        self.f = float("inf")
        self.parent = None
        self.ward = "" # keep track of what ward the cell is a part of for later use
        self.priority = 0 # keep track of what priority cell location has based on ward

    #### Compare two cells based on their evaluation functions
    def __lt__(self, other):
        return self.f < other.f


######################################################
# A maze is a grid of size rows X cols
######################################################
class MazeGame:
    def __init__(self, root, maze):
        self.root = root
        self.maze = maze

        self.rows = len(maze) #MAZE WILL BE BOX ONLY VIEW OF IMAGE PROVIDED - ONCE DETERMINED HOW WE ARE BREAKING IT DOWN
        self.cols = len(maze[0])

        #### Start state: (0,0) or top left to start -> should always be updated as current location
        self.agent_pos = (0, 0)

        ### Priority queue to hold delivery locations - will come from text file
        self.locations = []

        #### Goal state: WILL BE BASED ON PRIORITY QUEUE - 0,0 to start for init
        self.goal_pos = (0, 0)

        self.cells = [[Cell(x, y, maze[x][y] == 1) for y in range(self.cols)] for x in range(self.rows)]

        ### ASSIGN PRIORITY AND WARD TO EACH CELL HERE?

        ### Assign the algorithm based on input - 1 for A*, 2 for Dijkstra - A* by default
        self.algorithm = 1

        #### Start state's initial values for f(n) = g(n) + h(n)
        self.cells[self.agent_pos[0]][self.agent_pos[1]].g = 0
        if self.algorithm == 1:
            self.cells[self.agent_pos[0]][self.agent_pos[1]].h = self.Astar_heuristic(self.agent_pos)
            self.cells[self.agent_pos[0]][self.agent_pos[1]].f = self.Astar_heuristic(self.agent_pos)
        elif self.algorithm == 2:
            self.cells[self.agent_pos[0]][self.agent_pos[1]].h = self.Dijkstra_heuristic(self.agent_pos)
            self.cells[self.agent_pos[0]][self.agent_pos[1]].f = self.Dijkstra_heuristic(self.agent_pos)

        # GRAPHICS - TO BE CHANGED LATER
        #### The maze cell size in pixels
        #self.cell_size = 75
        #self.canvas = tk.Canvas(root, width=self.cols * self.cell_size, height=self.rows * self.cell_size, bg='white')
        #self.canvas.pack()

        #self.draw_maze() - DISPLAY GRAPHIC

        #### Display the optimum path in the maze
        self.find_path()

    ############################################################
    #### Manhattan distance - heuristic for A* algorithm
    ############################################################
    def Astar_heuristic(self, pos):
        return (abs(pos[0] - self.goal_pos[0]) + abs(pos[1] - self.goal_pos[1]))

    ############################################################
    #### Dijkstra heuristic - always 0 because Dijkstra only relies on true path cost
    ############################################################
    def Dijkstra_heuristic(self, pos):
        return 0

    ############################################################
    #### Algorithm
    #### Only difference between A* and Dijkstra is the heuristic function that is used
    ############################################################
    def find_path(self):
        open_set = PriorityQueue()

        #### Add the start state to the queue
        #### Adds to the queue based on the prioiryt assigned based on the ward
        open_set.put((self.cells[self.agent_pos[0]][self.agent_pos[1]].priority, self.agent_pos))

        #### Continue exploring until the queue is exhausted
        while not open_set.empty():
            current_cost, current_pos = open_set.get()
            current_cell = self.cells[current_pos[0]][current_pos[1]]

            #### Stop if goal is reached
            if current_pos == self.goal_pos:
                #self.reconstruct_path() -> used only for GUI
                break

            #### Agent goes E, W, N, and S, whenever possible
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                new_pos = (current_pos[0] + dx, current_pos[1] + dy)

                if 0 <= new_pos[0] < self.rows and 0 <= new_pos[1] < self.cols and not self.cells[new_pos[0]][
                    new_pos[1]].is_wall:

                    #### The cost of moving to a new position is 1 unit
                    new_g = current_cell.g + 1

                    if new_g < self.cells[new_pos[0]][new_pos[1]].g:
                        ### Update the path cost g()
                        self.cells[new_pos[0]][new_pos[1]].g = new_g

                        ### Update the heurstic h() based on algorithm being used
                        if self.algorithm == 1:
                            self.cells[new_pos[0]][new_pos[1]].h = self.Astar_heuristic(new_pos)
                        if self.algorithm == 2:
                            self.cells[new_pos[0]][new_pos[1]].h = self.Dijkstra_heuristic(new_pos)

                        ### Update the evaluation function for the cell n: f(n) = g(n) + h(n)
                        self.cells[new_pos[0]][new_pos[1]].f = new_g + self.cells[new_pos[0]][new_pos[1]].h
                        self.cells[new_pos[0]][new_pos[1]].parent = current_cell

                        #### Add the new cell to the priority queue
                        open_set.put((self.cells[new_pos[0]][new_pos[1]].f, new_pos))

    ############################################################
    #### Representation of maze based on breakdown of provided image
    ############################################################
    maze = [
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ]