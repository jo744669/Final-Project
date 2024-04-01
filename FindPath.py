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
        x = 26; y = 24
        while x < 30:
            while y < 36:
                self.cells[x][y].ward = "Surgical"
                if y == 25:
                    y = 30
                else:
                    y += 1
            x += 1
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
        self.cells[27][3].ward = "Hallway"
        self.cells[27][4].ward = "Oncology"
        self.cells[27][5].ward = "Oncology"
        self.cells[28][3].ward = "Hallway"
        self.cells[28][4].ward = "Hallway"
        self.cells[28][5].ward = "Hallway"
        self.cells[29][3].ward = "Isolation"
        self.cells[29][4].ward = "Isolation"
        self.cells[29][5].ward = "Isolation"


    def __init__(self, root, maze):
        self.root = root
        self.maze = maze

        self.rows = 38
        self.cols = 30

        self.locations = set()
        delivery_locations = PriorityQueue()

        #### READ FROM INPUT FILE HERE
        # add all locations to self.locations
        # update self.algorithm based on if using A* or Dijkstra

        #### General list to hold delivery locations - to be able to look at all locations
        #### Fill this list from input file - fill priority queue from this list
        for x in self.locations:
            delivery_locations.put(x)

        #### Start state: (0,0) or top left to start -> should always be updated as current location
        self.agent_pos = (0, 0)

        #### Goal state: start with first location from the priority queue
        self.goal_pos = (0,0)
        self.goals_completed = set()

        ### Creates cell object for every cell and assigns the wards and priorities to each cell
        self.cells = [[Cell(x, y) for y in range(self.cols)] for x in range(self.rows)]
        self.assign_wards()
        self.assign_priorities()

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
        while delivery_locations:
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

            #### Agent looks at every child of the current cell
            for neighbor in self.maze[current_cell]:
                new_pos = neighbor

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