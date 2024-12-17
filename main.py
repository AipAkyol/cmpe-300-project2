from mpi4py import MPI


# Define faction enum
EARTH = "E"
FIRE = "F"
WATER = "W"
AIR = "A"

# DEFINE READFY FLAGS
READY_1 = 1
READY_1_POST = 2
READY_2 = 3
READY_3 = 4
READY_4 = 5


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
            print(cell, end="")
            if idx != N:
                print(" ", end="")
        print()


def generate_grid_from_wave(grid, wave, is_first=False):
    if is_first:
        grid = [["." for _ in range(N)] for _ in range(N)]
    for faction in wave:
        for unit in wave[faction]:
            x, y = unit
            # If overlaps, ignore new unit
            if grid[x][y] == ".":
                continue
            unit = Unit(x, y, faction)
            grid[x][y] = unit
    return grid


## Communication
# Workers send flags after each step of the simulation stating they are ready
# Flags:
# -1: Error occured
# 1: Ready after initialization

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
    print(waves)
    grid = [["." for _ in range(N)] for _ in range(N)]
    update_grid(waves[current_wave], N)
    print_grid(grid, N)
    data = (N, W, T, R, waves)

    init_wave = True
    for i in range(W):
        print("Starting wave", i + 1)
        grid = generate_grid_from_wave(grid, waves[i], init_wave)
        for j in range(R):
            print("Starting round", j + 1)
            print("Round", j + 1, "completed")
        init_wave = False


# Workers
else:

    # Phase functions
    # Notice receive flag determines if processors wait for data
    # at each time, one out of four group of processors will be waiting for data
    # this approach avoids deadlocks in checkered pattern
    def phase1(receive=False):
        pass

    # Function to run in phase 2 which is the post processing of phase 1
    # places air units in a given grid, and merges if necessary
    def post_phase1():
        pass

    def phase2(receive=False):
        pass

    def phase3():
        pass

    def phase4():
        pass

    data = comm.recv(source=0, tag=22)
    N, W, T, R, waves = data
    pass
