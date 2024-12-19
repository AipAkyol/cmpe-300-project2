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

# Define master commands
START_PHASE_1 = 1
START_PHASE_1_POST = 2
START_PHASE_1_POST_POST = 3
START_PHASE_2 = 4
START_PHASE_3 = 5
START_PHASE_4 = 6
SUB_GRID = 7

# Define receiver enumerations
# For example in ODD_ODD group only the processors with odd x and odd y values will receive data
# this method avoids dedalocks by splitting receivers into 4 groups in checkered pattern
# notice for readability, in the below functions groups are interchangabily used as phase
EVEN_EVEN = 100
ODD_EVEN = 200
EVEN_ODD = 300
ODD_ODD = 400


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


# This function returns the list of sources current receiver expects data from
# which is all 8 directions if boundary is not violated
def get_receiver_source_list(cur_id, no_workers):
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

    # Convert coordinates to processors id
    for i in range(len(sources)):
        x, y = sources[i]
        sources[i] = x * sqrt(no_workers) + y + 1

    return sources


# This function returns the list of destinations current sender should send data
def get_sender_destination_list(cur_id, no_workers, phase):
    cur_x = (cur_id - 1) // int(sqrt(no_workers))
    cur_y = (cur_id - 1) % int(sqrt(no_workers))

    cur_type = get_type_from_id(cur_id, no_workers)

    destinations = []

    if phase == EVEN_EVEN:
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

    elif phase == ODD_ODD:
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

    elif phase == ODD_EVEN:
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

    elif phase == EVEN_ODD:
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
        destinations[i] = x * sqrt(no_workers) + y + 1

    return destinations


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

            # To avoid deadlock seperate phase 1, phase 1 post  to 4 groups
            # First group: x and y are even
            # Second group: x odd y even
            # Third group: x even y odd
            # Fourth group: x and y are even

            groups = [EVEN_EVEN, ODD_EVEN, EVEN_ODD, ODD_ODD]

            for cur_group in groups:
                # Send start phase 1 signals to workers
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
    def phase1(rank, cur_group, receive):
        pass

    # Function to run in phase 2 which is the post processing of phase 1
    # places air units in a given grid, and merges if necessary
    def post_phase1(rank, cur_group, receive):
        pass

    def phase2(receive):
        pass

    def phase3():
        pass

    def phase4(send_back):
        pass

    sub_grid = []
    # this list holds the future positions of air units in post post phase 1
    # The format will be as follows:
    # (processor_id, rel_x, rel_y, unit)
    # where processor_id holds where the unit will belong in the future
    # rel_x and rel_y holds the relative position of the unit in the subgrid
    # unit holds the unit itself which will be from air faction
    airs_to_place = []

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
