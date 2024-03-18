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
    #### Initially, all maze cells have g() = inf and h() = 0
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
    def assign_priorities(self):
        #function to check the ward of the cell at the given position and assign priority accordingly
        for y in range(self.cols):
            for x in range(self.rows):
                if self.cells[x][y].ward == "ICU" or self.cells[x][y].ward == "ER":
                    self.cells[x][y].priority = 5
                elif self.cells[x][y].ward == "Oncology" or self.cells[x][y].ward == "Burn":
                    self.cells[x][y].priority = 5
                elif self.cells[x][y].ward == "Surgical" or self.cells[x][y].ward == "Maternity":
                    self.cells[x][y].priority = 4
                elif self.cells[x][y].ward == "Hematology" or self.cells[x][y].ward == "Pediatric":
                    self.cells[x][y].priority = 3
                elif self.cells[x][y].ward == "Medical" or self.cells[x][y].ward == "General":
                    self.cells[x][y].priority = 2
                elif self.cells[x][y].ward == "Admissions" or self.cells[x][y].ward == "Isolation":
                    self.cells[x][y].priority = 1
                elif self.cells[x][y].ward == "Hallway":
                    self.cells[x][y].priority = 0
                else:
                    self.cells[x][y].priority = -1 #if ward not correct - assigns priority -1

    def assign_wards(self):
        x = 0; y = 0
        # rows 0 - 3
        while y < 3:
            self.cells[0][y].ward = "Hallway"
            self.cells[1][y].ward = "Hallway"
            self.cells[2][y].ward = "Hallway"
            self.cells[3][y].ward = "Hallway"
            self.cells[4][y].ward = "Hallway"
            self.cells[5][y].ward = "Hallway"
            y += 1
        y = 3
        while y < 12:
            self.cells[0][y].ward = "Maternity"
            self.cells[1][y].ward = "Maternity"
            self.cells[2][y].ward = "Maternity"
            self.cells[3][y].ward = "Maternity"
            y += 1
        y = 12
        while y < 38:
            self.cells[0][y].ward = "Hallway"
            self.cells[1][y].ward = "Hallway"
            self.cells[2][y].ward = "Hallway"
            self.cells[3][y].ward = "Hallway"
            y += 1

        # rows 4 - 6
        y = 3
        while y < 11:
            self.cells[4][y].ward = "Maternity"
            self.cells[5][y].ward = "Maternity"
            y += 1
        self.cells[4][11].ward = "General"
        self.cells[5][11].ward = "Maternity"
        y = 12
        while y < 29:
            self.cells[4][y].ward = "General"
            self.cells[5][y].ward = "General"
            self.cells[6][y].ward = "General"
            y += 1
        y = 29
        while y < 38:
            self.cells[4][y].ward = "Hallway"
            self.cells[5][y].ward = "Hallway"
            y += 1
        self.cells[6][0].ward = "Hallway"
        self.cells[6][1].ward = "Hallway"
        self.cells[6][2].ward = "Hallway"
        self.cells[6][3].ward = "Maternity"
        self.cells[6][4].ward = "Maternity"
        self.cells[6][5].ward = "Hallway"
        self.cells[6][6].ward = "Maternity"
        self.cells[6][7].ward = "Maternity"
        self.cells[6][8].ward = "General"
        self.cells[6][9].ward = "General"
        self.cells[6][10].ward = "Maternity"
        self.cells[6][11].ward = "Maternity"
        self.cells[6][29].ward = "Hallway"
        self.cells[6][30].ward = "Emergency"
        self.cells[6][31].ward = "Emergency"
        self.cells[6][32].ward = "Emergency"
        self.cells[6][33].ward = "Emergency"
        self.cells[6][34].ward = "Emergency"

        #rows 7 - 10
        y = 0; x = 7
        while x < 26:
            while y < 5:
                self.cells[x][y].ward = "Hallway"
                y += 1
            x += 1
        self.cells[7][5].ward = "Hallway"
        self.cells[7][6].ward = "Hallway"
        y = 7; x = 7
        while x < 11:
            while y < 27:
                self.cells[x][y].ward = "General"
                y += 1
            x += 1
        self.cells[7][27].ward = "General"
        self.cells[7][28].ward = "Hallway"
        self.cells[7][29].ward = "Hallway"
        self.cells[8][5].ward = "Isolation"
        self.cells[8][6].ward = "Isolation"
        self.cells[8][27].ward = "Isolation"
        self.cells[8][28].ward = "Isolation"
        self.cells[8][29].ward = "Hallway"
        x = 7; y = 30
        while x < 12:
            while y < 35:
                self.cells[x][y].ward = "Emergency"
                y += 1
            x += 1
        x = 6; y = 35
        while x < 14:
            while y < 38:
                self.cells[x][y].ward = "Admissions"
                y += 1
            x += 1
        self.cells[9][5].ward = "Hallway"
        self.cells[9][6].ward = "Isolation"
        self.cells[10][5].ward = "Hallway"
        self.cells[10][6].ward = "Isolation"
        self.cells[9][27].ward = "Isolation"
        self.cells[9][28].ward = "Isolation"
        self.cells[9][29].ward = "Hallway"
        self.cells[10][27].ward = "Isolation"
        self.cells[10][28].ward = "Isolation"
        self.cells[10][29].ward = "Hallway"

        #rows 11 - 13
        self.cells[11][5].ward = "Hallway"
        self.cells[11][6].ward = "Hallway"
        self.cells[11][7].ward = "Hallway"
        self.cells[11][8].ward = "Hallway"
        y = 9
        while y < 23:
            self.cells[11][y].ward = "General"
            y += 1
        self.cells[11][23].ward = "Emergency"
        self.cells[11][24].ward = "Emergency"
        self.cells[11][25].ward = "Isolation"
        self.cells[11][26].ward = "Isolation"
        self.cells[11][27].ward = "Isolation"
        self.cells[11][28].ward = "Isolation"
        self.cells[11][29].ward = "Hallway"
        self.cells[12][5].ward = "Oncology"
        self.cells[12][6].ward = "Oncology"
        self.cells[12][7].ward = "Oncology"
        self.cells[12][8].ward = "Oncology"
        self.cells[12][9].ward = "Oncology"
        self.cells[12][10].ward = "General"
        self.cells[12][11].ward = "General"
        self.cells[12][12].ward = "General"
        self.cells[12][13].ward = "General"
        self.cells[12][14].ward = "General"
        self.cells[12][15].ward = "General"
        self.cells[12][16].ward = "Burn"
        self.cells[12][17].ward = "General"
        self.cells[12][18].ward = "General"
        self.cells[12][19].ward = "General"
        self.cells[12][20].ward = "General"
        self.cells[12][21].ward = "General"
        self.cells[12][22].ward = "General"
        self.cells[12][23].ward = "Emergency"
        self.cells[12][24].ward = "Emergency"
        self.cells[12][25].ward = "Isolation"
        self.cells[12][26].ward = "Isolation"
        self.cells[12][27].ward = "Isolation"
        self.cells[12][28].ward = "Isolation"
        self.cells[12][29].ward = "Hallway"
        self.cells[12][30].ward = "ICU"
        self.cells[12][31].ward = "ICU"
        self.cells[12][32].ward = "Admissions"
        self.cells[12][33].ward = "Admissions"
        self.cells[12][34].ward = "Admissions"
        self.cells[13][5].ward = "Oncology"
        self.cells[13][6].ward = "Oncology"
        self.cells[13][7].ward = "Oncology"
        self.cells[13][8].ward = "Oncology"
        self.cells[13][9].ward = "Oncology"
        self.cells[13][10].ward = "General"
        self.cells[13][11].ward = "General"
        self.cells[13][12].ward = "General"
        self.cells[13][13].ward = "General"
        self.cells[13][14].ward = "General"
        self.cells[13][15].ward = "General"
        self.cells[13][16].ward = "Burn"
        self.cells[13][17].ward = "General"
        self.cells[13][18].ward = "General"
        self.cells[13][19].ward = "General"
        self.cells[13][20].ward = "General"
        self.cells[13][21].ward = "General"
        self.cells[13][22].ward = "General"
        self.cells[13][23].ward = "Emergency"
        self.cells[13][24].ward = "Emergency"
        self.cells[13][25].ward = "Oncology"
        self.cells[13][26].ward = "Emergency"
        self.cells[13][27].ward = "Emergency"
        self.cells[13][28].ward = "Emergency"
        self.cells[13][29].ward = "Hallway"
        self.cells[13][30].ward = "ICU"
        self.cells[13][31].ward = "ICU"
        self.cells[13][32].ward = "Admissions"
        self.cells[13][33].ward = "Admissions"
        self.cells[13][34].ward = "Admissions"

        #rows 14 - 16
        self.cells[14][5].ward = "Oncology"
        self.cells[14][6].ward = "Oncology"
        self.cells[14][7].ward = "Oncology"
        self.cells[14][8].ward = "Oncology"
        y = 9
        while y < 18:
            self.cells[14][y].ward = "Burn"
            y += 1
        self.cells[14][18].ward = "General"
        self.cells[14][19].ward = "General"
        self.cells[14][20].ward = "General"
        self.cells[14][21].ward = "General"
        self.cells[14][22].ward = "General"
        self.cells[14][23].ward = "Emergency"
        self.cells[14][24].ward = "Emergency"
        self.cells[14][25].ward = "Oncology"
        self.cells[14][26].ward = "Oncology"
        self.cells[14][27].ward = "Emergency"
        self.cells[14][28].ward = "Emergency"
        self.cells[14][29].ward = "Hallway"
        y = 30
        while y < 38:
            self.cells[14][y].ward = "ICU"
            self.cells[15][y].ward = "ICU"
            self.cells[16][y].ward = "ICU"
            if y > 30:
                self.cells[16][y].ward = "ICU"
                self.cells[17][y].ward = "ICU"
            y += 1
        self.cells[15][5].ward = "Oncology"
        self.cells[15][6].ward = "Oncology"
        self.cells[15][7].ward = "Oncology"
        self.cells[15][8].ward = "Oncology"
        y = 9
        while y < 18:
            self.cells[15][y].ward = "Burn"
            y += 1
        self.cells[15][18].ward = "General"
        self.cells[15][19].ward = "General"
        self.cells[15][20].ward = "General"
        self.cells[15][21].ward = "General"
        self.cells[15][22].ward = "General"
        self.cells[15][23].ward = "Isolation"
        self.cells[15][24].ward = "Isolation"
        self.cells[15][25].ward = "Oncology"
        self.cells[15][26].ward = "Oncology"
        self.cells[15][27].ward = "Oncology"
        self.cells[15][28].ward = "Oncology"
        self.cells[15][29].ward = "Hallway"

        self.cells[16][5].ward = "Oncology"
        self.cells[16][6].ward = "Oncology"
        self.cells[16][7].ward = "Oncology"
        self.cells[16][8].ward = "Oncology"
        y = 9
        while y < 17:
            self.cells[16][y].ward = "Burn"
            y += 1
        self.cells[16][17].ward = "General"
        self.cells[16][18].ward = "General"
        self.cells[16][19].ward = "General"
        self.cells[16][20].ward = "General"
        self.cells[16][21].ward = "General"
        self.cells[16][22].ward = "Hallway"
        self.cells[16][23].ward = "Isolation"
        self.cells[16][24].ward = "Isolation"
        self.cells[16][25].ward = "Oncology"
        self.cells[16][26].ward = "Oncology"
        self.cells[16][27].ward = "Oncology"
        self.cells[16][28].ward = "Oncology"
        self.cells[16][29].ward = "Hallway"

    def __init__(self, root, maze):
        self.root = root
        self.maze = maze

        self.rows = 38
        self.cols = 30
        #### READ FROM INPUT FILE HERE
        delivery_locations = PriorityQueue()

        #### General list to hold delivery locations - to be able to look at all locations
        #### Fill this list from input file - fill priority queue from this list
        self.locations = set()
        for x in self.locations:
            delivery_locations.put(x)

        #### Start state: (0,0) or top left to start -> should always be updated as current location
        self.agent_pos = (0, 0)

        #### Goal state: start with first location from the priority queue
        self.goal_pos = (0,0)
        self.goals_completed = set()

        self.cells = [[Cell(x, y, maze[x][y] == 1) for y in range(self.cols)] for x in range(self.rows)]

        ### ASSIGN WARDS TO EVERY CELL HERE
        self.assign_wards()


        ### Assigning priority to each cell based on its ward
        for cell in self.cells:
            self.assign_priorities(cell[0], cell[1])

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
        while (delivery_locations):
            # get the current ward
            current_ward = self.cells[self.agent_pos[0]][self.agent_pos[1]].ward
            # check if there are anymore deliveries in the list in that ward
            for x in self.locations:
                #if it is in the same ward and has not been visited already
                if self.cells[x[0]][x[1]].ward == current_ward and x not in self.goals_completed:
                    self.goal_pos = x
                # if not delivery locations not yet visited in same ward as current ward, look at priority queue
                else:
                    #check the next element in the priority queue
                    goal = delivery_locations.get()
                    #make sure goal has not yet been visited - if it has, pop until you find oen that hasn't been
                    while goal in self.goals_completed:
                        goal = delivery_locations.get()
                    self.goal_pos = goal
            #now that you have the correct next delivery, find the optimum path using designated algorithm
            self.find_path()
            #once it returns the correct path, repeat to find the next element


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
        open_set.put((0, self.agent_pos))

        #### Continue exploring until the queue is exhausted
        while not open_set.empty():
            current_cost, current_pos = open_set.get()
            current_cell = self.cells[current_pos[0]][current_pos[1]]

            #### Stop if goal is reached
            if current_pos == self.goal_pos:
                #self.reconstruct_path() -> used only for GUI
                self.goals_completed.add(self.goal_pos)
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

                        #### ADD LIST HERE TO KEEP RUNNING TOTAL OF THE PATH THAT IS NOT OVERWRITTEN EVERY TIME YOU CALL THIS METHOD

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