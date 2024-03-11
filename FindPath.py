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