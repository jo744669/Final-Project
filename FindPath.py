########################################
# Jillian O'Connell and Luke Mcginley
# Artificial Intelligence
# May 7, 2024
# Final Project
# Purpose: This project should simulate a robot in a hospital delivering medicine to different patients in different wards
# dependent upon the priority of the destination ward. It should be implemented using A* and Dijkstra's Algorithms.
########################################
import sys
import tkinter as tk
from collections import deque
from queue import PriorityQueue

######################################################
#### A cell stores f(), g() and h() values
#### A cell is either open or part of a wall
######################################################
class Cell:
    #### Initially, all maze cells have g() = inf and h() = 0
    def __init__(self, x, y):
        self.x = x
        self.y = y
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

        self.rows = 30
        self.cols = 38

        #### Start state: (0,0) or top left to start -> should always be updated as current location
        self.agent_pos = (0, 0)

        #### Goal state: start with first location from the priority queue
        self.goal_pos = (0, 0)
        self.goals_completed = set()

        ### Creates cell object for every cell and assigns the wards and priorities to each cell
        self.cells = [[Cell(x, y) for y in range(self.cols)] for x in range(self.rows)]
        self.assign_wards()
        self.assign_priorities()

        ### Read from input file after assigning priorities and wards and buidling cells
        self.locations = set()
        delivery_locations = PriorityQueue()
        self.fullPath = deque()  # keeps track of full path to every location in order
        self.temporaryPath = deque() #keeps track of path from start to goal to build backwards

        #### READ FROM INPUT FILE HERE
        # add all locations to self.locations
        # update self.algorithm based on if using A* or Dijkstra
        self.locations.add((12, 23))
        self.locations.add((15, 21)) #for testing

        #### General list to hold delivery locations - to be able to look at all locations
        #### Fill this list from input file - fill priority queue from this list
        for x in self.locations:
            delivery_locations.put((self.cells[x[0]][x[1]].priority, x))

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

        # GRAPHICS
        #### The maze cell size in pixels
        self.cell_size = 20
        self.canvas = tk.Canvas(root, width=self.cols * self.cell_size, height=self.rows * self.cell_size, bg='white')
        self.canvas.pack()

        self.draw_maze()  #DISPLAY GRAPHIC

        #### Display the optimum path in the maze
        while not delivery_locations.empty():
            # check if there are anymore deliveries in the list in that ward
            # get the current ward
            current_ward = self.cells[self.agent_pos[0]][self.agent_pos[1]].ward
            for x in self.locations:
                #if it is in the same ward and has not been visited already
                if len(self.fullPath) != 0: #not the first iteration bc already found a path
                    current_ward = self.cells[self.agent_pos[0]][self.agent_pos[1]].ward
                if self.cells[x[0]][x[1]].ward == current_ward and x not in self.goals_completed:
                    self.goal_pos = x
                    self.find_path()
                # if not delivery locations not yet visited in same ward as current ward, look at priority queue
                else:
                    #check the next element in the priority queue
                    goal = delivery_locations.get()
                    #make sure goal has not yet been visited - if it has, pop until you find oen that hasn't been
                    while goal in self.goals_completed:
                        goal = delivery_locations.get()
                    self.goal_pos = goal[1]
                    self.find_path()
            while not delivery_locations.empty():
                delivery_locations.get()

        #print the full path found for testing reasons
        #while self.fullPath:
        #   print(self.fullPath.popleft(), end = ", ")

    def assign_priorities(self):
        #function to check the ward of the cell at the given position and assign priority accordingly
        for y in range(self.cols):
            for x in range(self.rows):
                if self.cells[x][y].ward == "ICU" or self.cells[x][y].ward == "Emergency":
                    self.cells[x][y].priority = -5
                elif self.cells[x][y].ward == "Oncology" or self.cells[x][y].ward == "Burn":
                    self.cells[x][y].priority = -5
                elif self.cells[x][y].ward == "Surgical" or self.cells[x][y].ward == "Maternity":
                    self.cells[x][y].priority = -4
                elif self.cells[x][y].ward == "Hematology" or self.cells[x][y].ward == "Pediatric":
                    self.cells[x][y].priority = -3
                elif self.cells[x][y].ward == "Medical" or self.cells[x][y].ward == "General":
                    self.cells[x][y].priority = -2
                elif self.cells[x][y].ward == "Admissions" or self.cells[x][y].ward == "Isolation":
                    self.cells[x][y].priority = -1
                elif self.cells[x][y].ward == "Hallway":
                    self.cells[x][y].priority = 0
                else:
                    self.cells[x][y].priority = 1 #if ward not correct - assigns priority -1

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
        while y < 30:
            self.cells[4][y].ward = "General"
            self.cells[5][y].ward = "General"
            self.cells[6][y].ward = "General"
            y += 1
        y = 30
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
            y = 7
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
            y = 30
        x = 6; y = 35
        while x < 14:
            while y < 38:
                self.cells[x][y].ward = "Admissions"
                y += 1
            x += 1
            y = 35
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
                self.cells[18][y].ward = "ICU"
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

        #rows 17 - 19
        y = 5
        while y < 31:
            self.cells[17][y].ward = "Hallway"
            y += 1
        self.cells[18][5].ward = "Hallway"
        self.cells[18][6].ward = "Isolation"
        self.cells[18][7].ward = "Oncology"
        self.cells[18][8].ward = "Hallway"
        self.cells[18][9].ward = "Hallway"
        self.cells[18][10].ward = "Admissions"
        self.cells[18][11].ward = "Admissions"
        self.cells[18][12].ward = "Admissions"
        self.cells[18][13].ward = "Admissions"
        self.cells[18][14].ward = "Admissions"
        self.cells[18][15].ward = "Hallway"
        self.cells[18][16].ward = "Hallway"
        self.cells[18][17].ward = "Hematology"
        self.cells[18][18].ward = "Hematology"
        self.cells[18][19].ward = "Hematology"
        self.cells[18][20].ward = "Hematology"
        self.cells[18][21].ward = "Hematology"
        self.cells[18][22].ward = "Hallway"
        self.cells[18][23].ward = "Surgical"
        self.cells[18][24].ward = "Surgical"
        self.cells[18][25].ward = "Surgical"
        self.cells[18][26].ward = "Surgical"
        self.cells[18][27].ward = "Oncology"
        self.cells[18][28].ward = "Oncology"
        self.cells[18][29].ward = "Hallway"
        self.cells[18][30].ward = "Hallway"

        self.cells[19][5].ward = "Hallway"
        self.cells[19][6].ward = "Oncology"
        self.cells[19][7].ward = "Oncology"
        self.cells[19][8].ward = "Oncology"
        self.cells[19][9].ward = "Oncology"
        self.cells[19][10].ward = "Admissions"
        self.cells[19][11].ward = "Admissions"
        self.cells[19][12].ward = "Admissions"
        self.cells[19][13].ward = "Admissions"
        self.cells[19][14].ward = "Admissions"
        self.cells[19][15].ward = "Hematology"
        self.cells[19][16].ward = "Hematology"
        self.cells[19][17].ward = "Hematology"
        self.cells[19][18].ward = "Hematology"
        self.cells[19][19].ward = "Hematology"
        self.cells[19][20].ward = "Hematology"
        self.cells[19][21].ward = "Hematology"
        self.cells[19][22].ward = "Hallway"
        self.cells[19][23].ward = "Surgical"
        self.cells[19][24].ward = "Surgical"
        self.cells[19][25].ward = "Surgical"
        self.cells[19][26].ward = "Surgical"
        y = 27
        while y < 36:
            self.cells[19][y].ward = "Oncology"
            self.cells[20][y].ward = "Oncology"
            self.cells[21][y].ward = "Oncology"
            self.cells[22][y].ward = "Oncology"
            self.cells[23][y].ward = "Oncology"
            y += 1

        #rows 20 - 22
        self.cells[20][5].ward = "Hallway"
        self.cells[20][6].ward = "Oncology"
        self.cells[20][7].ward = "Oncology"
        self.cells[20][8].ward = "Oncology"
        self.cells[20][9].ward = "Oncology"
        self.cells[20][10].ward = "Oncology"
        self.cells[20][11].ward = "Oncology"
        self.cells[20][12].ward = "Admissions"
        self.cells[20][13].ward = "Admissions"
        self.cells[20][14].ward = "Admissions"
        self.cells[20][15].ward = "Hematology"
        self.cells[20][16].ward = "Hematology"
        self.cells[20][17].ward = "Hematology"
        self.cells[20][18].ward = "Hematology"
        self.cells[20][19].ward = "Hematology"
        self.cells[20][20].ward = "Pediatric"
        self.cells[20][21].ward = "Pediatric"
        self.cells[20][22].ward = "Hallway"
        self.cells[20][23].ward = "Surgical"
        self.cells[20][24].ward = "Surgical"
        self.cells[20][25].ward = "Surgical"
        self.cells[20][26].ward = "Surgical"
        x = 19
        while x < 30:
            self.cells[x][36].ward = "Hallway"
            self.cells[x][37].ward = "Hallway"
            x += 1
        self.cells[21][5].ward = "Hallway"
        self.cells[21][6].ward = "Oncology"
        self.cells[21][7].ward = "Oncology"
        self.cells[21][8].ward = "Oncology"
        self.cells[21][9].ward = "Oncology"
        self.cells[21][10].ward = "Oncology"
        self.cells[21][11].ward = "Oncology"
        self.cells[21][12].ward = "Pediatric"
        self.cells[21][13].ward = "Pediatric"
        self.cells[21][14].ward = "Hematology"
        self.cells[21][15].ward = "Hematology"
        self.cells[21][16].ward = "Hematology"
        self.cells[21][17].ward = "Hematology"
        self.cells[21][18].ward = "Hematology"
        self.cells[21][19].ward = "Hematology"
        self.cells[21][20].ward = "Pediatric"
        self.cells[21][21].ward = "Pediatric"
        self.cells[21][22].ward = "Hallway"
        self.cells[21][23].ward = "Surgical"
        self.cells[21][24].ward = "Surgical"
        self.cells[21][25].ward = "Surgical"
        self.cells[21][26].ward = "Surgical"

        self.cells[22][5].ward = "Hallway"
        self.cells[22][6].ward = "Oncology"
        self.cells[22][7].ward = "Oncology"
        self.cells[22][8].ward = "Oncology"
        self.cells[22][9].ward = "Oncology"
        self.cells[22][10].ward = "Oncology"
        self.cells[22][11].ward = "Oncology"
        self.cells[22][12].ward = "Pediatric"
        self.cells[22][13].ward = "Pediatric"
        self.cells[22][14].ward = "Hematology"
        self.cells[22][15].ward = "Hematology"
        self.cells[22][16].ward = "Hematology"
        self.cells[22][17].ward = "Hematology"
        self.cells[22][18].ward = "Hematology"
        self.cells[22][19].ward = "Hematology"
        self.cells[22][20].ward = "Pediatric"
        self.cells[22][21].ward = "Pediatric"
        self.cells[22][22].ward = "Hallway"
        self.cells[22][23].ward = "Surgical"
        self.cells[22][24].ward = "Surgical"
        self.cells[22][25].ward = "Surgical"
        self.cells[22][26].ward = "Surgical"

        #rows 23 - 25
        self.cells[23][5].ward = "Hallway"
        self.cells[23][6].ward = "Oncology"
        self.cells[23][7].ward = "Oncology"
        self.cells[23][8].ward = "Oncology"
        self.cells[23][9].ward = "Oncology"
        y = 10
        while y < 22:
            self.cells[23][y].ward = "Pediatric"
            y += 1
        self.cells[23][22].ward = "Hallway"
        self.cells[23][23].ward = "Surgical"
        self.cells[23][24].ward = "Surgical"
        self.cells[23][25].ward = "Surgical"
        self.cells[23][26].ward = "Surgical"

        y = 5
        while y < 24:
            self.cells[24][y].ward = "Hallway"
            self.cells[25][y].ward = "Hallway"
            y += 1
        y = 24
        while y < 36:
            self.cells[24][y].ward = "Surgical"
            self.cells[25][y].ward = "Surgical"
            y += 1
        x = 26; y = 0
        while x < 30:
            while y < 3:
                self.cells[x][y].ward = "Hallway"
                y += 1
            x += 1

        #rows 26 - 29
        self.cells[26][3].ward = "Hallway"
        self.cells[26][4].ward = "Oncology"
        self.cells[26][5].ward = "Oncology"
        x = 26; y = 6
        while x < 30:
            while y < 24:
                self.cells[x][y].ward = "Pediatric"
                y += 1
            x += 1
            y = 6
        x = 26; y = 24
        while x < 30:
            while y < 36:
                self.cells[x][y].ward = "Surgical"
                if y == 25:
                    y = 30
                else:
                    y += 1
            x += 1
            y = 24
        self.cells[26][26].ward = "Medical"
        self.cells[26][27].ward = "Surgical"
        self.cells[26][28].ward = "Medical"
        self.cells[26][29].ward = "Medical"
        x = 27; y = 26
        while x < 30:
            while y < 30:
                self.cells[x][y].ward = "Medical"
                y += 1
            x += 1
            y = 26
        self.cells[27][3].ward = "Hallway"
        self.cells[27][4].ward = "Oncology"
        self.cells[27][5].ward = "Oncology"
        self.cells[28][3].ward = "Hallway"
        self.cells[28][4].ward = "Hallway"
        self.cells[28][5].ward = "Hallway"
        self.cells[29][3].ward = "Isolation"
        self.cells[29][4].ward = "Isolation"
        self.cells[29][5].ward = "Isolation"

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
    #### Function to return possible locations to move to from
    #### current state based on adjacency list
    ############################################################
    def get_neighbors(self, v):
        return self.maze[v]

    ############################################################
    #### Reset g, h, and f values
    #### Before finding next path
    ############################################################
    def reset_values(self, open, closed):
        while len(open):
            cost, node = open.popleft()
            self.cells[node[0]][node[1]].g = float("inf")
            self.cells[node[0]][node[1]].h = 0
            self.cells[node[0]][node[1]].f = float("inf")
        while len(closed):
            node = closed.pop()
            self.cells[node[0]][node[1]].g = float("inf")
            self.cells[node[0]][node[1]].h = 0
            self.cells[node[0]][node[1]].f = float("inf")
        return None

    ############################################################
    #### Algorithm
    #### Only difference between A* and Dijkstra is the heuristic function that is used
    ############################################################
    def find_path(self):
        # list of nodes that have been visited but neighbors of them haven't all been looked at
        open = deque()
        open.append((0, self.agent_pos))
        closed = set()

        #### Continue exploring until the queue is exhausted
        while len(open):
            # get the current position
            current_cost, current_pos = open.popleft() #pop from front of deque
            current_cell = self.cells[current_pos[0]][current_pos[1]]

            # if current node is goal node, reconstruct the path
            if current_pos == self.goal_pos:
                self.goals_completed.add(self.goal_pos)
                self.reset_values(open, closed)
                open.clear()
                closed.clear()
                self.reconstruct_path()
                return self.fullPath

            for neighbor in self.get_neighbors(current_pos):

                if neighbor in closed:
                    continue

                new_g = current_cell.g + 1

                if new_g < self.cells[neighbor[0]][neighbor[1]].g:
                    # update path cost
                    self.cells[neighbor[0]][neighbor[1]].g = new_g

                    # update heuristic
                    if self.algorithm == 1:
                        self.cells[neighbor[0]][neighbor[1]].h = self.Astar_heuristic(neighbor)
                    if self.algorithm == 2:
                        self.cells[neighbor[0]][neighbor[1]].h = self.Dijkstra_heuristic(neighbor)

                    # update evaluation function
                    self.cells[neighbor[0]][neighbor[1]].f = new_g + self.cells[neighbor[0]][neighbor[1]].h
                    self.cells[neighbor[0]][neighbor[1]].parent = current_cell

                    open.append((self.cells[neighbor[0]][neighbor[1]].f, neighbor))
                    sorted(open)

            if current_pos not in closed:
                closed.add(current_pos)

        print('Path does not exist')
        return None

    ############################################################
    #### To rebuild the path and keep a running total of where agent has been
    #### This is also for the GUI part
    ############################################################
    def reconstruct_path(self):
        #rebuilds the path using the temporary and full list
        current_cell = self.cells[self.goal_pos[0]][self.goal_pos[1]]
        self.temporaryPath.clear()
        while current_cell.parent:
            #build the temporary path of just this portion of movement
            self.temporaryPath.appendleft((current_cell.x, current_cell.y))
            if current_cell.x == self.agent_pos[0] and current_cell.y == self.agent_pos[1]:
                break
            current_cell = current_cell.parent

        if self.agent_pos != self.goal_pos:
            print("Path to {}".format(self.goal_pos))

        # add the temporary path to the running total once it is complete
        while self.temporaryPath:
            x, y = self.temporaryPath.popleft()
            self.canvas.create_rectangle(y * self.cell_size, x * self.cell_size, (y + 1) * self.cell_size,
                                         (x + 1) * self.cell_size, fill='black')
            text = {len(self.goals_completed)}
            self.canvas.create_text((self.goal_pos[1] + 0.5) * self.cell_size,
                                    (self.goal_pos[0] + 0.5) * self.cell_size, font=("Purisa", 8),
                                    text=text, fill='white')
            print((x, y), end = ", ")
            self.fullPath.append((x, y))
        print()

        self.agent_pos = self.goal_pos

    ############################################################
    #### This is for the GUI part. No need to modify this unless
    #### GUI changes are needed.
    ############################################################
    def draw_maze(self):
        for x in range(self.rows):
            for y in range(self.cols):
                if self.cells[x][y].ward == "General":
                    color = 'red'
                elif self.cells[x][y].ward == "Maternity":
                    color = 'medium blue'
                elif self.cells[x][y].ward == "Isolation":
                    color = 'sky blue'
                elif self.cells[x][y].ward == "Emergency":
                    color = 'gold'
                elif self.cells[x][y].ward == "Surgical":
                    color = 'salmon1'
                elif self.cells[x][y].ward == "Admissions":
                    color = 'pink4'
                elif self.cells[x][y].ward == "Oncology":
                    color = 'SpringGreen4'
                elif self.cells[x][y].ward == "Pediatric":
                    color = 'SeaGreen1'
                elif self.cells[x][y].ward == "Medical":
                    color = 'chartreuse2'
                elif self.cells[x][y].ward == "Burn":
                    color = 'purple'
                elif self.cells[x][y].ward == "ICU":
                    color = 'chocolate1'
                elif self.cells[x][y].ward == "Hematology":
                    color = 'orange red'
                else:
                    color = 'grey85'

                self.canvas.create_rectangle(y * self.cell_size, x * self.cell_size, (y + 1) * self.cell_size,
                                             (x + 1) * self.cell_size, fill=color)


############################################################
#### Representation of maze based on breakdown of provided image
############################################################
maze = {
        (0, 0): [(0, 1), (1, 0)],  # Column 0
        (1, 0): [(0, 0), (1, 1), (2, 0)],  # Up, Right, Down
        (2, 0): [(1, 0), (2, 1), (3, 0)],
        (3, 0): [(2, 0), (3, 1), (4, 0)],
        (4, 0): [(3, 0), (4, 1), (5, 0)],
        (5, 0): [(4, 0), (5, 1), (6, 0)],
        (6, 0): [(6, 1), (7, 0), (5, 0)],
        (7, 0): [(6, 0), (7, 1), (8, 0)],
        (8, 0): [(7, 0), (8, 1), (9, 0)],
        (9, 0): [(8, 0), (9, 1), (10, 0)],
        (10, 0): [(9, 0), (10, 1), (11, 0)],
        (11, 0): [(10, 0), (11, 1), (12, 0)],
        (12, 0): [(11, 0), (12, 1), (13, 0)],
        (13, 0): [(12, 0), (13, 1), (14, 0)],
        (14, 0): [(13, 0), (14, 1), (15, 0)],
        (15, 0): [(14, 0), (15, 1), (16, 0)],  # Pillars in Hosp. Layout, TBD if wall. Treated as Open Currently
        (16, 0): [(15, 0), (16, 1), (17, 0)],
        (17, 0): [(16, 0), (17, 1), (18, 0)],  # Poss. Wall
        (18, 0): [(17, 0), (18, 1), (19, 0)],
        (19, 0): [(19, 1), (20, 0), (18, 0)],
        (20, 0): [(19, 0), (20, 1), (21, 0)],
        (21, 0): [(20, 0), (21, 1), (22, 0)],
        (22, 0): [(21, 0), (22, 1), (23, 0)],
        (23, 0): [(22, 0), (23, 1), (24, 0)],
        (24, 0): [(23, 0), (24, 1), (25, 0)],
        (25, 0): [(24, 0), (25, 1), (26, 0)],
        (26, 0): [(25, 0), (26, 1), (27, 0)],
        (27, 0): [(26, 0), (27, 1), (28, 0)],
        (28, 0): [(27, 0), (28, 1), (29, 0)],
        (29, 0): [(28, 0), (29, 1)],

        (0, 1): [(0, 0), (0, 2), (1, 1)],  # Column 1
        (1, 1): [(0, 1), (2, 1), (1, 0), (1, 2)],  # Up, Down, Left, Right - Different from top but new format.
        (2, 1): [(1, 1), (3, 1), (2, 0), (2, 2)],
        (3, 1): [(2, 1), (4, 1), (3, 0), (3, 2)],
        (4, 1): [(3, 1), (5, 1), (4, 0), (4, 2)],
        (5, 1): [(4, 1), (6, 1), (5, 0), (5, 2)],
        (6, 1): [(5, 1), (7, 1), (6, 0), (6, 2)],
        (7, 1): [(6, 1), (8, 1), (7, 0), (7, 2)],
        (8, 1): [(7, 1), (9, 1), (8, 0), (8, 2)],
        (9, 1): [(8, 1), (10, 1), (9, 0), (9, 2)],
        (10, 1): [(9, 1), (11, 1), (10, 0), (10, 2)],
        (11, 1): [(10, 1), (12, 1), (11, 0), (11, 2)],
        (12, 1): [(11, 1), (13, 1), (12, 0), (12, 2)],
        (13, 1): [(12, 1), (14, 1), (13, 0), (13, 2)],
        (14, 1): [(13, 1), (15, 1), (14, 0), (14, 2)],
        (15, 1): [(14, 1), (16, 1), (15, 0), (15, 2)],
        (16, 1): [(15, 1), (17, 1), (16, 0), (16, 2)],
        (17, 1): [(16, 1), (18, 1), (17, 0), (17, 2)],
        (18, 1): [(17, 1), (18, 0), (18, 2)],
        (19, 1): [(20, 1), (19, 0), (19, 2)],
        (20, 1): [(19, 1), (21, 1), (20, 0), (20, 2)],
        (21, 1): [(20, 1), (22, 1), (21, 0), (21, 2)],
        (22, 1): [(21, 1), (23, 1), (22, 0), (22, 2)],
        (23, 1): [(22, 1), (24, 1), (23, 0), (23, 2)],
        (24, 1): [(23, 1), (25, 1), (24, 0), (24, 2)],
        (25, 1): [(24, 1), (26, 1), (25, 0), (25, 2)],
        (26, 1): [(25, 1), (27, 1), (26, 0), (26, 2)],
        (27, 1): [(26, 1), (28, 1), (27, 0), (27, 2)],
        (28, 1): [(27, 1), (29, 1), (28, 0), (28, 2)],
        (29, 1): [(28, 1), (29, 0), (29, 2)],
        #  UP    D     L    R
        (0, 2): [(1, 2), (0, 1)],  # Column 2
        (1, 2): [(0, 2), (2, 2), (1, 1)],
        (2, 2): [(1, 2), (3, 2), (2, 1)],
        (3, 2): [(2, 2), (4, 2), (3, 1)],
        (4, 2): [(3, 2), (5, 2), (4, 1)],
        (5, 2): [(4, 2), (5, 1), (6, 2)],
        (6, 2): [(6, 1), (7, 2), (5, 2)],
        (7, 2): [(6, 2), (8, 2), (7, 1), (7, 3)],
        (8, 2): [(7, 2), (9, 2), (8, 1), (8, 3)],
        (9, 2): [(8, 2), (10, 2), (9, 1), (9, 3)],
        (10, 2): [(9, 2), (11, 2), (10, 1), (10, 3)],
        (11, 2): [(10, 2), (12, 2), (11, 1), (11, 3)],
        (12, 2): [(11, 2), (13, 2), (12, 1), (12, 3)],
        (13, 2): [(12, 2), (14, 2), (13, 1), (13, 3)],
        (14, 2): [(13, 2), (15, 2), (14, 1), (14, 3)],
        (15, 2): [(14, 2), (16, 2), (15, 1), (15, 3)],
        (16, 2): [(15, 2), (17, 2), (16, 1), (16, 3)],
        (17, 2): [(16, 2), (18, 2), (17, 1), (17, 3)],
        (18, 2): [(17, 2), (18, 1), (18, 3)],
        (19, 2): [(20, 2), (19, 1)],
        (20, 2): [(19, 2), (21, 2), (20, 1)],
        (21, 2): [(20, 2), (22, 2), (21, 1)],
        (22, 2): [(21, 2), (23, 2), (22, 1)],
        (23, 2): [(22, 2), (24, 2), (23, 1)],
        (24, 2): [(23, 2), (25, 2), (24, 1), (24, 3)],
        (25, 2): [(24, 2), (26, 2), (25, 1), (25, 3)],
        (26, 2): [(25, 2), (27, 2), (26, 1), (26, 3)],
        (27, 2): [(26, 2), (28, 2), (27, 1), (27, 3)],
        (28, 2): [(27, 2), (29, 2), (28, 1), (28, 3)],
        (29, 2): [(28, 2), (29, 1)],
        #  UP    D     L     R
        (0, 3): [(1, 3), (0, 4)],  # Column 3
        (1, 3): [(0, 3), (2, 3), (1, 4)],
        (2, 3): [(1, 3), (3, 3), (2, 4)],
        (3, 3): [(2, 3), (3, 4)],
        (4, 3): [(4, 4)],
        (5, 3): [(6, 3), (5, 4)],
        (6, 3): [(5, 3), (6, 4)],
        (7, 3): [(8, 3), (7, 2), (7, 4)],
        (8, 3): [(7, 3), (9, 3), (8, 2), (8, 4)],
        (9, 3): [(8, 3), (10, 3), (9, 2), (9, 4)],
        (10, 3): [(9, 3), (11, 3), (10, 2), (10, 4)],
        (11, 3): [(10, 3), (12, 3), (11, 2), (11, 4)],
        (12, 3): [(11, 3), (13, 3), (12, 2), (12, 4)],
        (13, 3): [(12, 3), (14, 3), (13, 2), (13, 4)],
        (14, 3): [(13, 3), (15, 3), (14, 2), (14, 4)],
        (15, 3): [(14, 3), (16, 3), (15, 2), (15, 4)],
        (16, 3): [(15, 3), (17, 3), (16, 2), (16, 4)],
        (17, 3): [(16, 3), (18, 3), (17, 2), (17, 4)],
        (18, 3): [(17, 3), (19, 3), (18, 2), (18, 4)],
        (19, 3): [(18, 3), (20, 3), (19, 4)],
        (20, 3): [(19, 3), (21, 3), (20, 4)],
        (21, 3): [(20, 3), (22, 3), (21, 4)],
        (22, 3): [(21, 3), (23, 3), (22, 4)],
        (23, 3): [(22, 3), (24, 3), (23, 4)],
        (24, 3): [(23, 3), (25, 3), (24, 2), (24, 4)],
        (25, 3): [(24, 3), (26, 3), (25, 2), (25, 4)],
        (26, 3): [(25, 3), (27, 3), (26, 2)],
        (27, 3): [(26, 3), (28, 3), (27, 2)],
        (28, 3): [(27, 3), (28, 2), (28, 4)],
        (29, 3): [(29, 4)],

        #   UP    D     L     R
        (0, 4): [(1, 4), (0, 3), (0, 5)],  # Column 4
        (1, 4): [(0, 4), (2, 4), (1, 3), (1, 5)],
        (2, 4): [(1, 4), (3, 4), (2, 3), (2, 5)],
        (3, 4): [(2, 4), (3, 3), (3, 5)],
        (4, 4): [(4, 3), (4, 5)],
        (5, 4): [(6, 4), (5, 3), (5, 5)],
        (6, 4): [(5, 4), (6, 3)],
        (7, 4): [(8, 4), (7, 3), (7, 5)],
        (8, 4): [(7, 4), (9, 4), (8, 3)],
        (9, 4): [(8, 4), (10, 4), (9, 3), (9, 5)],
        (10, 4): [(9, 4), (11, 4), (10, 3), (10, 5)],
        (11, 4): [(10, 4), (12, 4), (11, 3), (11, 5)],
        (12, 4): [(11, 4), (13, 4), (12, 3)],
        (13, 4): [(12, 4), (14, 4), (13, 3)],
        (14, 4): [(13, 4), (15, 4), (14, 3)],
        (15, 4): [(14, 4), (16, 4), (15, 3)],
        (16, 4): [(15, 4), (17, 4), (16, 3)],
        (17, 4): [(16, 4), (18, 4), (17, 3), (17, 5)],
        (18, 4): [(17, 4), (19, 4), (18, 3), (18, 5)],
        (19, 4): [(18, 4), (20, 4), (19, 3), (19, 5)],
        (20, 4): [(19, 4), (21, 4), (20, 3), (20, 5)],
        (21, 4): [(20, 4), (22, 4), (21, 3), (21, 5)],
        (22, 4): [(21, 4), (23, 4), (22, 3), (22, 5)],
        (23, 4): [(22, 4), (24, 4), (23, 3), (23, 5)],
        (24, 4): [(23, 4), (25, 4), (24, 3), (24, 5)],
        (25, 4): [(24, 4), (25, 3), (25, 5)],
        (26, 4): [(27, 4), (26, 5)],
        (27, 4): [(26, 4), (27, 5)],
        (28, 4): [(29, 4), (28, 3), (28, 5)],
        (29, 4): [(28, 4), (29, 3)],
        #   UP     D      L       R
        (0, 5): [(1, 5), (0, 4), (0, 6)],  # Column 5
        (1, 5): [(0, 5), (2, 5), (1, 4), (1, 6)],
        (2, 5): [(1, 5), (3, 5), (2, 4), (2, 6)],
        (3, 5): [(2, 5), (4, 5), (3, 4), (3, 6)],
        (4, 5): [(3, 5), (5, 5), (4, 4), (4, 6)],
        (5, 5): [(4, 5), (6, 5), (5, 4)],
        (6, 5): [(5, 5), (7, 5)],
        (7, 5): [(6, 5), (8, 5), (7, 4), (7, 6)],
        (8, 5): [(7, 5), (8, 6)],
        (9, 5): [(10, 5), (9, 4)],
        (10, 5): [(9, 5), (11, 5), (10, 4)],
        (11, 5): [(10, 5), (11, 4), (11, 6)],
        (12, 5): [(13, 5), (12, 6)],
        (13, 5): [(12, 5), (14, 5), (13, 6)],
        (14, 5): [(13, 5), (15, 5), (14, 6)],
        (15, 5): [(14, 5), (16, 5), (15, 6)],
        (16, 5): [(15, 5), (16, 6)],
        (17, 5): [(18, 5), (17, 4), (17, 6)],
        (18, 5): [(17, 5), (19, 5), (18, 4)],
        (19, 5): [(18, 5), (20, 5), (19, 4)],
        (20, 5): [(19, 5), (21, 5), (20, 4)],
        (21, 5): [(20, 5), (22, 5), (21, 4)],
        (22, 5): [(21, 5), (23, 5), (22, 4)],
        (23, 5): [(22, 5), (24, 5), (23, 4)],
        (24, 5): [(23, 5), (25, 5), (24, 4), (24, 6)],
        (25, 5): [(24, 5), (26, 5), (25, 4), (25, 6)],
        (26, 5): [(25, 5), (27, 5), (26, 4)],
        (27, 5): [(26, 5), (27, 4)],
        (28, 5): [(29, 5), (28, 4)],
        (29, 5): [(28, 5)],

        #   UP    D      L     R
        (0, 6): [(1, 6), (0, 5)],  # Column 6
        (1, 6): [(0, 6), (2, 6), (1, 5), (1, 7)],
        (2, 6): [(1, 6), (3, 6), (2, 5)],
        (3, 6): [(2, 6), (4, 6), (3, 5), (3, 7)],
        (4, 6): [(3, 6), (5, 6), (4, 5), (4, 7)],
        (5, 6): [(4, 6), (6, 6)],
        (6, 6): [(5, 6)],
        (7, 6): [(8, 6), (7, 5), (7, 7)],
        (8, 6): [(7, 6), (8, 5)],
        (9, 6): [(10, 6)],
        (10, 6): [(9, 6), (11, 6)],
        (11, 6): [(10, 6), (12, 6), (11, 5), (11, 7)],
        (12, 6): [(11, 6), (13, 6), (12, 5)],
        (13, 6): [(12, 6), (14, 6), (13, 5)],
        (14, 6): [(13, 6), (15, 6), (14, 5), (14, 7)],
        (15, 6): [(14, 6), (16, 6), (15, 5)],
        (16, 6): [(15, 6), (17, 6), (16, 5)],
        (17, 6): [(16, 6), (18, 6), (17, 5), (17, 7)],
        (18, 6): [(17, 6)],
        (19, 6): [(20, 6), (19, 7)],
        (20, 6): [(19, 6), (21, 6), (20, 7)],
        (21, 6): [(20, 6), (21, 7)],
        (22, 6): [(23, 6), (22, 7)],
        (23, 6): [(22, 6), (23, 5), (23, 7)],
        (24, 6): [(25, 6), (24, 5), (24, 7)],
        (25, 6): [(24, 6), (26, 6), (25, 5), (25, 7)],
        (26, 6): [(25, 6), (27, 6), (26, 7)],
        (27, 6): [(26, 6), (27, 7)],
        (28, 6): [(29, 6), (28, 7)],
        (29, 6): [(28, 6), (29, 7)],

        #   UP    D     L     R
        (0, 7): [(1, 7), (0, 8)],  # Column 7
        (1, 7): [(0, 7), (2, 7), (1, 6), (1, 8)],
        (2, 7): [(1, 7), (3, 7), (2, 8)],
        (3, 7): [(2, 7), (4, 7), (3, 6), (3, 8)],
        (4, 7): [(3, 7), (4, 6), (4, 8)],
        (5, 7): [(6, 7), (5, 8)],
        (6, 7): [(5, 7)],
        (7, 7): [(6, 7), (8, 7), (7, 6), (7, 8)],
        (8, 7): [(7, 7), (9, 7), (8, 8)],
        (9, 7): [(8, 7), (10, 7), (9, 8)],
        (10, 7): [(9, 7), (11, 7), (10, 8)],
        (11, 7): [(10, 7), (12, 7), (11, 6), (11, 8)],
        (12, 7): [(11, 7), (13, 7)],
        (13, 7): [(12, 7), (14, 7)],
        (14, 7): [(13, 7), (15, 7), (14, 6), (14, 8)],
        (15, 7): [(14, 7), (16, 7)],
        (16, 7): [(15, 7), (17, 7)],
        (17, 7): [(16, 7), (17, 6), (17, 8)],
        (18, 7): [(19, 7)],
        (19, 7): [(18, 7), (20, 7), (19, 6), (19, 8)],
        (20, 7): [(19, 7), (21, 7), (20, 6), (20, 8)],
        (21, 7): [(20, 7), (21, 6), (21, 8)],
        (22, 7): [(23, 7), (22, 6), (22, 8)],
        (23, 7): [(22, 7), (23, 6), (23, 8)],
        (24, 7): [(25, 7), (24, 6), (24, 8)],
        (25, 7): [(24, 7), (26, 7), (25, 6), (25, 8)],
        (26, 7): [(25, 7), (27, 7), (26, 6)],
        (27, 7): [(26, 7), (27, 6), (27, 8)],
        (28, 7): [(29, 7), (28, 6), (28, 8)],
        (29, 7): [(28, 7), (29, 6), (29, 8)],

        #   UP    D     L     R
        (0, 8): [(1, 8), (0, 7)],  # Column 8
        (1, 8): [(0, 8), (2, 8), (1, 7)],
        (2, 8): [(1, 8), (3, 8), (2, 7), (2, 9)],
        (3, 8): [(2, 8), (4, 8), (3, 7), (3, 9)],
        (4, 8): [(3, 8), (5, 8), (4, 7), (4, 9)],
        (5, 8): [(4, 8), (6, 8), (5, 7), (5, 9)],
        (6, 8): [(5, 8), (7, 8), (6, 9)],
        (7, 8): [(6, 8), (7, 7), (7, 9)],
        (8, 8): [(9, 8), (8, 7)],
        (9, 8): [(8, 8), (10, 8), (9, 7)],
        (10, 8): [(9, 8), (10, 7)],
        (11, 8): [(12, 8), (11, 7), (11, 9)],
        (12, 8): [(11, 8), (13, 8), (12, 9)],
        (13, 8): [(12, 8), (13, 9)],
        (14, 8): [(15, 8), (14, 7)],
        (15, 8): [(14, 8), (16, 8)],
        (16, 8): [(15, 8), (17, 8)],
        (17, 8): [(16, 8), (18, 8), (17, 7), (17, 9)],
        (18, 8): [(17, 8), (18, 9)],
        (19, 8): [(19, 7)],
        (20, 8): [(21, 8), (20, 7)],
        (21, 8): [(20, 8), (21, 7), (21, 9)],
        (22, 8): [(23, 8), (22, 7), (22, 9)],
        (23, 8): [(22, 8), (23, 7), (23, 9)],
        (24, 8): [(25, 8), (24, 7), (24, 9)],
        (25, 8): [(24, 8), (26, 8), (25, 7), (25, 9)],
        (26, 8): [(25, 8), (27, 8), (26, 9)],
        (27, 8): [(26, 8), (28, 8), (27, 7)],
        (28, 8): [(27, 8), (29, 8), (28, 7), (28, 9)],
        (29, 8): [(28, 8), (29, 7), (29, 9)],

        #   UP      D     L     R
        (0, 9): [(1, 9), (0, 10)],  # Column 9
        (1, 9): [(0, 9), (2, 9), (1, 10)],
        (2, 9): [(1, 9), (3, 9), (2, 8), (2, 10)],
        (3, 9): [(2, 9), (4, 9), (3, 8), (3, 10)],
        (4, 9): [(3, 9), (5, 9), (4, 8), (4, 10)],
        (5, 9): [(4, 9), (6, 9), (5, 8), (5, 10)],
        (6, 9): [(5, 9), (7, 9), (6, 8)],
        (7, 9): [(6, 9), (8, 9), (7, 8), (7, 10)],
        (8, 9): [(7, 9), (8, 10)],
        (9, 9): [(10, 9), (9, 10)],
        (10, 9): [(9, 9), (10, 10)],
        (11, 9): [(12, 9), (11, 8), (11, 10)],
        (12, 9): [(11, 9), (13, 9), (12, 8), (12, 10)],
        (13, 9): [(12, 9), (13, 8), (13, 10)],
        (14, 9): [(15, 9), (14, 10)],
        (15, 9): [(14, 9), (16, 9), (15, 10)],
        (16, 9): [(15, 9), (17, 9), (16, 10)],
        (17, 9): [(16, 9), (18, 9), (17, 8), (17, 10)],
        (18, 9): [(17, 9), (19, 9), (18, 8)],
        (19, 9): [(18, 9), (20, 9)],
        (20, 9): [(19, 9), (21, 9), (20, 10)],
        (21, 9): [(20, 9), (22, 9), (21, 8)],
        (22, 9): [(21, 9), (23, 9), (22, 8)],
        (23, 9): [(22, 9), (23, 8)],
        (24, 9): [(25, 9), (24, 8), (24, 10)],
        (25, 9): [(24, 9), (26, 9), (25, 8), (25, 10)],
        (26, 9): [(25, 9), (27, 9), (26, 8)],
        (27, 9): [(26, 9)],
        (28, 9): [(29, 9), (28, 8)],
        (29, 9): [(28, 9), (29, 8)],

        #   UP       D      L     R
        (0, 10): [(1, 10), (0, 9), (0, 11)],  # Column 10
        (1, 10): [(0, 10), (2, 10), (1, 9), (1, 11)],
        (2, 10): [(1, 10), (3, 10), (2, 9), (2, 11)],
        (3, 10): [(2, 10), (4, 10), (3, 9), (3, 11)],
        (4, 10): [(3, 10), (4, 9)],
        (5, 10): [(6, 10), (5, 9), (5, 11)],
        (6, 10): [(5, 10), (6, 11)],
        (7, 10): [(7, 9), (7, 11)],
        (8, 10): [(8, 9)],
        (9, 10): [(10, 10), (9, 9)],
        (10, 10): [(9, 10), (11, 10), (10, 9)],
        (11, 10): [(10, 10), (12, 10), (11, 9), (11, 11)],
        (12, 10): [(12, 9), (11, 10), (13, 10)],
        (13, 10): [(13, 9), (12, 10)],
        (14, 10): [(15, 10), (14, 9)],
        (15, 10): [(14, 10), (16, 10), (15, 9), (15, 11)],
        (16, 10): [(15, 10), (16, 9), (16, 11)],
        (17, 10): [(17, 9), (17, 11)],
        (18, 10): [(19, 10), (18, 11)],
        (19, 10): [(18, 10), (19, 11)],
        (20, 10): [(21, 10), (20, 9), (20, 11)],
        (21, 10): [(20, 10), (22, 10), (21, 11)],
        (22, 10): [(21, 10), (22, 11)],
        (23, 10): [(23, 11)],
        (24, 10): [(25, 10), (24, 9), (24, 11)],
        (25, 10): [(24, 10), (25, 9), (25, 11)],
        (26, 10): [(27, 10), (26, 11)],
        (27, 10): [(26, 10), (28, 10), (27, 11)],
        (28, 10): [(27, 10), (29, 10), (28, 11)],
        (29, 10): [(28, 10), (29, 11)],

        #   UP       D      L     R
        (0, 11): [(1, 11), (0, 10)],  # Column 11
        (1, 11): [(0, 11), (2, 11), (1, 10)],
        (2, 11): [(1, 11), (3, 11), (2, 10)],
        (3, 11): [(2, 11), (3, 10)],
        (4, 11): [(4, 12)],
        (5, 11): [(6, 11), (5, 10)],
        (6, 11): [(5, 11), (6, 10)],
        (7, 11): [(7, 10), (7, 12)],
        (8, 11): [(9, 11), (8, 12)],
        (9, 11): [(8, 11), (10, 11), (9, 12)],
        (10, 11): [(9, 11), (10, 12)],
        (11, 11): [(11, 10), (11, 12)],
        (12, 11): [(13, 11), (12, 12)],
        (13, 11): [(12, 11), (13, 12)],
        (14, 11): [(15, 11), (14, 12)],
        (15, 11): [(14, 11), (15, 10), (15, 12)],
        (16, 11): [(16, 10)],
        (17, 11): [(18, 11), (17, 10), (17, 12)],
        (18, 11): [(17, 11), (19, 11), (18, 10)],
        (19, 11): [(18, 11), (19, 10)],
        (20, 11): [(21, 11), (20, 10)],
        (21, 11): [(20, 11), (22, 11), (21, 10)],
        (22, 11): [(21, 11), (22, 10)],
        (23, 11): [(24, 11), (23, 10)],
        (24, 11): [(23, 11), (25, 11), (24, 10), (24, 12)],
        (25, 11): [(24, 11), (26, 11), (25, 10), (25, 12)],
        (26, 11): [(25, 11), (27, 11), (26, 10)],
        (27, 11): [(26, 11), (28, 11), (27, 10), (27, 12)],
        (28, 11): [(27, 11), (29, 11), (28, 10), (28, 12)],
        (29, 11): [(28, 11), (29, 10), (29, 12)],

        #     UP       D      L     R
        (0, 12): [(1, 12), (0, 13)],  # Column 12
        (1, 12): [(0, 12), (2, 12), (1, 13)],
        (2, 12): [(1, 12), (3, 12), (2, 13)],
        (3, 12): [(2, 12), (4, 12), (3, 13)],
        (4, 12): [(3, 12), (5, 12), (4, 11)],
        (5, 12): [(4, 12), (6, 12)],
        (6, 12): [(5, 12), (7, 12)],
        (7, 12): [(6, 12), (8, 12), (7, 11), (7, 13)],
        (8, 12): [(7, 12), (9, 12), (8, 11), (8, 13)],
        (9, 12): [(8, 12), (10, 12), (9, 11), (9, 13)],
        (10, 12): [(9, 12), (11, 12), (10, 11), (10, 13)],
        (11, 12): [(10, 12), (12, 12), (11, 11), (11, 13)],
        (12, 12): [(11, 12), (13, 12), (12, 11)],
        (13, 12): [(12, 12), (13, 11)],
        (14, 12): [(15, 12), (14, 11), (14, 13)],
        (15, 12): [(14, 12), (16, 12), (15, 11), (15, 13)],
        (16, 12): [(15, 12), (16, 13)],
        (17, 12): [(18, 12), (17, 11), (17, 13)],
        (18, 12): [(17, 12), (19, 12), (18, 13)],
        (19, 12): [(18, 12), (20, 12), (19, 13)],
        (20, 12): [(19, 12), (20, 13)],
        (21, 12): [(21, 13)],
        (22, 12): [(23, 12), (22, 13)],
        (23, 12): [(22, 12)],
        (24, 12): [(25, 12), (24, 11), (24, 13)],
        (25, 12): [(24, 12), (25, 11), (25, 13)],
        (26, 12): [(27, 12), (26, 13)],
        (27, 12): [(26, 12), (27, 11)],
        (28, 12): [(29, 12), (28, 11)],
        (29, 12): [(28, 12), (29, 11)],

        #     UP       D      L     R
        (0, 13): [(1, 13), (0, 12), (0, 14)],  # Column 13
        (1, 13): [(0, 13), (2, 13), (1, 12), (1, 14)],
        (2, 13): [(1, 13), (3, 13), (2, 12), (2, 14)],
        (3, 13): [(2, 13), (3, 12), (3, 14)],
        (4, 13): [(5, 13), (4, 14)],
        (5, 13): [(4, 13), (6, 13), (5, 14)],
        (6, 13): [(5, 13), (6, 14)],
        (7, 13): [(8, 13), (7, 12), (7, 14)],
        (8, 13): [(7, 13), (9, 13), (8, 12), (8, 14)],
        (9, 13): [(8, 13), (10, 13), (9, 12), (9, 14)],
        (10, 13): [(9, 13), (11, 13), (10, 12), (10, 14)],
        (11, 13): [(10, 13), (12, 13), (11, 12), (11, 14)],
        (12, 13): [(11, 13), (13, 13)],
        (13, 13): [(12, 13)],
        (14, 13): [(15, 13), (14, 12), (14, 14)],
        (15, 13): [(14, 13), (16, 13), (15, 12), (15, 14)],
        (16, 13): [(15, 13), (16, 12), (16, 14)],
        (17, 13): [(17, 12), (17, 14)],
        (18, 13): [(19, 13), (18, 12), (18, 14)],
        (19, 13): [(18, 13), (20, 13), (19, 12), (19, 14)],
        (20, 13): [(19, 13), (20, 12), (20, 14)],
        (21, 13): [(22, 13), (21, 12)],
        (22, 13): [(21, 13), (23, 13), (22, 12)],
        (23, 13): [(22, 13), (24, 13), (23, 14)],
        (24, 13): [(23, 13), (25, 13), (24, 12), (24, 14)],
        (25, 13): [(24, 13), (26, 13), (25, 12), (25, 14)],
        (26, 13): [(25, 13), (27, 13), (26, 12), (26, 14)],
        (27, 13): [(26, 13), (27, 14)],
        (28, 13): [(29, 13), (28, 14)],
        (29, 13): [(28, 13), (29, 14)],

        #     UP      D      L     R
        (0, 14): [(1, 14), (0, 13), (0, 15)],  # Column 14
        (1, 14): [(0, 14), (2, 14), (1, 13), (1, 15)],
        (2, 14): [(1, 14), (3, 14), (2, 13), (2, 15)],
        (3, 14): [(2, 14), (3, 13), (3, 15)],
        (4, 14): [(5, 14), (4, 13), (4, 15)],
        (5, 14): [(4, 14), (6, 14), (5, 13), (5, 15)],
        (6, 14): [(5, 14), (7, 14), (6, 13), (6, 15)],
        (7, 14): [(6, 14), (8, 14), (7, 13), (7, 15)],
        (8, 14): [(7, 14), (9, 14), (8, 13), (8, 15)],
        (9, 14): [(8, 14), (10, 14), (9, 13), (9, 15)],
        (10, 14): [(9, 14), (11, 14), (10, 13), (10, 15)],
        (11, 14): [(10, 14), (11, 13), (11, 15)],
        (12, 14): [(13, 14), (12, 15)],
        (13, 14): [(12, 14), (13, 15)],
        (14, 14): [(15, 14), (14, 13), (14, 15)],
        (15, 14): [(14, 14), (16, 14), (15, 13), (15, 15)],
        (16, 14): [(15, 14), (16, 13), (16, 15)],
        (17, 14): [(17, 13), (17, 15)],
        (18, 14): [(19, 14), (18, 13)],
        (19, 14): [(18, 14), (20, 14), (19, 13)],
        (20, 14): [(19, 14), (20, 13)],
        (21, 14): [(22, 14), (21, 15)],
        (22, 14): [(21, 14), (23, 14), (22, 15)],
        (23, 14): [(22, 14), (24, 14), (23, 13), (23, 15)],
        (24, 14): [(23, 14), (25, 14), (24, 13), (24, 15)],
        (25, 14): [(24, 14), (25, 13), (25, 15)],
        (26, 14): [(27, 14), (26, 13)],
        (27, 14): [(26, 14), (27, 13), (27, 15)],
        (28, 14): [(29, 14), (28, 13), (28, 15)],
        (29, 14): [(28, 14), (29, 13), (29, 15)],

        #     UP      D      L     R
        (0, 15): [(1, 15), (0, 14), (0, 16)],  # Column 15
        (1, 15): [(0, 15), (2, 15), (1, 14), (1, 16)],
        (2, 15): [(1, 15), (3, 15), (2, 14), (2, 16)],
        (3, 15): [(2, 15), (3, 14), (3, 16)],
        (4, 15): [(5, 15), (4, 14)],
        (5, 15): [(4, 15), (6, 15), (5, 14)],
        (6, 15): [(5, 15), (6, 14)],
        (7, 15): [(8, 15), (7, 14), (7, 16)],
        (8, 15): [(7, 15), (9, 15), (8, 14)],
        (9, 15): [(8, 15), (10, 15), (9, 14), (9, 16)],
        (10, 15): [(9, 15), (11, 15), (10, 14)],
        (11, 15): [(10, 15), (12, 15), (11, 14), (11, 16)],
        (12, 15): [(11, 15), (13, 15), (12, 14)],
        (13, 15): [(12, 15), (13, 14)],
        (14, 15): [(15, 15), (14, 14), (14, 16)],
        (15, 15): [(14, 15), (16, 15), (15, 14), (15, 16)],
        (16, 15): [(15, 15), (17, 15), (16, 14), (16, 16)],
        (17, 15): [(16, 15), (18, 15), (17, 14), (17, 16)],
        (18, 15): [(17, 15), (18, 16)],
        (19, 15): [(20, 15), (19, 16)],
        (20, 15): [(19, 15), (20, 16)],
        (21, 15): [(22, 15), (21, 14)],
        (22, 15): [(21, 15), (23, 15), (22, 14)],
        (23, 15): [(22, 15), (24, 15), (23, 14), (23, 16)],
        (24, 15): [(23, 15), (25, 15), (24, 14), (24, 16)],
        (25, 15): [(24, 15), (26, 15), (25, 14), (25, 16)],
        (26, 15): [(25, 15), (27, 15)],
        (27, 15): [(26, 15), (28, 15), (27, 14)],
        (28, 15): [(27, 15), (29, 15), (28, 14)],
        (29, 15): [(28, 15), (29, 14)],

        #     UP      D      L     R
        (0, 16): [(1, 16), (0, 15), (0, 17)],  # Column 16
        (1, 16): [(0, 16), (2, 16), (1, 15), (1, 17)],
        (2, 16): [(1, 16), (3, 16), (2, 15), (2, 17)],
        (3, 16): [(2, 16), (3, 15), (3, 17)],
        (4, 16): [(5, 16), (4, 17)],
        (5, 16): [(4, 16), (6, 16), (5, 17)],
        (6, 16): [(5, 16), (6, 17)],
        (7, 16): [(7, 15), (7, 17)],
        (8, 16): [(9, 16), (8, 17)],
        (9, 16): [(8, 16), (10, 16), (9, 15), (9, 17)],
        (10, 16): [(9, 16), (10, 17)],
        (11, 16): [(12, 16), (11, 15), (11, 17)],
        (12, 16): [(11, 16), (13, 16)],
        (13, 16): [(12, 16), (14, 16)],
        (14, 16): [(13, 16), (15, 16), (14, 15), (14, 17)],
        (15, 16): [(14, 16), (16, 16), (15, 15)],
        (16, 16): [(15, 16), (16, 15)],
        (17, 16): [(18, 16), (17, 15), (17, 17)],
        (18, 16): [(17, 16), (18, 15)],
        (19, 16): [(20, 16), (19, 15), (19, 17)],
        (20, 16): [(19, 16), (20, 15), (20, 17)],
        (21, 16): [(21, 17)],
        (22, 16): [(22, 17)],
        (23, 16): [(24, 16), (23, 15)],
        (24, 16): [(23, 16), (25, 16), (24, 15), (24, 17)],
        (25, 16): [(24, 16), (26, 16), (25, 15), (25, 17)],
        (26, 16): [(25, 16), (27, 16)],
        (27, 16): [(26, 16), (28, 16), (27, 17)],
        (28, 16): [(27, 16), (29, 16), (28, 17)],
        (29, 16): [(28, 16), (29, 17)],

        #     UP     D     L      R
        (0, 17): [(1, 17), (0, 16), (0, 18)],  # Column 17
        (1, 17): [(0, 17), (2, 17), (1, 16), (1, 18)],
        (2, 17): [(1, 17), (3, 17), (2, 16), (2, 18)],
        (3, 17): [(2, 17), (3, 16), (3, 18)],
        (4, 17): [(5, 17), (4, 16), (4, 18)],
        (5, 17): [(4, 17), (6, 17), (5, 16), (5, 18)],
        (6, 17): [(5, 17), (7, 17), (6, 16), (6, 18)],
        (7, 17): [(6, 17), (7, 16), (7, 18)],
        (8, 17): [(9, 17), (8, 16)],
        (9, 17): [(8, 17), (10, 17), (9, 16)],
        (10, 17): [(9, 17), (10, 16)],
        (11, 17): [(12, 17), (11, 16), (11, 18)],
        (12, 17): [(11, 17), (13, 17)],
        (13, 17): [(12, 17)],
        (14, 17): [(15, 17), (14, 16)],
        (15, 17): [(14, 17)],
        (16, 17): [(16, 18)],
        (17, 17): [(18, 17), (17, 16), (17, 18)],
        (18, 17): [(17, 17), (19, 17), (18, 18)],
        (19, 17): [(18, 17), (20, 17), (19, 16), (19, 18)],
        (20, 17): [(19, 17), (21, 17), (20, 16), (20, 18)],
        (21, 17): [(20, 17), (22, 17), (21, 16), (21, 18)],
        (22, 17): [(21, 17), (22, 16), (22, 18)],
        (23, 17): [(24, 17), (23, 18)],
        (24, 17): [(23, 17), (25, 17), (24, 16), (24, 18)],
        (25, 17): [(24, 17), (26, 17), (25, 16), (25, 18)],
        (26, 17): [(25, 17), (27, 17), (26, 18)],
        (27, 17): [(26, 17), (27, 16)],
        (28, 17): [(29, 17), (28, 16)],
        (29, 17): [(28, 17), (29, 16)],

        #     UP     D     L      R
        (0, 18): [(1, 18), (0, 17), (0, 19)],  # Column 18
        (1, 18): [(0, 18), (2, 18), (1, 17), (1, 19)],
        (2, 18): [(1, 18), (3, 18), (2, 17), (2, 19)],
        (3, 18): [(2, 18), (3, 17), (3, 19)],
        (4, 18): [(5, 18), (4, 17)],
        (5, 18): [(4, 18), (6, 18), (5, 17)],
        (6, 18): [(5, 18), (6, 17)],
        (7, 18): [(8, 18), (7, 17), (7, 19)],
        (8, 18): [(7, 18), (9, 18)],
        (9, 18): [(8, 18), (10, 18)],
        (10, 18): [(9, 18), (11, 18)],
        (11, 18): [(10, 18), (12, 18), (11, 17), (11, 19)],
        (12, 18): [(11, 18), (13, 18), (12, 19)],
        (13, 18): [(12, 18), (13, 19)],
        (14, 18): [(15, 18), (14, 19)],
        (15, 18): [(14, 18), (15, 19)],
        (16, 18): [(16, 17), (16, 19)],
        (17, 18): [(17, 17), (17, 19)],
        (18, 18): [(19, 18), (18, 17), (18, 19)],
        (19, 18): [(18, 18), (20, 18), (19, 17), (19, 19)],
        (20, 18): [(19, 18), (21, 18), (20, 17), (20, 19)],
        (21, 18): [(20, 18), (22, 18), (21, 17), (21, 19)],
        (22, 18): [(21, 18), (22, 17), (22, 19)],
        (23, 18): [(24, 18), (23, 17)],
        (24, 18): [(23, 18), (25, 18), (24, 17), (24, 19)],
        (25, 18): [(24, 18), (26, 18), (25, 17), (25, 19)],
        (26, 18): [(25, 18), (27, 18), (26, 17), (26, 19)],
        (27, 18): [(26, 18), (27, 19)],
        (28, 18): [(29, 18), (28, 19)],
        (29, 18): [(28, 18), (29, 19)],

        #     UP     D     L      R
        (0, 19): [(1, 19), (0, 18), (0, 20)],  # Column 19
        (1, 19): [(0, 19), (2, 19), (1, 18), (1, 20)],
        (2, 19): [(1, 19), (3, 19), (2, 18), (2, 20)],
        (3, 19): [(2, 19), (3, 18), (3, 20)],
        (4, 19): [(5, 19), (4, 20)],
        (5, 19): [(4, 19), (6, 19), (5, 20)],
        (6, 19): [(5, 19), (7, 19), (6, 20)],
        (7, 19): [(6, 19), (7, 18), (7, 20)],
        (8, 19): [(9, 19), (8, 20)],
        (9, 19): [(8, 19), (10, 19), (9, 20)],
        (10, 19): [(9, 19), (10, 20)],
        (11, 19): [(11, 18), (11, 20)],
        (12, 19): [(13, 19), (12, 18)],
        (13, 19): [(12, 19), (13, 18)],
        (14, 19): [(15, 19), (14, 18), (14, 20)],
        (15, 19): [(14, 19), (16, 19), (15, 18), (15, 20)],
        (16, 19): [(15, 19), (16, 18), (16, 20)],
        (17, 19): [(17, 18), (17, 20)],
        (18, 19): [(19, 19), (18, 18), (18, 20)],
        (19, 19): [(18, 19), (20, 19), (19, 18)],
        (20, 19): [(19, 19), (21, 19), (20, 18)],
        (21, 19): [(20, 19), (22, 19), (21, 18)],
        (22, 19): [(21, 19), (22, 18)],
        (23, 19): [(24, 19)],
        (24, 19): [(23, 19), (25, 19), (24, 18), (24, 20)],
        (25, 19): [(24, 19), (26, 19), (25, 18), (25, 20)],
        (26, 19): [(25, 19), (27, 19), (26, 18)],
        (27, 19): [(26, 19), (27, 18), (27, 20)],
        (28, 19): [(29, 19), (28, 18), (28, 20)],
        (29, 19): [(28, 19), (29, 18), (29, 20)],

        #     UP     D     L      R
        (0, 20): [(1, 20), (0, 19), (0, 21)],  # Column 20
        (1, 20): [(0, 20), (2, 20), (1, 19), (1, 21)],
        (2, 20): [(1, 20), (3, 20), (2, 19), (2, 21)],
        (3, 20): [(2, 20), (3, 19), (3, 21)],
        (4, 20): [(5, 20), (4, 19)],
        (5, 20): [(4, 20), (5, 19)],
        (6, 20): [(7, 20), (6, 19), (6, 21)],
        (7, 20): [(6, 20), (8, 20), (7, 19), (7, 21)],
        (8, 20): [(7, 20), (9, 20), (8, 19)],
        (9, 20): [(8, 20), (10, 20), (9, 19)],
        (10, 20): [(9, 20), (11, 20), (10, 19)],
        (11, 20): [(10, 20), (12, 20), (11, 19), (11, 21)],
        (12, 20): [(11, 20), (13, 20), (12, 21)],
        (13, 20): [(12, 20), (13, 21)],
        (14, 20): [(15, 20), (14, 19), (14, 21)],
        (15, 20): [(14, 20), (16, 20), (15, 19), (15, 21)],
        (16, 20): [(15, 20), (16, 19), (16, 21)],
        (17, 20): [(17, 19), (17, 21)],
        (18, 20): [(19, 20), (18, 19), (18, 21)],
        (19, 20): [(18, 20), (19, 21)],
        (20, 20): [(21, 20), (20, 21)],
        (21, 20): [(20, 20)],
        (22, 20): [(23, 20), (22, 21)],
        (23, 20): [(22, 20), (24, 20), (23, 21)],
        (24, 20): [(23, 20), (25, 20), (24, 19), (24, 21)],
        (25, 20): [(24, 20), (26, 20), (25, 19), (25, 21)],
        (26, 20): [(25, 20), (27, 20)],
        (27, 20): [(26, 20), (28, 20), (27, 19)],
        (28, 20): [(27, 20), (29, 20), (28, 19)],
        (29, 20): [(28, 20), (29, 19)],

        #     UP     D     L      R
        (0, 21): [(1, 21), (0, 20), (0, 22)],  # Column 21
        (1, 21): [(0, 21), (2, 21), (1, 20), (1, 22)],
        (2, 21): [(1, 21), (3, 21), (2, 20), (2, 22)],
        (3, 21): [(2, 21), (3, 20), (3, 22)],
        (4, 21): [(5, 21), (4, 22)],
        (5, 21): [(4, 21), (6, 21), (5, 22)],
        (6, 21): [(5, 21), (7, 21), (6, 20), (6, 22)],
        (7, 21): [(6, 21), (7, 20), (7, 22)],
        (8, 21): [(9, 21), (8, 22)],
        (9, 21): [(8, 21)],
        (10, 21): [(11, 21)],
        (11, 21): [(10, 21), (11, 20), (11, 22)],
        (12, 21): [(13, 21), (12, 20)],
        (13, 21): [(12, 21), (13, 20)],
        (14, 21): [(15, 21), (14, 20), (14, 22)],
        (15, 21): [(14, 21), (16, 21), (15, 20), (15, 22)],
        (16, 21): [(15, 21), (16, 20)],
        (17, 21): [(17, 20), (17, 22)],
        (18, 21): [(19, 21), (18, 20)],
        (19, 21): [(18, 21), (19, 20)],
        (20, 21): [(20, 20), (20, 22)],
        (21, 21): [(21, 22)],
        (22, 21): [(23, 21), (22, 20)],
        (23, 21): [(22, 21), (23, 20)],
        (24, 21): [(25, 21), (24, 20), (24, 22)],
        (25, 21): [(24, 21), (26, 21), (25, 20), (25, 22)],
        (26, 21): [(25, 21)],
        (27, 21): [(28, 21), (27, 22)],
        (28, 21): [(27, 21), (29, 21), (28, 22)],
        (29, 21): [(28, 21), (29, 22)],

        #     UP     D     L      R
        # Column 22
        (0, 22): [(1, 22), (0, 21), (0, 23)],
        (1, 22): [(0, 22), (2, 22), (1, 21), (1, 23)],
        (2, 22): [(1, 22), (3, 22), (2, 21), (2, 23)],
        (3, 22): [(2, 22), (3, 21), (3, 23)],
        (4, 22): [(5, 22), (4, 21), (4, 23)],
        (5, 22): [(4, 22), (5, 21), (5, 23)],
        (6, 22): [(7, 22), (6, 21), (6, 23)],
        (7, 22): [(6, 22), (8, 22), (7, 21), (7, 23)],
        (8, 22): [(7, 22), (9, 22), (8, 21), (8, 23)],
        (9, 22): [(8, 22), (10, 22), (9, 23)],
        (10, 22): [(9, 22), (11, 22), (10, 23)],
        (11, 22): [(10, 22), (12, 22), (11, 21)],
        (12, 22): [(11, 22), (13, 22), (12, 23)],
        (13, 22): [(12, 22), (14, 22)],
        (14, 22): [(13, 22), (15, 22), (14, 21), (14, 23)],
        (15, 22): [(14, 22), (16, 22), (15, 21)],
        (16, 22): [(15, 22), (17, 22)],
        (17, 22): [(16, 22), (18, 22), (17, 21), (17, 23)],
        (18, 22): [(17, 22), (19, 22), (18, 23)],
        (19, 22): [(18, 22), (20, 22), (19, 23)],
        (20, 22): [(19, 22), (21, 22), (20, 21), (20, 23)],
        (21, 22): [(20, 22), (22, 22), (21, 21), (21, 23)],
        (22, 22): [(21, 22), (23, 22)],
        (23, 22): [(22, 22), (24, 22), (23, 23)],
        (24, 22): [(23, 22), (25, 22), (24, 21), (24, 23)],
        (25, 22): [(24, 22), (26, 22), (25, 21), (25, 23)],
        (26, 22): [(25, 22), (27, 22), (26, 23)],
        (27, 22): [(26, 22), (28, 22), (27, 21), (27, 23)],
        (28, 22): [(27, 22), (29, 22), (28, 21), (28, 23)],
        (29, 22): [(28, 22), (29, 21), (29, 23)],

        #   UP     D      L      R
        (0, 23): [(1, 23), (0, 22), (0, 24)],  # Column 23
        (1, 23): [(0, 23), (2, 23), (1, 22), (1, 24)],
        (2, 23): [(1, 23), (3, 23), (2, 22), (2, 24)],
        (3, 23): [(2, 23), (3, 22), (3, 24)],
        (4, 23): [(5, 23), (4, 22), (4, 24)],
        (5, 23): [(4, 23), (5, 22)],
        (6, 23): [(7, 23), (6, 22), (6, 24)],
        (7, 23): [(6, 23), (8, 23), (7, 22), (7, 24)],
        (8, 23): [(7, 23), (9, 23), (8, 22), (8, 24)],
        (9, 23): [(8, 23), (10, 23), (9, 22), (9, 24)],
        (10, 23): [(9, 23), (10, 22), (10, 24)],
        (11, 23): [(12, 23), (11, 24)],
        (12, 23): [(11, 23), (12, 22), (12, 24)],
        (13, 23): [(14, 23), (13, 24)],
        (14, 23): [(13, 23), (14, 22), (14, 24)],
        (15, 23): [(16, 23), (15, 24)],
        (16, 23): [(15, 23), (16, 24)],
        (17, 23): [(17, 22), (17, 24)],
        (18, 23): [(19, 23), (18, 22), (18, 24)],
        (19, 23): [(18, 23), (20, 23), (19, 22)],
        (20, 23): [(19, 23), (21, 23), (20, 22), (20, 24)],
        (21, 23): [(20, 23), (21, 22)],
        (22, 23): [(22, 24)],
        (23, 23): [(24, 23), (23, 22), (23, 24)],
        (24, 23): [(23, 23), (25, 23), (24, 22), (24, 24)],
        (25, 23): [(24, 23), (25, 22), (25, 24)],
        (26, 23): [(27, 23), (26, 22)],
        (27, 23): [(26, 23), (28, 23), (27, 22)],
        (28, 23): [(27, 23), (29, 23), (28, 22)],
        (29, 23): [(28, 23), (29, 22)],

        #   UP     D      L      R
        (0, 24): [(1, 24), (0, 23), (0, 25)],  # Column 24
        (1, 24): [(0, 24), (2, 24), (1, 23), (1, 25)],
        (2, 24): [(1, 24), (3, 24), (2, 23), (2, 25)],
        (3, 24): [(2, 24), (3, 23), (3, 25)],
        (4, 24): [(4, 23)],
        (5, 24): [(6, 24)],
        (6, 24): [(5, 24), (7, 24), (6, 23), (6, 25)],
        (7, 24): [(6, 24), (7, 23), (7, 25)],
        (8, 24): [(9, 24), (8, 23)],
        (9, 24): [(8, 24), (10, 24), (9, 23)],
        (10, 24): [(9, 24), (10, 23)],
        (11, 24): [(12, 24), (11, 23)],
        (12, 24): [(11, 24), (12, 23)],
        (13, 24): [(14, 24), (13, 23)],
        (14, 24): [(13, 24), (14, 23)],
        (15, 24): [(16, 24), (15, 23)],
        (16, 24): [(15, 24), (17, 24), (16, 23)],
        (17, 24): [(16, 24), (17, 23), (17, 25)],
        (18, 24): [(18, 23), (18, 25)],
        (19, 24): [(20, 24), (19, 25)],
        (20, 24): [(19, 24), (21, 24), (20, 23), (20, 25)],
        (21, 24): [(20, 24), (22, 24), (21, 25)],
        (22, 24): [(21, 24), (22, 23), (22, 25)],
        (23, 24): [(23, 23)],
        (24, 24): [(25, 24), (24, 23), (24, 25)],
        (25, 24): [(24, 24), (25, 23), (25, 25)],
        (26, 24): [(27, 24), (26, 25)],
        (27, 24): [(26, 24), (28, 24), (27, 25)],
        (28, 24): [(27, 24), (29, 24), (28, 25)],
        (29, 24): [(28, 24), (29, 25)],

        #     UP      D      L      R
        (0, 25): [(1, 25), (0, 24), (0, 26)],  # Column 25
        (1, 25): [(0, 25), (2, 25), (1, 24), (1, 26)],
        (2, 25): [(1, 25), (3, 25), (2, 24), (2, 26)],
        (3, 25): [(2, 25), (3, 24), (3, 26)],
        (4, 25): [(5, 25), (4, 26)],
        (5, 25): [(4, 25), (6, 25), (5, 26)],
        (6, 25): [(5, 25), (7, 25), (6, 24), (6, 26)],
        (7, 25): [(6, 25), (8, 25), (7, 24), (7, 26)],
        (8, 25): [(7, 25), (9, 25), (8, 26)],
        (9, 25): [(8, 25), (10, 25), (9, 26)],
        (10, 25): [(9, 25), (10, 26)],
        (11, 25): [(12, 25), (11, 26)],
        (12, 25): [(11, 25), (12, 26)],
        (13, 25): [(14, 25)],
        (14, 25): [(13, 25), (15, 25), (14, 26)],
        (15, 25): [(14, 25), (16, 25), (15, 26)],
        (16, 25): [(15, 25), (16, 26)],
        (17, 25): [(16, 25), (18, 25), (17, 24), (17, 26)],
        (18, 25): [(17, 25), (19, 25), (18, 24), (18, 26)],
        (19, 25): [(18, 25), (20, 25), (19, 24), (19, 26)],
        (20, 25): [(19, 25), (21, 25), (20, 24), (20, 26)],
        (21, 25): [(20, 25), (22, 25), (21, 24), (21, 26)],
        (22, 25): [(21, 25), (23, 25), (22, 24)],
        (23, 25): [(22, 25), (24, 25)],
        (24, 25): [(23, 25), (25, 25), (24, 24), (24, 26)],
        (25, 25): [(24, 25), (26, 25), (25, 24), (25, 26)],
        (26, 25): [(25, 25), (27, 25), (26, 24)],
        (27, 25): [(26, 25), (28, 25), (27, 24)],
        (28, 25): [(27, 25), (29, 25), (28, 24)],
        (29, 25): [(28, 25), (29, 24)],

        #     UP      D      L      R
        (0, 26): [(1, 26), (0, 25), (0, 27)],  # Column 26
        (1, 26): [(0, 26), (2, 26), (1, 25), (1, 27)],
        (2, 26): [(1, 26), (3, 26), (2, 25), (2, 27)],
        (3, 26): [(2, 26), (3, 25), (3, 27)],
        (4, 26): [(5, 26), (4, 25), (4, 27)],
        (5, 26): [(4, 26), (5, 25), (5, 27)],
        (6, 26): [(7, 26), (6, 25), (6, 27)],
        (7, 26): [(6, 26), (7, 25), (7, 27)],
        (8, 26): [(9, 26), (8, 25)],
        (9, 26): [(8, 26), (10, 26), (9, 25)],
        (10, 26): [(9, 26), (10, 25)],
        (11, 26): [(12, 26), (11, 25), (11, 27)],
        (12, 26): [(11, 26), (13, 26), (12, 25), (12, 27)],
        (13, 26): [(12, 26), (13, 27)],
        (14, 26): [(15, 26), (14, 25)],
        (15, 26): [(14, 26), (16, 26), (15, 25), (15, 27)],
        (16, 26): [(15, 26), (16, 25)],
        (17, 26): [(17, 25), (17, 27)],
        (18, 26): [(18, 25)],
        (19, 26): [(20, 26), (19, 25)],
        (20, 26): [(19, 26), (21, 26), (20, 25)],
        (21, 26): [(20, 26), (21, 25)],
        (22, 26): [(23, 26)],
        (23, 26): [(22, 26), (24, 26)],
        (24, 26): [(23, 26), (25, 26), (24, 25), (24, 27)],
        (25, 26): [(24, 26), (25, 25), (25, 27)],
        (26, 26): [(27, 26)],
        (27, 26): [(26, 26), (28, 26), (27, 27)],
        (28, 26): [(27, 26), (29, 26), (28, 27)],
        (29, 26): [(28, 26), (29, 27)],

        #     UP      D      L      R
        (0, 27): [(1, 27), (0, 26), (0, 28)],  # Column 27
        (1, 27): [(0, 27), (2, 27), (1, 26), (1, 28)],
        (2, 27): [(1, 27), (3, 27), (2, 26), (2, 28)],
        (3, 27): [(2, 27), (3, 26), (3, 28)],
        (4, 27): [(5, 27), (4, 26)],
        (5, 27): [(4, 27), (5, 26)],
        (6, 27): [(7, 27), (6, 26), (6, 28)],
        (7, 27): [(6, 27), (7, 26)],
        (8, 27): [(9, 27), (8, 28)],
        (9, 27): [(8, 27), (9, 28)],
        (10, 27): [(11, 27), (10, 28)],
        (11, 27): [(10, 27), (12, 27), (11, 26), (11, 28)],
        (12, 27): [(11, 27), (12, 26), (12, 28)],
        (13, 27): [(14, 27), (13, 26), (13, 28)],
        (14, 27): [(13, 27), (14, 28)],
        (15, 27): [(16, 27), (15, 26), (15, 28)],
        (16, 27): [(15, 27), (16, 28)],
        (17, 27): [(17, 26), (17, 28)],
        (18, 27): [(19, 27), (18, 28)],
        (19, 27): [(18, 27), (20, 27), (19, 28)],
        (20, 27): [(19, 27), (20, 28)],
        (21, 27): [(22, 27), (21, 28)],
        (22, 27): [(21, 27), (22, 28)],
        (23, 27): [(23, 28)],
        (24, 27): [(25, 27), (24, 26), (24, 28)],
        (25, 27): [(24, 27), (26, 27), (25, 26), (25, 28)],
        (26, 27): [(25, 27)],
        (27, 27): [(28, 27), (27, 26)],
        (28, 27): [(27, 27), (29, 27), (28, 26)],
        (29, 27): [(28, 27), (29, 26), (29, 28)],

        #     UP      D      L      R
        (0, 28): [(1, 28), (0, 27), (0, 29)],  # Column 28
        (1, 28): [(0, 28), (2, 28), (1, 27), (1, 29)],
        (2, 28): [(1, 28), (3, 28), (2, 27), (2, 29)],
        (3, 28): [(2, 28), (3, 27), (3, 29)],
        (4, 28): [(5, 28), (4, 29)],
        (5, 28): [(4, 28), (6, 28), (5, 29)],
        (6, 28): [(5, 28), (6, 27), (6, 29)],
        (7, 28): [(7, 29)],
        (8, 28): [(9, 28), (8, 27)],
        (9, 28): [(8, 28), (9, 27), (9, 29)],
        (10, 28): [(11, 28), (10, 27)],
        (11, 28): [(10, 28), (12, 28), (11, 27)],
        (12, 28): [(11, 28), (12, 27), (12, 29)],
        (13, 28): [(14, 28), (13, 27)],
        (14, 28): [(13, 28), (14, 27), (14, 29)],
        (15, 28): [(16, 28), (15, 27)],
        (16, 28): [(15, 28), (16, 27)],
        (17, 28): [(17, 27), (17, 29)],
        (18, 28): [(19, 28), (18, 27)],
        (19, 28): [(18, 28), (20, 28), (19, 27)],
        (20, 28): [(19, 28), (20, 27), (20, 29)],
        (21, 28): [(22, 28), (21, 27)],
        (22, 28): [(21, 28), (22, 27), (22, 29)],
        (23, 28): [(23, 27), (23, 29)],
        (24, 28): [(25, 28), (24, 27), (24, 29)],
        (25, 28): [(24, 28), (25, 27), (25, 29)],
        (26, 28): [(26, 29)],
        (27, 28): [(28, 28), (27, 29)],
        (28, 28): [(27, 28), (28, 29)],
        (29, 28): [(29, 27), (29, 29)],

        #     UP      D      L      R
        (0, 29): [(1, 29), (0, 28), (0, 30)],  # Column 29
        (1, 29): [(0, 29), (2, 29), (1, 28), (1, 30)],
        (2, 29): [(1, 29), (3, 29), (2, 28), (2, 30)],
        (3, 29): [(2, 29), (3, 28), (3, 30)],
        (4, 29): [(5, 29), (4, 28)],
        (5, 29): [(4, 29), (6, 29), (5, 28)],
        (6, 29): [(5, 29), (6, 28)],
        (7, 29): [(8, 29), (7, 28), (7, 30)],
        (8, 29): [(7, 29), (9, 29), (8, 30)],
        (9, 29): [(8, 29), (10, 29), (9, 28), (9, 30)],
        (10, 29): [(9, 29), (11, 29), (10, 30)],
        (11, 29): [(10, 29), (12, 29), (11, 30)],
        (12, 29): [(11, 29), (13, 29), (12, 28)],
        (13, 29): [(12, 29), (14, 29)],
        (14, 29): [(13, 29), (15, 29), (14, 28), (14, 30)],
        (15, 29): [(14, 29), (16, 29)],
        (16, 29): [(15, 29), (17, 29)],
        (17, 29): [(16, 29), (18, 29), (17, 28), (17, 30)],
        (18, 29): [(17, 29), (18, 30)],
        (19, 29): [(20, 29)],
        (20, 29): [(19, 29), (21, 29), (20, 28)],
        (21, 29): [(20, 29), (22, 29), (21, 30)],
        (22, 29): [(21, 29), (23, 29), (22, 28), (22, 30)],
        (23, 29): [(22, 29), (23, 28), (23, 30)],
        (24, 29): [(25, 29), (24, 28), (24, 30)],
        (25, 29): [(24, 29), (26, 29), (25, 28), (25, 30)],
        (26, 29): [(25, 29), (27, 29), (26, 28)],
        (27, 29): [(26, 29), (28, 29), (27, 28)],
        (28, 29): [(27, 29), (28, 28)],
        (29, 29): [(29, 28)],

        #     UP      D      L      R
        (0, 30): [(1, 30), (0, 29), (0, 31)],  # Column 30
        (1, 30): [(0, 30), (2, 30), (1, 29), (1, 31)],
        (2, 30): [(1, 30), (3, 30), (2, 29), (2, 31)],
        (3, 30): [(2, 30), (4, 30), (3, 29), (3, 31)],
        (4, 30): [(3, 30), (5, 30), (4, 31)],
        (5, 30): [(4, 30), (5, 31)],
        (6, 30): [(6, 31)],
        (7, 30): [(8, 30), (7, 29), (7, 31)],
        (8, 30): [(7, 30), (8, 29), (8, 31)],
        (9, 30): [(9, 29), (9, 31)],
        (10, 30): [(10, 29), (10, 31)],
        (11, 30): [(12, 30), (11, 29), (11, 31)],
        (12, 30): [(11, 30), (13, 30), (12, 31)],
        (13, 30): [(12, 30), (13, 31)],
        (14, 30): [(15, 30), (14, 29), (14, 31)],
        (15, 30): [(14, 30), (15, 31)],
        (16, 30): [(16, 31)],
        (17, 30): [(18, 30), (17, 29), (17, 31)],
        (18, 30): [(17, 30), (18, 29), (18, 31)],  # Not sure if Wall, currently mapped as wall
        (19, 30): [(18, 30), (20, 30), (19, 31)],
        (20, 30): [(19, 30), (21, 30), (20, 31)],
        (21, 30): [(20, 30), (22, 30), (21, 29), (21, 31)],
        (22, 30): [(21, 30), (23, 30), (22, 29), (22, 31)],
        (23, 30): [(22, 30), (23, 29), (23, 31)],
        (24, 30): [(25, 30), (24, 29), (24, 31)],
        (25, 30): [(24, 30), (26, 30), (25, 29), (25, 31)],
        (26, 30): [(25, 30), (27, 30), (26, 31)],
        (27, 30): [(26, 30), (28, 30), (27, 31)],
        (28, 30): [(27, 30), (29, 30), (28, 31)],
        (29, 30): [(28, 30), (29, 31)],

        #     UP    D      L      R
        (0, 31): [(1, 31), (0, 30), (0, 32)],  # Column 31
        (1, 31): [(0, 31), (2, 31), (1, 30), (1, 32)],
        (2, 31): [(1, 31), (3, 31), (2, 30), (2, 32)],
        (3, 31): [(2, 31), (4, 31), (3, 30), (3, 32)],
        (4, 31): [(3, 31), (5, 31), (4, 30), (4, 32)],
        (5, 31): [(4, 31), (6, 31), (5, 30), (5, 32)],
        (6, 31): [(5, 31), (6, 30)],
        (7, 31): [(8, 31), (7, 30)],
        (8, 31): [(7, 31), (8, 30)],
        (9, 31): [(9, 30)],
        (10, 31): [(10, 30)],
        (11, 31): [(11, 30), (11, 32)],
        (12, 31): [(11, 31), (13, 31), (12, 30)],
        (13, 31): [(12, 31), (14, 31), (13, 30)],
        (14, 31): [(13, 31), (15, 31), (14, 30), (14, 32)],
        (15, 31): [(14, 31), (16, 31), (15, 30), (15, 32)],
        (16, 31): [(15, 31), (16, 30), (16, 32)],
        (17, 31): [(18, 31), (17, 30), (17, 32)],
        (18, 31): [(17, 31), (18, 30), (18, 32)],
        (19, 31): [(20, 31), (19, 30), (19, 32)],
        (20, 31): [(19, 31), (20, 30), (20, 32)],
        (21, 31): [(22, 31), (21, 30), (21, 32)],
        (22, 31): [(21, 31), (23, 31), (22, 30), (22, 32)],
        (23, 31): [(22, 31), (23, 30), (23, 32)],
        (24, 31): [(25, 31), (24, 30), (24, 32)],
        (25, 31): [(24, 31), (26, 31), (25, 30), (25, 32)],
        (26, 31): [(25, 31), (27, 31), (26, 30), (26, 32)],
        (27, 31): [(26, 31), (28, 31), (27, 30), (27, 32)],
        (28, 31): [(27, 31), (29, 31), (28, 30), (28, 32)],
        (29, 31): [(28, 31), (29, 30), (29, 32)],

        #     UP     D      L      R
        (0, 32): [(1, 32), (0, 31), (0, 33)],  # Column 32
        (1, 32): [(0, 32), (2, 32), (1, 31), (1, 33)],
        (2, 32): [(1, 32), (3, 32), (2, 31), (2, 33)],
        (3, 32): [(2, 32), (4, 32), (3, 31), (3, 33)],
        (4, 32): [(3, 32), (5, 32), (4, 31), (4, 33)],
        (5, 32): [(4, 32), (5, 31), (5, 33)],
        (6, 32): [(7, 32), (6, 33)],
        (7, 32): [(6, 32), (8, 32), (7, 33)],
        (8, 32): [(7, 32), (9, 32), (8, 33)],
        (9, 32): [(8, 32), (10, 32), (9, 33)],
        (10, 32): [(9, 32), (11, 32), (10, 33)],
        (11, 32): [(10, 32), (11, 31), (11, 33)],
        (12, 32): [(13, 32), (12, 33)],
        (13, 32): [(12, 32), (13, 33)],
        (14, 32): [(15, 32), (14, 31), (14, 33)],
        (15, 32): [(14, 32), (15, 31), (15, 33)],
        (16, 32): [(16, 31)],
        (17, 32): [(18, 32), (17, 31), (17, 33)],
        (18, 32): [(17, 32), (18, 31), (18, 33)],
        (19, 32): [(20, 32), (19, 31), (19, 33)],
        (20, 32): [(19, 32), (20, 31), (20, 33)],
        (21, 32): [(22, 32), (21, 31), (21, 33)],
        (22, 32): [(21, 32), (23, 32), (22, 31), (22, 33)],
        (23, 32): [(22, 32), (23, 31)],
        (24, 32): [(25, 32), (24, 31), (24, 33)],
        (25, 32): [(24, 32), (25, 31)],
        (26, 32): [(27, 32), (26, 31), (26, 33)],
        (27, 32): [(26, 32), (28, 32), (27, 31), (27, 33)],
        (28, 32): [(27, 32), (29, 32), (28, 31), (28, 33)],
        (29, 32): [(28, 32), (29, 31), (29, 33)],

        #     UP     D      L      R
        (0, 33): [(1, 33), (0, 32), (0, 34)],  # Column 33
        (1, 33): [(0, 33), (2, 33), (1, 32), (1, 34)],
        (2, 33): [(1, 33), (3, 33), (2, 32), (2, 34)],
        (3, 33): [(2, 33), (4, 33), (3, 32), (3, 34)],
        (4, 33): [(3, 33), (5, 33), (4, 32), (4, 34)],
        (5, 33): [(4, 33), (6, 33), (5, 32), (5, 34)],
        (6, 33): [(5, 33), (7, 33), (6, 32), (6, 34)],
        (7, 33): [(6, 33), (8, 33), (7, 32), (7, 34)],
        (8, 33): [(7, 33), (9, 33), (8, 32), (8, 34)],
        (9, 33): [(8, 33), (10, 33), (9, 32), (9, 34)],
        (10, 33): [(9, 33), (11, 33), (10, 32), (10, 34)],
        (11, 33): [(10, 33), (11, 32), (11, 34)],
        (12, 33): [(13, 33), (12, 32)],
        (13, 33): [(12, 33), (13, 32), (13, 34)],
        (14, 33): [(15, 33), (14, 32), (14, 34)],
        (15, 33): [(14, 33), (16, 33), (15, 32), (15, 34)],
        (16, 33): [(15, 33), (17, 33), (16, 34)],
        (17, 33): [(16, 33), (18, 33), (17, 32), (17, 34)],
        (18, 33): [(17, 33), (18, 32), (18, 34)],
        (19, 33): [(20, 33), (19, 32), (19, 34)],
        (20, 33): [(19, 33), (20, 32), (20, 34)],
        (21, 33): [(22, 33), (21, 32), (21, 34)],
        (22, 33): [(21, 33), (23, 33), (22, 32), (22, 34)],
        (23, 33): [(22, 33), (23, 34)],
        (24, 33): [(25, 33), (24, 32), (24, 34)],
        (25, 33): [(24, 33), (26, 33), (25, 34)],
        (26, 33): [(25, 33), (27, 33), (26, 32), (26, 34)],
        (27, 33): [(26, 33), (28, 33), (27, 32), (27, 34)],
        (28, 33): [(27, 33), (29, 33), (28, 32), (28, 34)],
        (29, 33): [(28, 33), (29, 32), (29, 34)],

        #     UP     D      L      R
        (0, 34): [(1, 34), (0, 33), (0, 35)],  # Column 34
        (1, 34): [(0, 34), (2, 34), (1, 33), (1, 35)],
        (2, 34): [(1, 34), (3, 34), (2, 33), (2, 35)],
        (3, 34): [(2, 34), (4, 34), (3, 33), (3, 35)],
        (4, 34): [(3, 34), (5, 34), (4, 33), (4, 35)],
        (5, 34): [(4, 34), (5, 33), (5, 35)],
        (6, 34): [(7, 34), (6, 33)],
        (7, 34): [(6, 34), (8, 34), (7, 33)],
        (8, 34): [(7, 34), (9, 34), (8, 33)],
        (9, 34): [(8, 34), (10, 34), (9, 33)],
        (10, 34): [(9, 34), (11, 34), (10, 33)],
        (11, 34): [(10, 34), (11, 33)],
        (12, 34): [(13, 34), (12, 35)],
        (13, 34): [(12, 34), (13, 33), (13, 35)],
        (14, 34): [(15, 34), (14, 33), (14, 35)],
        (15, 34): [(14, 34), (16, 34), (15, 33), (15, 35)],
        (16, 34): [(15, 34), (16, 33), (16, 35)],
        (17, 34): [(18, 34), (17, 33), (17, 35)],
        (18, 34): [(17, 34), (18, 33), (18, 35)],
        (19, 34): [(20, 34), (19, 33), (19, 35)],
        (20, 34): [(19, 34), (21, 34), (20, 33), (20, 35)],
        (21, 34): [(20, 34), (22, 34), (21, 33), (21, 35)],
        (22, 34): [(21, 34), (22, 33), (22, 35)],
        (23, 34): [(23, 33)],
        (24, 34): [(25, 34), (24, 33), (24, 35)],
        (25, 34): [(24, 34), (25, 33), (25, 35)],
        (26, 34): [(27, 34), (26, 33), (26, 35)],
        (27, 34): [(26, 34), (28, 34), (27, 33), (27, 35)],
        (28, 34): [(27, 34), (29, 34), (28, 33), (28, 35)],
        (29, 34): [(28, 34), (29, 33), (29, 35)],

        #     UP     D      L      R
        (0, 35): [(1, 35), (0, 34), (0, 36)],  # Column 35
        (1, 35): [(0, 35), (2, 35), (1, 34), (1, 36)],
        (2, 35): [(1, 35), (3, 35), (2, 34), (2, 36)],
        (3, 35): [(2, 35), (4, 35), (3, 34), (3, 36)],
        (4, 35): [(3, 35), (5, 35), (4, 34), (4, 36)],
        (5, 35): [(4, 35), (5, 34), (5, 36)],
        (6, 35): [(6, 36)],
        (7, 35): [(8, 35), (7, 36)],
        (8, 35): [(7, 35), (9, 35), (8, 36)],
        (9, 35): [(8, 35), (9, 36)],
        (10, 35): [(11, 35), (10, 36)],
        (11, 35): [(10, 35), (11, 36)],
        (12, 35): [(13, 35), (12, 34), (12, 36)],
        (13, 35): [(12, 35), (13, 34), (13, 36)],
        (14, 35): [(15, 35), (14, 34), (14, 36)],
        (15, 35): [(14, 35), (16, 35), (15, 34), (15, 36)],
        (16, 35): [(15, 35), (16, 34)],
        (17, 35): [(18, 35), (17, 34), (17, 36)],
        (18, 35): [(17, 35), (18, 34), (18, 36)],
        (19, 35): [(20, 35), (19, 34)],
        (20, 35): [(19, 35), (21, 35), (20, 34)],
        (21, 35): [(20, 35), (22, 35), (21, 34)],
        (22, 35): [(21, 35), (23, 35), (22, 34)],
        (23, 35): [(22, 35), ],
        (24, 35): [(25, 35), (24, 34)],
        (25, 35): [(24, 35), (25, 34)],
        (26, 35): [(27, 35), (26, 34)],
        (27, 35): [(26, 35), (28, 35), (27, 34)],
        (28, 35): [(27, 35), (29, 35), (28, 34)],
        (29, 35): [(28, 35), (29, 34)],

        #      UP     D      L      R
        (0, 36): [(1, 36), (0, 35), (0, 37)],  # Column 36
        (1, 36): [(0, 36), (2, 36), (1, 35), (1, 37)],
        (2, 36): [(1, 36), (3, 36), (2, 35), (2, 37)],
        (3, 36): [(2, 36), (4, 36), (3, 35), (3, 37)],
        (4, 36): [(3, 36), (5, 36), (4, 35), (4, 37)],
        (5, 36): [(4, 36), (6, 36), (5, 35), (5, 37)],
        (6, 36): [(5, 36), (7, 36), (6, 35), (6, 37)],
        (7, 36): [(6, 36), (8, 36), (7, 35), (7, 37)],
        (8, 36): [(7, 36), (9, 36), (8, 35), (8, 37)],
        (9, 36): [(8, 36), (10, 36), (9, 35), (9, 37)],
        (10, 36): [(9, 36), (11, 36), (10, 35), (10, 37)],
        (11, 36): [(10, 36), (11, 35), (11, 37)],
        (12, 36): [(13, 36), (12, 35), (12, 37)],
        (13, 36): [(12, 36), (13, 35), (13, 37)],
        (14, 36): [(15, 36), (14, 35), (14, 37)],
        (15, 36): [(14, 36), (15, 35), (15, 37)],
        (16, 36): [(16, 37)],
        (17, 36): [(18, 36), (17, 35), (17, 37)],
        (18, 36): [(17, 36), (18, 35), (18, 37)],
        (19, 36): [(20, 36), (19, 37)],
        (20, 36): [(19, 36), (21, 36), (20, 37)],
        (21, 36): [(20, 36), (22, 36), (21, 37)],
        (22, 36): [(21, 36), (23, 36), (22, 37)],
        (23, 36): [(22, 36), (24, 36), (23, 37)],
        (24, 36): [(23, 36), (25, 36), (24, 37)],
        (25, 36): [(24, 36), (26, 36), (25, 37)],
        (26, 36): [(25, 36), (27, 36), (26, 37)],
        (27, 36): [(26, 36), (28, 36), (27, 37)],
        (28, 36): [(27, 36), (29, 36), (28, 37)],
        (29, 36): [(28, 36), (29, 37)],

        #      UP     D      L      R
        (0, 37): [(1, 37), (0, 36)],  # Column 37
        (1, 37): [(0, 37), (2, 37), (1, 36)],
        (2, 37): [(1, 37), (3, 37), (2, 36)],
        (3, 37): [(2, 37), (4, 37), (3, 36)],
        (4, 37): [(3, 37), (5, 37), (4, 36)],
        (5, 37): [(4, 37), (5, 36)],
        (6, 37): [(6, 36)],
        (7, 37): [(8, 37), (7, 36)],
        (8, 37): [(7, 37), (9, 37), (8, 36)],
        (9, 37): [(8, 37), (9, 36)],
        (10, 37): [(11, 37), (10, 36)],
        (11, 37): [(10, 37), (11, 36)],
        (12, 37): [(13, 37), (12, 36)],
        (13, 37): [(12, 37), (13, 36)],
        (14, 37): [(15, 37), (14, 36)],
        (15, 37): [(14, 37), (16, 37), (15, 36)],
        (16, 37): [(15, 37), (16, 36)],
        (17, 37): [(18, 37), (17, 36)],
        (18, 37): [(17, 37), (18, 36)],
        (19, 37): [(20, 37), (19, 36)],
        (20, 37): [(19, 37), (21, 37), (20, 36)],
        (21, 37): [(20, 37), (22, 37), (21, 36)],
        (22, 37): [(21, 37), (23, 37), (22, 36)],
        (23, 37): [(22, 37), (24, 37), (23, 36)],
        (24, 37): [(23, 37), (25, 37), (24, 36)],
        (25, 37): [(24, 37), (26, 37), (25, 36)],
        (26, 37): [(25, 37), (27, 37), (26, 36)],
        (27, 37): [(26, 37), (28, 37), (27, 36)],
        (28, 37): [(27, 37), (29, 37), (28, 36)],
        (29, 37): [(28, 37), (29, 36)]
}

root = tk.Tk()
root.title("A* Maze")
#root = (0, 0)
game = MazeGame(root, maze)
#root.bind("<KeyPress>", game.move_agent)
root.mainloop()