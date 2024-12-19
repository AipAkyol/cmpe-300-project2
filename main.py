from mpi4py import MPI
from math import sqrt
import time


# Define faction enum
EARTH = "E"
FIRE = "F"
WATER = "W"
AIR = "A"

# DEFINE READFY FLAGS
READY_1 = 11  # Phase 1 is complete and ready for next
READY_1_POST = 22
READY_1_POST_POST = 223
READY_2 = 33
READY_3 = 44
READY_4 = 55
WAVE_READY = 66

# Inter Worker Tags
AIR_LOC_INFO = 432
AIR_NEW_LOC_INFO = 543

# Define master commands
START_PHASE_1 = 1
START_PHASE_1_POST = 2
START_PHASE_1_POST_POST = 3
START_PHASE_2 = 4
START_PHASE_3 = 5
START_PHASE_4 = 6
SUB_GRID = 7

# Define relative positions of two units
# Convention: Directions are the destination relative to source
# For example, TOP_LEFT means destination is at top left of source
TOP = -1
BOTTOM = -2
LEFT = -3
RIGHT = -4
TOP_LEFT = -5
TOP_RIGHT = -6
BOTTOM_LEFT = -7
BOTTOM_RIGHT = -8

# Define receiver enumerations
# For example in ODD_ODD group only the processors with odd x and odd y values will receive data
# this method avoids dedalocks by splitting receivers into 4 groups in checkered pattern
# notice for readability, in the below functions groups are interchangabily used as phase
EVEN_EVEN = 100
ODD_EVEN = 200
EVEN_ODD = 300
ODD_ODD = 400


def print_relative_pos(rel_pos):
    if rel_pos == TOP:
        print("TOP")
    elif rel_pos == BOTTOM:
        print("BOTTOM")
    elif rel_pos == LEFT:
        print("LEFT")
    elif rel_pos == RIGHT:
        print("RIGHT")
    elif rel_pos == TOP_LEFT:
        print("TOP_LEFT")
    elif rel_pos == TOP_RIGHT:
        print("TOP_RIGHT")
    elif rel_pos == BOTTOM_LEFT:
        print("BOTTOM_LEFT")
    elif rel_pos == BOTTOM_RIGHT:
        print("BOTTOM_RIGHT")


# This function returns the processor receive type from its id
# For example the processor 2 is of type EVEN_ODD
# this is used in determining which processor will receive in given group
def get_type_from_id(id, no_workers):
    cur_x = (id - 1) // int(sqrt(no_workers))
    cur_y = (id - 1) % int(sqrt(no_workers))
    if cur_x % 2 == 0:
        if cur_y % 2 == 0:
            cur_type = EVEN_EVEN
        else:
            cur_type = EVEN_ODD
    else:
        if cur_y % 2 == 0:
            cur_type = ODD_EVEN
        else:
            cur_type = ODD_ODD

    return cur_type


# This function returns the list of destinations current sender should send data
def get_sender_destination_list(cur_id, no_workers, cur_group):
    cur_x = (cur_id - 1) // int(sqrt(no_workers))
    cur_y = (cur_id - 1) % int(sqrt(no_workers))

    cur_type = get_type_from_id(cur_id, no_workers)

    destinations = []

    if cur_group == EVEN_EVEN:
        if cur_type == EVEN_EVEN:
            print("Error in deadlock handling")
        elif cur_type == EVEN_ODD:
            # Put the right and left processors with boundary check
            if cur_y - 1 >= 0:
                destinations.append((cur_x, cur_y - 1))
            if cur_y + 1 < sqrt(no_workers):
                destinations.append((cur_x, cur_y + 1))
        elif cur_type == ODD_EVEN:
            # Put the top and bottom processors with boundary check
            if cur_x - 1 >= 0:
                destinations.append((cur_x - 1, cur_y))
            if cur_x + 1 < sqrt(no_workers):
                destinations.append((cur_x + 1, cur_y))
        elif cur_type == ODD_ODD:
            # Put the top right, top left, bottom right, bottom left processors with boundary check
            if cur_x - 1 >= 0:
                if cur_y - 1 >= 0:
                    destinations.append((cur_x - 1, cur_y - 1))
                if cur_y + 1 < sqrt(no_workers):
                    destinations.append((cur_x - 1, cur_y + 1))
            if cur_x + 1 < sqrt(no_workers):
                if cur_y - 1 >= 0:
                    destinations.append((cur_x + 1, cur_y - 1))
                if cur_y + 1 < sqrt(no_workers):
                    destinations.append((cur_x + 1, cur_y + 1))

    elif cur_group == ODD_ODD:
        if cur_type == ODD_ODD:
            print("Deadlock error")
        elif cur_type == EVEN_ODD:
            # Put the top and bottom processors with boundary check
            if cur_x - 1 >= 0:
                destinations.append((cur_x - 1, cur_y))
            if cur_x + 1 < sqrt(no_workers):
                destinations.append((cur_x + 1, cur_y))
        elif cur_type == ODD_EVEN:
            # Put the right and left processors with boundary check
            if cur_y - 1 >= 0:
                destinations.append((cur_x, cur_y - 1))
            if cur_y + 1 < sqrt(no_workers):
                destinations.append((cur_x, cur_y + 1))
        elif cur_type == EVEN_EVEN:
            # Put the top right, top left, bottom right, bottom left processors with boundary check
            if cur_x - 1 >= 0:
                if cur_y - 1 >= 0:
                    destinations.append((cur_x - 1, cur_y - 1))
                if cur_y + 1 < sqrt(no_workers):
                    destinations.append((cur_x - 1, cur_y + 1))
            if cur_x + 1 < sqrt(no_workers):
                if cur_y - 1 >= 0:
                    destinations.append((cur_x + 1, cur_y - 1))
                if cur_y + 1 < sqrt(no_workers):
                    destinations.append((cur_x + 1, cur_y + 1))

    elif cur_group == ODD_EVEN:
        if cur_type == ODD_EVEN:
            print("Deadlock error")
        elif cur_type == EVEN_EVEN:
            # Put the top and bottom processors with boundary check
            if cur_x - 1 >= 0:
                destinations.append((cur_x - 1, cur_y))
            if cur_x + 1 < sqrt(no_workers):
                destinations.append((cur_x + 1, cur_y))
        elif cur_type == ODD_ODD:
            # Put the right and left processors with boundary check
            if cur_y - 1 >= 0:
                destinations.append((cur_x, cur_y - 1))
            if cur_y + 1 < sqrt(no_workers):
                destinations.append((cur_x, cur_y + 1))
        elif cur_type == EVEN_ODD:
            # Put the top right, top left, bottom right, bottom left processors with boundary check
            if cur_x - 1 >= 0:
                if cur_y - 1 >= 0:
                    destinations.append((cur_x - 1, cur_y - 1))
                if cur_y + 1 < sqrt(no_workers):
                    destinations.append((cur_x - 1, cur_y + 1))
            if cur_x + 1 < sqrt(no_workers):
                if cur_y - 1 >= 0:
                    destinations.append((cur_x + 1, cur_y - 1))
                if cur_y + 1 < sqrt(no_workers):
                    destinations.append((cur_x + 1, cur_y + 1))

    elif cur_group == EVEN_ODD:
        if cur_type == EVEN_ODD:
            print("Deadlock error")
        elif cur_type == ODD_ODD:
            # Put the top and bottom processors with boundary check
            if cur_x - 1 >= 0:
                destinations.append((cur_x - 1, cur_y))
            if cur_x + 1 < sqrt(no_workers):
                destinations.append((cur_x + 1, cur_y))
        elif cur_type == EVEN_EVEN:
            # Put the right and left processors with boundary check
            if cur_y - 1 >= 0:
                destinations.append((cur_x, cur_y - 1))
            if cur_y + 1 < sqrt(no_workers):
                destinations.append((cur_x, cur_y + 1))
        elif cur_type == ODD_EVEN:
            # Put the top right, top left, bottom right, bottom left processors with boundary check
            if cur_x - 1 >= 0:
                if cur_y - 1 >= 0:
                    destinations.append((cur_x - 1, cur_y - 1))
                if cur_y + 1 < sqrt(no_workers):
                    destinations.append((cur_x - 1, cur_y + 1))
            if cur_x + 1 < sqrt(no_workers):
                if cur_y - 1 >= 0:
                    destinations.append((cur_x + 1, cur_y - 1))
                if cur_y + 1 < sqrt(no_workers):
                    destinations.append((cur_x + 1, cur_y + 1))

    # Convert coordinates to processors id
    for i in range(len(destinations)):
        x, y = destinations[i]
        destinations[i] = x * int(sqrt(no_workers)) + y + 1

    return destinations


# This function returns the list of sources current receiver expecting data
def get_receiver_source_list(cur_id, no_workers):
    # Normally all 8 directions are expected sources of data, but boundary checks should be made
    cur_x = (cur_id - 1) // int(sqrt(no_workers))
    cur_y = (cur_id - 1) % int(sqrt(no_workers))
    sources = []
    if cur_x - 1 >= 0:
        sources.append((cur_x - 1, cur_y))
        if cur_y - 1 >= 0:
            sources.append((cur_x - 1, cur_y - 1))
        if cur_y + 1 < sqrt(no_workers):
            sources.append((cur_x - 1, cur_y + 1))
    if cur_x + 1 < sqrt(no_workers):
        sources.append((cur_x + 1, cur_y))
        if cur_y - 1 >= 0:
            sources.append((cur_x + 1, cur_y - 1))
        if cur_y + 1 < sqrt(no_workers):
            sources.append((cur_x + 1, cur_y + 1))
    if cur_y - 1 >= 0:
        sources.append((cur_x, cur_y - 1))
    if cur_y + 1 < sqrt(no_workers):
        sources.append((cur_x, cur_y + 1))

    # Convert sources to processor ids
    for i in range(len(sources)):
        x, y = sources[i]
        sources[i] = x * int(sqrt(no_workers)) + y + 1

    return sources


# This function calculates the number of attackable units given by the air unit
# takes a subgrid (5x5) at whose center lies the air unit we are interested at
def calc_air_attackables(attack_grid):
    cur_x = 2
    cur_y = 2
    attackables = 0

    # Chek bottom location
    if attack_grid[cur_x + 1][cur_y] == ".":
        if attack_grid[cur_x + 2][cur_y] != ".":
            attackables += 1
    else:
        attackables += 1

    # Check top location
    if attack_grid[cur_x - 1][cur_y] == ".":
        if attack_grid[cur_x - 2][cur_y] != ".":
            attackables += 1
    else:
        attackables += 1

    # Check left location
    if attack_grid[cur_x][cur_y - 1] == ".":
        if attack_grid[cur_x][cur_y - 2] != ".":
            attackables += 1
    else:
        attackables += 1

    # Check right location
    if attack_grid[cur_x][cur_y + 1] == ".":
        if attack_grid[cur_x][cur_y + 2] != ".":
            attackables += 1
    else:
        attackables += 1

    # Check top left
    if attack_grid[cur_x - 1][cur_y - 1] == ".":
        if attack_grid[cur_x - 2][cur_y - 2] != ".":
            attackables += 1
    else:
        attackables += 1

    # Check top right
    if attack_grid[cur_x - 1][cur_y + 1] == ".":
        if attack_grid[cur_x - 2][cur_y + 2] != ".":
            attackables += 1
    else:
        attackables += 1

    # Check bottom left
    if attack_grid[cur_x + 1][cur_y - 1] == ".":
        if attack_grid[cur_x + 2][cur_y - 2] != ".":
            attackables += 1
    else:
        attackables += 1

    # Check bottom right
    if attack_grid[cur_x + 1][cur_y + 1] == ".":
        if attack_grid[cur_x + 2][cur_y + 2] != ".":
            attackables += 1
    else:
        attackables += 1


# Calculate the new location of the given air unit in the subgrid
# takes a subgrid (7x7) at whose center lies the air unit we are interested at
def optimum_air_location(location_grid):
    cur_x = 3
    cur_y = 3
    checked_xs = [cur_x - 1, cur_x, cur_x + 1]
    checked_ys = [cur_y - 1, cur_y, cur_y + 1]

    opt_x, opt_y = -1, -1
    attackables = -1

    for new_x in checked_xs:
        for new_y in checked_ys:
            # Calculate the 5x5 subgrid at whose center lies the new_x and new_y
            attack_grid = []
            for i in range(new_x - 2, new_x + 3):
                row = []
                for j in range(new_y - 2, new_y + 3):
                    row.append(location_grid[i][j])
                attack_grid.append(row)

            new_attackables = calc_air_attackables(
                attack_grid
            )  # TODO check tie condition from forum
            should_change = False
            if new_attackables >= attackables:
                if new_attackables == attackables:
                    if new_x < opt_x:
                        should_change = True
                    elif new_x == opt_x:
                        if new_y < opt_y:
                            should_change = True
                else:
                    should_change = True

            if should_change:
                attackables = new_attackables
                opt_x = new_x
                opt_y = new_y

    return (opt_x, opt_y)


# This function calculates the relative position of the destination id against source id
def calc_relative_pos(cur_id, dest_id, no_workers):
    cur_x = (cur_id - 1) // int(sqrt(no_workers))
    cur_y = (cur_id - 1) % int(sqrt(no_workers))

    dest_x = (dest_id - 1) // int(sqrt(no_workers))
    dest_y = (dest_id - 1) % int(sqrt(no_workers))

    if dest_x == cur_x:
        if dest_y == cur_y:
            print("Logic error in relative pos")
            return 0
        elif dest_y > cur_y:
            return RIGHT
        else:
            return LEFT
    elif dest_y == cur_y:
        if dest_x > cur_x:
            return BOTTOM
        else:
            return TOP
    elif dest_x > cur_x:
        if dest_y > cur_y:
            return BOTTOM_RIGHT
        else:
            return BOTTOM_LEFT
    else:
        if dest_y > cur_y:
            return TOP_RIGHT
        else:
            return TOP_LEFT


# This function returns the required portion of subgrid to share to destination id
# to be used in calculation of air units' special ability
def get_subgrid_to_share_air(sub_grid, cur_id, dest_id, no_workers):
    relative_pos = calc_relative_pos(cur_id, dest_id, no_workers)
    if relative_pos == TOP:
        return sub_grid[0:3][:]
    elif relative_pos == BOTTOM:
        # Return last 3 row
        return sub_grid[-3:][:]
    elif relative_pos == LEFT:
        # Return first 3 column
        return [row[0:3] for row in sub_grid]
    elif relative_pos == RIGHT:
        # Return last 3 column
        return [row[-3:] for row in sub_grid]
    elif relative_pos == TOP_LEFT:
        return [sub_grid[0][0:3], sub_grid[1][0:3], sub_grid[2][0:3]]
    elif relative_pos == TOP_RIGHT:
        return [sub_grid[0][-3:], sub_grid[1][-3:], sub_grid[2][-3:]]
    elif relative_pos == BOTTOM_LEFT:
        return [sub_grid[-3][0:3], sub_grid[-2][0:3], sub_grid[-1][0:3]]
    elif relative_pos == BOTTOM_RIGHT:
        return [sub_grid[-3][-3:], sub_grid[-2][-3:], sub_grid[-1][-3:]]


class Unit:
    def set_props(self, faction):
        self.will_heal = False
        self.damage_queue = []
        if faction == EARTH:
            self.hp = 18
            self.max_hp = 18
            self.attack = 2
            self.heal_rate = 3
        elif faction == FIRE:
            self.hp = 12
            self.max_hp = 12
            self.attack = 4
            self.heal_rate = 1
        elif faction == WATER:
            self.hp = 14
            self.max_hp = 14
            self.attack = 3
            self.heal_rate = 2
        elif faction == AIR:
            self.hp = 10
            self.max_hp = 10
            self.attack = 2
            self.heal_rate = 2

    def __init__(self, x, y, faction):
        self.x = x
        self.y = y
        self.faction = faction
        self.set_props(faction)

    def attack_or_heal(self):
        # Decite to heal
        if self.hp < self.max_hp / 2:
            self.will_heal = True
        else:  # Attack
            pass

    def heal(self):
        self.hp += self.heal_rate
        self.will_heal = False

    def apply_damage(self):
        pass


def read_input(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()

    # Read the grid parameters
    N, W, T, R = map(int, lines[0].split())
    waves = []

    # Parse each wave
    line_idx = 2
    for wave in range(W):
        units = {"E": [], "F": [], "W": [], "A": []}
        while line_idx < len(lines):
            line = lines[line_idx].strip()
            if line.startswith("Wave"):
                line_idx += 1
                break
            if not line or ":" not in line:
                break

            faction, positions = line.split(":")
            for pos in positions.strip().split(","):
                x, y = map(int, pos.strip().split())
                units[faction.strip()].append((x, y))
            line_idx += 1
        waves.append(units)
    return N, W, T, R, waves


def print_grid(grid, N):
    for row in grid:
        idx = 0
        for cell in row:
            idx += 1
            visual = cell
            if visual != ".":
                visual = cell.faction
            print(visual, end="")
            if idx != N:
                print(" ", end="")
        print()


def debug_print_grid(grid):
    for row in grid:
        idx = 0
        for cell in row:
            idx += 1
            visual = cell
            if visual != ".":
                visual = cell.faction
            print(visual, end="")
            if idx != len(grid[0]):
                print(" ", end="")
        print()


def generate_grid_from_wave(grid, wave, is_first=False):
    if is_first:
        grid = [["." for _ in range(N)] for _ in range(N)]
    for faction in wave:
        for unit in wave[faction]:
            x, y = unit
            # If overlaps, ignore new unit
            if grid[x][y] != ".":
                continue
            unit = Unit(x, y, faction)
            grid[x][y] = unit
    return grid


# This function appends the source subgrid to the extended subgrid depending on its relative path
def append_source_to_extended(extended_sub_grid, source, relative_pos):
    x = int(len(extended_sub_grid)) - 6
    if relative_pos == TOP:
        for i in range(3):
            for j in range(x):
                extended_sub_grid[i][j + 3] = source[i][j]
    elif relative_pos == BOTTOM:
        for i in range(3):
            for j in range(x):
                extended_sub_grid[i + x + 3][j + 3] = source[i][j]
    elif relative_pos == LEFT:
        for i in range(x):
            for j in range(3):
                extended_sub_grid[i + 3][j] = source[i][j]
    elif relative_pos == RIGHT:
        for i in range(x):
            for j in range(3):
                extended_sub_grid[i + 3][j + x + 3] = source[i][j]
    elif relative_pos == TOP_LEFT:
        for i in range(3):
            for j in range(3):
                extended_sub_grid[i][j] = source[i][j]
    elif relative_pos == TOP_RIGHT:
        for i in range(3):
            for j in range(3):
                extended_sub_grid[i][j + x + 3] = source[i][j]
    elif relative_pos == BOTTOM_LEFT:
        for i in range(3):
            for j in range(3):
                extended_sub_grid[i + x + 3][j] = source[i][j]
    elif relative_pos == BOTTOM_RIGHT:
        for i in range(3):
            for j in range(3):
                extended_sub_grid[i + x + 3][j + x + 3] = source[i][j]


# Function that returns the processor id which the air unit will belong to in its new location
def get_processor_id_air(new_x, new_y, sub_grid_length, cur_id, no_workers):
    k = int(sqrt(no_workers))
    if new_x < 3:
        if new_y < 3:
            return cur_id - k - 1
        elif new_y > sub_grid_length - 4:
            return cur_id - k + 1
        elif new_y >= 3 and new_y <= sub_grid_length - 4:
            return cur_id - k
        else:
            print("Error in get_processor_id_air")
    elif new_x > sub_grid_length - 4:
        if new_y < 3:
            return cur_id + k - 1
        elif new_y > sub_grid_length - 4:
            return cur_id + k + 1
        elif new_y >= 3 and new_y <= sub_grid_length - 4:
            return cur_id + k
        else:
            print("Error in get_processor_id_air")
    elif new_x >= 3 and new_x <= sub_grid_length - 4:
        if new_y < 3:
            return cur_id - 1
        elif new_y > sub_grid_length - 4:
            return cur_id + 1
        elif new_y >= 3 and new_y <= sub_grid_length - 4:
            return cur_id
        else:
            print("Error in get_processor_id_air")


# Initialize the MPI communicator
comm = MPI.COMM_WORLD

# Get the rank (unique ID) of the current process
rank = comm.Get_rank()

# Get the total number of processes in the communicator
world_size = comm.Get_size()

no_processors = world_size
no_workers = no_processors - 1

# Master process
if rank == 0:

    input_file = "./cases/input1.txt"  # TODO chnage
    current_wave = 0
    # grid size, number of waves, unit per faction, rounds per wave
    N, W, T, R, waves = read_input(input_file)
    data = (N, W, T, R, waves)
    sub_grid_length = int(N // int(sqrt(no_workers)))
    grid = []
    init_wave = True
    for i in range(W):
        print("Starting wave", i + 1)
        grid = generate_grid_from_wave(grid, waves[i], init_wave)
        print("Grid after wave ", i + 1)
        print_grid(grid, N)
        # Send each part of the grid to a processor
        # processor no increases to right and down
        for k in range(1, no_workers + 1):
            x_value = (k - 1) // int(sqrt(no_workers))
            y_value = (k - 1) % int(sqrt(no_workers))
            # Send processor k the subgrid which has
            # x = x_value and y = y_value
            sub_grid = []
            for m in range(sub_grid_length):
                sub_row = []
                for n in range(sub_grid_length):
                    sub_row.append(
                        grid[x_value * sub_grid_length + m][
                            y_value * sub_grid_length + n
                        ]
                    )
                sub_grid.append(sub_row)
            comm.send(sub_grid, dest=k, tag=SUB_GRID)

        # Wait for all workers to init new wave
        for j in range(no_workers):
            res = comm.recv(source=MPI.ANY_SOURCE, tag=WAVE_READY)
            if not res:
                print("Error occured after wave init")

        for j in range(R):
            print("Starting round", j + 1)

            # To avoid deadlock seperate phase 1, phase 1 post  to 4 groups
            # First group: x and y are even
            # Second group: x odd y even
            # Third group: x even y odd
            # Fourth group: x and y are even

            groups = [EVEN_EVEN, ODD_EVEN, EVEN_ODD, ODD_ODD]

            for cur_group in groups:
                # Send start phase 1 signals to workers
                print(f"Running group {cur_group} of phase 1")
                for k in range(1, no_workers + 1):
                    cur_type = get_type_from_id(k, no_workers)
                    receive = cur_type == cur_group
                    worker_data = {}
                    worker_data["success"] = True
                    worker_data["receive"] = receive
                    worker_data["cur_group"] = cur_group
                    comm.send(worker_data, dest=k, tag=START_PHASE_1)

                # Wait for all workers to finish phase 1
                for k in range(no_workers):
                    res = comm.recv(source=MPI.ANY_SOURCE, tag=READY_1)
                    if not res:
                        print("Error occured after phase 1")

            exit(12)

            for cur_group in groups:
                # send start post phase 1signals to workers
                for k in range(1, no_workers + 1):
                    cur_type = get_type_from_id(k, no_workers)
                    receive = cur_type == cur_group
                    worker_data = {}
                    worker_data["success"] = True
                    worker_data["receive"] = receive
                    worker_data["cur_group"] = cur_group
                    comm.send(worker_data, dest=k, tag=START_PHASE_1_POST)

                # Wait for all workers to finish post phase 1
                for k in range(no_workers):
                    res = comm.recv(source=MPI.ANY_SOURCE, tag=READY_1_POST)
                    if not res:
                        print("Error occured after post phase 1")

            # Send start post post phase 1 signals to workers
            for k in range(1, no_workers + 1):
                comm.send(True, dest=k, tag=START_PHASE_1_POST_POST)

            # Wait for all workers to finish post post phase 1
            for k in range(no_workers):
                res = comm.recv(source=MPI.ANY_SOURCE, tag=READY_1_POST_POST)
                if not res:
                    print("Error occured after post post phase 1")

            for cur_group in groups:
                # Send start phase 2 signals to workers
                for k in range(1, no_workers + 1):
                    cur_type = get_type_from_id(k, no_workers)
                    receive = cur_type == cur_group
                    worker_data = {}
                    worker_data["success"] = True
                    worker_data["receive"] = receive
                    worker_data["cur_group"] = cur_group
                    comm.send(worker_data, dest=k, tag=START_PHASE_2)

                # Wait for all workers to finish phase 2
                for k in range(no_workers):
                    res = comm.recv(source=MPI.ANY_SOURCE, tag=READY_2)
                    if not res:
                        print("Error occured after phase 2")

            # Send start phase 3 signals to workers
            for k in range(1, no_workers + 1):
                comm.send(True, dest=k, tag=START_PHASE_3)

            # Wait for all workers to finish phase 3
            for k in range(no_workers):
                res = comm.recv(source=MPI.ANY_SOURCE, tag=READY_3)
                if not res:
                    print("Error occured after phase 3")

            # Send start phase 4 signals to workers
            for k in range(1, no_workers + 1):
                worker_data = {}
                worker_data["success"] = True
                worker_data["send_back_subgrid"] = False
                if j == R - 1:
                    worker_data["send_back_subgrid"] = True
                comm.send(worker_data, dest=k, tag=START_PHASE_4)

            # Wait for all workers to finish phase 4
            for k in range(no_workers):
                res = comm.recv(source=MPI.ANY_SOURCE, tag=READY_4)
                if not res:
                    print("Error occured after phase 4")

            print("Round", j + 1, "completed")
        init_wave = False


# Workers
else:
    # processor id of master
    MASTER = 0

    sub_grid = []
    # this list holds the future positions of air units in post post phase 1
    # The format will be as follows:
    # (processor_id, rel_x, rel_y, unit)
    # where processor_id holds where the unit will belong in the future
    # rel_x and rel_y holds the relative position of the unit in the subgrid
    # unit holds the unit itself which will be from air faction
    airs_to_place = []

    # Phase functions
    # Notice receive flag determines if processors wait for data
    # at each time, one out of four group of processors will be waiting for data
    # this approach avoids deadlocks in checkered pattern
    def phase1(rank, cur_group, receive):
        if not receive:  # Share data
            destinations = get_sender_destination_list(rank, no_workers, cur_group)
            for dest in destinations:
                shared_sub_grid_part = get_subgrid_to_share_air(
                    sub_grid, rank, dest, no_workers
                )
                comm.send(shared_sub_grid_part, dest=dest, tag=AIR_LOC_INFO)
        elif receive:  # Collect data, and find optimal positions for air units
            sources = get_receiver_source_list(rank, no_workers)
            x = len(sub_grid)  # x represents border length of subgrid
            extended_sub_grid = [["." for _ in range(x + 6)] for _ in range(x + 6)]
            # Place sub grid in the middle of the extended sub grid
            for i in range(x):
                for j in range(x):
                    extended_sub_grid[i + 3][j + 3] = sub_grid[i][j]
            print("Initial subgrid of processor", rank, "is")
            print_grid(sub_grid, x)
            print(f"Processor {rank} is receiving the followings: ")
            for source in sources:
                sub_grid_part = comm.recv(source=source, tag=AIR_LOC_INFO)
                debug_print_grid(sub_grid_part)
                relative_pos = calc_relative_pos(rank, source, no_workers)
                print(f"From source: {source} with relative pos: ")
                print_relative_pos(relative_pos)
                append_source_to_extended(
                    extended_sub_grid, sub_grid_part, relative_pos
                )

            print("Extended subgrid of processor", rank, "is")
            print_grid(extended_sub_grid, x + 6)

            # Find the optimal location of air units
            for row in sub_grid:
                for unit in row:
                    if unit == ".":
                        continue
                    if unit.faction == AIR:
                        air_x = unit.x
                        air_y = unit.y
                        search_grid = extended_sub_grid[air_x - 3 : air_x + 4][
                            air_y - 3 : air_y + 4
                        ]
                        new_x, new_y = optimum_air_location(search_grid)
                        dest_id = get_processor_id_air(new_x, new_y, x, rank, no_workers)
                        

    # places air units in a given grid, and merges if necessary
    def post_phase1(rank, cur_group, receive):
        pass

    def post_post_phase1():
        pass

    def phase2(rank, cur_group, receive):
        pass

    def phase3():
        pass

    def phase4(send_back):
        pass

    while True:
        # Wait for subgrid at the start of wave
        status = MPI.Status()
        incoming_data = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
        source = status.Get_source()

        tag = status.Get_tag()
        if source == MASTER:
            if tag == SUB_GRID:
                print("Sub grid of processor", rank, "is")
                print_grid(incoming_data, len(incoming_data))
                sub_grid = incoming_data
                # Send master ready after wave flag
                time.sleep(1)
                comm.send(True, dest=MASTER, tag=WAVE_READY)
            elif tag == START_PHASE_1:
                print("Processor", rank, "starting phase 1")
                success = incoming_data["success"]
                if not success:
                    print("Erron in phase1")
                receive = incoming_data["receive"]
                cur_group = incoming_data["cur_group"]
                phase1(rank, cur_group, receive)
                # sleep thread for one second
                time.sleep(1)
                comm.send(True, dest=MASTER, tag=READY_1)
            elif tag == START_PHASE_1_POST:
                print("Processor", rank, "starting post phase 1")
                success = incoming_data["success"]
                if not success:
                    print("Erron in post phase1")
                receive = incoming_data["receive"]
                cur_group = incoming_data["cur_group"]
                post_phase1(rank, cur_group, receive)
                time.sleep(1)
                comm.send(True, dest=MASTER, tag=READY_1_POST)
            elif tag == START_PHASE_1_POST_POST:
                print("Processor", rank, "starting post post phase 1")
                post_post_phase1()
                time.sleep(1)
                comm.send(True, dest=MASTER, tag=READY_1_POST_POST)
            elif tag == START_PHASE_2:
                print("Processor", rank, "starting phase 2")
                success = incoming_data["success"]
                if not success:
                    print("Erron in post phase1")
                receive = incoming_data["receive"]
                cur_group = incoming_data["cur_group"]
                phase2(rank, cur_group, receive)
                time.sleep(1)
                comm.send(True, dest=MASTER, tag=READY_2)
            elif tag == START_PHASE_3:
                print("Processor", rank, "starting phase 3")
                phase3()
                time.sleep(1)
                comm.send(True, dest=MASTER, tag=READY_3)
            elif tag == START_PHASE_4:
                print("Processor", rank, "starting phase 4")
                send_back = incoming_data["send_back_subgrid"]
                phase4(send_back)
                time.sleep(1)
                comm.send(True, dest=MASTER, tag=READY_4)

        else:
            pass
