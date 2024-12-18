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
READY_2 = 33
READY_3 = 44
READY_4 = 55
WAVE_READY = 66

# Define master commands
START_PHASE_1 = 1
START_PHASE_1_POST = 2
START_PHASE_2 = 3
START_PHASE_3 = 4
START_PHASE_4 = 5
SUB_GRID = 6


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
    data = (N, W, T, R, waves)
    sub_grid_length = int(N // sqrt(no_workers))
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

            # Send start phase 1 signals to workers
            for k in range(1, no_workers + 1):
                comm.send(True, dest=k, tag=START_PHASE_1)

            # Wait for all workers to finish phase 1
            for k in range(no_workers):
                res = comm.recv(source=MPI.ANY_SOURCE, tag=READY_1)
                if not res:
                    print("Error occured after phase 1")

            # Post process phase 1
            for k in range(1, no_workers + 1):
                comm.send(True, dest=k, tag=START_PHASE_1_POST)

            # Wait for all workers to finish post phase 1
            for k in range(no_workers):
                res = comm.recv(source=MPI.ANY_SOURCE, tag=READY_1_POST)
                if not res:
                    print("Error occured after post phase 1")

            # Send start phase 2 signals to workers
            for k in range(1, no_workers + 1):
                comm.send(True, dest=k, tag=START_PHASE_2)

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
    MASTER = 0

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
                # Send master ready after wave flag
                time.sleep(1)
                comm.send(True, dest=MASTER, tag=WAVE_READY)
            elif tag == START_PHASE_1:
                print("Processor", rank, "starting phase 1")
                phase1()
                # sleep thread for one second
                time.sleep(1)
                comm.send(True, dest=MASTER, tag=READY_1)
            elif tag == START_PHASE_1_POST:
                print("Processor", rank, "starting post phase 1")
                post_phase1()
                time.sleep(1)
                comm.send(True, dest=MASTER, tag=READY_1_POST)
            elif tag == START_PHASE_2:
                print("Processor", rank, "starting phase 2")
                phase2()
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
