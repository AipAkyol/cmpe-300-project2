from mpi4py import MPI


# Define faction enum
EARTH = "E"
FIRE = "F"
WATER = "W"
AIR = "A"


class Unit:
    def set_props(self, faction):
        if faction == EARTH:
            self.hp = 18
            self.attack = 2
            self.heal_rate = 3
        elif faction == FIRE:
            self.hp = 12
            self.attack = 4
            self.heal_rate = 1
        elif faction == WATER:
            self.hp = 14
            self.attack = 3
            self.heal_rate = 2
        elif faction == AIR:
            self.hp = 10
            self.attack = 2
            self.heal_rate = 2

    def __init__(self, x, y, faction):
        self.x = x
        self.y = y
        self.faction = faction
        self.set_props(faction)


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


def update_grid(wave, N):
    # TODO check if same cell is occupied by multiple units
    for faction in wave:
        for unit in wave[faction]:
            x, y = unit
            grid[x][y] = faction


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
    comm.send(data, dest=1, tag=22)
# Workers
else:
    data = comm.recv(source=0, tag=22)
    N, W, T, R, waves = data
    pass
