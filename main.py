from mpi4py import MPI
from math import sqrt
import time
from unit_funcs import *
from enum_util import *


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
            if location_grid[new_x][new_y] != ".":  # If there is already a unit
                if not (new_x == cur_x and new_y == cur_y):
                    continue
            # Calculate the 5x5 subgrid at whose center lies the new_x and new_y
            attack_grid = []
            for i in range(new_x - 2, new_x + 3):
                row = []
                for j in range(new_y - 2, new_y + 3):
                    row.append(location_grid[i][j])
                attack_grid.append(row)

            new_attackables = calc_air_attackables_count(
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


# Function that returns the processor id and relative positions which the air unit will belong to in its new location
# Note new_x and new_y are in extended subgrid
def get_processor_id_loc_air(new_x, new_y, sub_grid_length, cur_id, no_workers):
    k = int(sqrt(no_workers))
    m = sub_grid_length
    if new_x < 3:
        if new_y < 3:
            return ((cur_id - k - 1), (m - 1), (m - 1))
        elif new_y > sub_grid_length + 2:
            return ((cur_id - k + 1), (m - 1), 0)
        elif new_y >= 3 and new_y <= sub_grid_length + 2:
            return ((cur_id - k), (m - 1), (new_y - 3))
        else:
            print("Error in get_processor_id_air")
    elif new_x > sub_grid_length + 2:
        if new_y < 3:
            return ((cur_id + k - 1), 0, (m - 1))
        elif new_y > sub_grid_length + 2:
            return ((cur_id + k + 1), 0, 0)
        elif new_y >= 3 and new_y <= sub_grid_length + 2:
            return (cur_id + k, 0, new_y - 3)
        else:
            print("Error in get_processor_id_air")
    elif new_x >= 3 and new_x <= sub_grid_length + 2:
        if new_y < 3:
            return (cur_id - 1, new_x - 3, m - 1)
        elif new_y > sub_grid_length + 2:
            return (cur_id + 1, new_x - 3, 0)
        elif new_y >= 3 and new_y <= sub_grid_length + 2:
            return (cur_id, new_x - 3, new_y - 3)
        else:
            print("Error in get_processor_id_air")


# Returns the relative x and relative y in subgrid
def get_sub_grid_loc_from_global(x, y, sub_grid_len):
    rel_x = x % sub_grid_len
    rel_y = y % sub_grid_len
    return (rel_x, rel_y)


# Returns the global x and global y from relative x and y in subgrid
def get_global_loc_from_sub_grid(rel_x, rel_y, sub_grid_len, processor_id, no_workers):
    processor_loc_x = (processor_id - 1) // int(sqrt(no_workers))
    processor_loc_y = (processor_id - 1) % int(sqrt(no_workers))
    global_x = processor_loc_x * sub_grid_len + rel_x
    global_y = processor_loc_y * sub_grid_len + rel_y
    return (global_x, global_y)


def get_id_from_global_pos(x, y, sub_grid_len, no_workers):
    proc_y = y // sub_grid_len
    proc_x = x // sub_grid_len
    return proc_x * int(sqrt(no_workers)) + proc_y + 1


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

            # Check if the rouns is the last of this wave
            last_round = j == R - 1

            # To avoid deadlock seperate phase 1, phase 1 post  to 4 groups
            # First group: x and y are even
            # Second group: x odd y even
            # Third group: x even y odd
            # Fourth group: x and y are even

            groups = [EVEN_EVEN, ODD_EVEN, EVEN_ODD, ODD_ODD]

            for cur_group in groups:
                # Send start phase 1 signals to workers
                print(f"Running group {get_group_string(cur_group)} of phase 1")
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
                # send start post phase 1 signals to workers
                print(f"Running group {get_group_string(cur_group)} of post phase 1")
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
                print(f"Running group {get_group_string(cur_group)} of phase 2")
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

            for cur_group in groups:
                # Send start post phase 2 signals to workers
                print(f"Running group {get_group_string(cur_group)} of post phase 2")
                for k in range(1, no_workers + 1):
                    cur_type = get_type_from_id(k, no_workers)
                    receive = cur_type == cur_group
                    worker_data = {}
                    worker_data["success"] = True
                    worker_data["receive"] = receive
                    worker_data["cur_group"] = cur_group
                    comm.send(worker_data, dest=k, tag=START_PHASE_2_POST)

                # Wait for all workers to finish post phase 2
                for k in range(no_workers):
                    res = comm.recv(source=MPI.ANY_SOURCE, tag=READY_2_POST)
                    if not res:
                        print("Error occured after post phase 2")

            # Send start phase 3 signals to workers
            for k in range(1, no_workers + 1):
                comm.send(True, dest=k, tag=START_PHASE_3)

            # Wait for all workers to finish phase 3
            for k in range(no_workers):
                res = comm.recv(source=MPI.ANY_SOURCE, tag=READY_3)
                if not res:
                    print("Error occured after phase 3")

            iteration = [""]
            if last_round:
                iteration = groups

            for cur_group in iteration:
                # Send start phase 4 signals to workers
                for k in range(1, no_workers + 1):
                    cur_type = get_type_from_id(k, no_workers)
                    worker_data = {}
                    worker_data["success"] = True
                    worker_data["last_round"] = last_round
                    worker_data["receive"] = cur_type == cur_group
                    worker_data["cur_group"] = cur_group
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
    # this array is cleared in post post phase 1
    airs_to_place = []

    # all the units that will be attacked in resolution phase,
    # this list is calculated in phase 2
    # the attacked units in different processors are transmitted in post phase 2
    all_units_to_attack = []

    # this list contains all the fire units that killed some unit and needs to be buffed
    fire_units_to_buff = []

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
            print("Inside receive of processor", rank)
            sources = get_receiver_source_list(rank, no_workers)
            len_sub_grid = len(sub_grid)  # x represents border length of subgrid
            extended_sub_grid = [
                ["." for _ in range(len_sub_grid + 6)] for _ in range(len_sub_grid + 6)
            ]
            # Place sub grid in the middle of the extended sub grid
            for i in range(len_sub_grid):
                for j in range(len_sub_grid):
                    extended_sub_grid[i + 3][j + 3] = sub_grid[i][j]
            print("Initial subgrid of processor", rank, "is")
            print_grid(sub_grid, len_sub_grid)
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
            print_grid(extended_sub_grid, len_sub_grid + 6)

            # Find the optimal location of air units
            for row in sub_grid:
                for unit in row:
                    if unit == ".":
                        continue
                    if unit.faction == AIR:
                        air_x, air_y = get_sub_grid_loc_from_global(
                            unit.x, unit.y, len_sub_grid
                        )
                        extended_air_x = air_x + 3
                        extended_air_y = air_y + 3
                        search_grid = []
                        for ii in range(extended_air_x - 3, extended_air_x + 4):
                            row = []
                            for jj in range(extended_air_y - 3, extended_air_y + 4):
                                row.append(extended_sub_grid[ii][jj])
                            search_grid.append(row)

                        print("*******")
                        debug_print_grid(search_grid)
                        new_x, new_y = optimum_air_location(
                            search_grid
                        )  # relative pos to the 7x7 search grid
                        print(f"New x found: {new_x} and new y found: {new_y}")
                        # now convert this pos to sub_grid_len + 6 x sub_grid_len + 6 extended grid
                        extended_new_pos_x = extended_air_x + new_x - 3
                        extended_new_pos_y = extended_air_y + new_y - 3
                        print(
                            "In extended grid new x and y are: ",
                            extended_new_pos_x,
                            extended_new_pos_y,
                        )
                        dest_id, rel_x, rel_y = get_processor_id_loc_air(
                            extended_new_pos_x,
                            extended_new_pos_y,
                            len_sub_grid,
                            rank,
                            no_workers,
                        )
                        airs_to_place.append((dest_id, rel_x, rel_y, unit))

            for s in airs_to_place:
                print(s)

    # places air units in a given grid, and merges if necessary
    def post_phase1(rank, cur_group, receive):
        if not receive:
            destinations = get_sender_destination_list(rank, no_workers, cur_group)
            for dest in destinations:
                airs_to_send = []
                for air in airs_to_place:
                    air_dest, rel_x, rel_y, unit = air
                    if air_dest == dest:
                        airs_to_send.append((dest, rel_x, rel_y, unit))
            comm.send(airs_to_send, dest=dest, tag=AIR_NEW_LOC_INFO)
        elif receive:
            sources = get_receiver_source_list(rank, no_workers)
            for source in sources:
                new_airs_from_src = comm.recv(source=source, tag=AIR_NEW_LOC_INFO)
                for new_air in new_airs_from_src:
                    airs_to_place.append(new_air)
            # Remove air units from subgrid, place them in other phase
            for grid_x in range(len(sub_grid)):
                for grid_y in range(len(sub_grid)):
                    if sub_grid[grid_x][grid_y] == ".":
                        continue
                    if sub_grid[grid_x][grid_y].faction == AIR:
                        sub_grid[grid_x][grid_y] = "."

    def post_post_phase1():
        for air in airs_to_place:
            dest_id, rel_x, rel_y, unit = air
            if dest_id == rank:
                global_x, global_y = get_global_loc_from_sub_grid(
                    rel_x, rel_y, len(sub_grid), rank, no_workers
                )
                unit.x = global_x
                unit.y = global_y
                if sub_grid[rel_x][rel_y] == ".":
                    sub_grid[rel_x][rel_y] = unit
                elif sub_grid[rel_x][rel_y].faction == AIR:
                    # Merge 2 units
                    sub_grid[rel_x][rel_y].hp += unit.hp
                    if sub_grid[rel_x][rel_y].hp > sub_grid[rel_x][rel_y].max_hp:
                        sub_grid[rel_x][rel_y].hp = sub_grid[rel_x][rel_y].max_hp
                    sub_grid[rel_x][rel_y].attack += unit.attack
                else:
                    print("ERROR in post post phase 1, merge with other unit")
            else:
                print("ERROR in post post phase 1")
        airs_to_place.clear()

    def phase2(rank, cur_group, receive):

        if receive:
            sources = get_receiver_source_list(rank, no_workers)
            len_sub_grid = len(sub_grid)
            extended_sub_grid = [
                ["." for _ in range(len_sub_grid + 6)] for _ in range(len_sub_grid + 6)
            ]
            # Place sub grid in the middle of the extended sub grid
            for i in range(len_sub_grid):
                for j in range(len_sub_grid):
                    extended_sub_grid[i + 3][j + 3] = sub_grid[i][j]
            # print("Initial subgrid of processor", rank, "is")
            # print_grid(sub_grid, len_sub_grid)
            # print(f"Processor {rank} is receiving the followings: ")
            for source in sources:
                sub_grid_part = comm.recv(source=source, tag=ATTACK_LOC_INFO)
                # debug_print_grid(sub_grid_part)
                relative_pos = calc_relative_pos(rank, source, no_workers)
                # print(f"From source: {source} with relative pos: ")
                # print_relative_pos(relative_pos)
                append_source_to_extended(
                    extended_sub_grid, sub_grid_part, relative_pos
                )
            print("after receive")

            # print("Extended subgrid of processor", rank, "is")
            # print_grid(extended_sub_grid, len_sub_grid + 6)

            for col_idx in range(len(sub_grid)):
                for row_idx in range(len(sub_grid[0])):
                    unit = sub_grid[col_idx][row_idx]
                    if unit == ".":
                        continue
                    # Create 5x5 array whose center is the unit
                    extended_x = col_idx + 3
                    extended_y = row_idx + 3
                    search_grid = []
                    for ii in range(extended_x - 2, extended_x + 3):
                        row = []
                        for jj in range(extended_y - 2, extended_y + 3):
                            row.append(extended_sub_grid[ii][jj])
                        search_grid.append(row)
                    # Returns the list of attack enemies
                    # each element is of the format (dest_id, rel_x, rel_y, source_unit)
                    units_to_attack = unit.attack_or_heal(unit, search_grid)
                    for unit_to_attack in units_to_attack:
                        all_units_to_attack.append((unit, unit_to_attack))

            print("Ending here")

        else:  # Shares border data
            destinations = get_sender_destination_list(rank, no_workers, cur_group)
            for dest in destinations:
                shared_sub_grid_part = get_subgrid_to_share_air(
                    sub_grid, rank, dest, no_workers
                )
                comm.send(shared_sub_grid_part, dest=dest, tag=ATTACK_LOC_INFO)

    def post_phase2(rank, cur_group, receive):
        if receive:
            sources = get_receiver_source_list(rank, no_workers)
            for source in sources:
                unit_vectors = comm.recv(source=source, tag=DAMAGE_LIST_INFO)
                for unit_vector in unit_vectors:
                    all_units_to_attack.append(unit_vector)
        else:  # Share data
            destinations = get_sender_destination_list(rank, no_workers, cur_group)
            for dest in destinations:
                units_vectors_to_send = []
                for unit_vector in all_units_to_attack:
                    source_unit, dest_unit = unit_vector
                    dest_id = get_id_from_global_pos(
                        dest_unit.x, dest_unit.y, len(sub_grid), no_workers
                    )
                    if dest_id == dest:
                        units_vectors_to_send.append(unit_vector)
                        all_units_to_attack.remove(unit_vector)
                comm.send(units_vectors_to_send, dest=dest, tag=DAMAGE_LIST_INFO)

    def phase3(rank, cur_group, receive):
        # Apply all the damages in the list
        for unit_vector in all_units_to_attack:
            source, dest = unit_vector
            dest_processor_id = get_id_from_global_pos(
                dest.x, dest.y, len(sub_grid), no_workers
            )
            if dest_processor_id != rank:
                print("Communication error in phase 3")
            dest_x, dest_y = dest.x, dest.y
            local_x, local_y = get_sub_grid_loc_from_global(
                dest_x, dest_y, len(sub_grid)
            )
            dest = sub_grid[local_x][local_y]
            dest.damage_queue += source.attack
            if source.faction == FIRE:
                dest.fire_attackers.append(source)

        # Apply damages
        for row_idx in range(len(sub_grid)):
            for col_idx in range(len(sub_grid)):
                unit = sub_grid[row_idx][col_idx]
                if unit == ".":
                    continue
                fires_to_buff, is_dead = unit.apply_damage()
                if is_dead:
                    sub_grid[row_idx][col_idx] = "."
                    for fire_to_buf in fires_to_buff:
                        fire_units_to_buff.append(fire_to_buf)
                unit.fire_attackers.clear()
                unit.damage_queue = 0

        all_units_to_attack.clear()

        if receive:
            sources = get_receiver_source_list(rank, no_workers)
            for source in sources:
                fire_units = comm.recv(source=source, tag=FIRE_LIST_INFO)
                for fire_unit in fire_units:
                    fire_units_to_buff.append(fire_unit)
            for fire_unit in fire_units_to_buff:
                fire_unit.attack += 1
                if fire_unit.attack > 6:
                    fire_unit.attack = 6
                fire_units_to_buff.remove(fire_unit)
        else:  # Share data
            destinations = get_sender_destination_list(rank, no_workers, cur_group)
            for dest in destinations:
                fire_units_to_send = []
                for fire_unit in fire_units_to_buff:
                    dest_id = get_id_from_global_pos(
                        fire_unit.x, fire_unit.y, len(sub_grid), no_workers
                    )
                    if dest_id == dest:
                        fire_units_to_send.append(fire_unit)
                        fire_units_to_buff.remove(fire_unit)
                comm.send(fire_units_to_send, dest=dest, tag=FIRE_LIST_INFO)

    def phase4(last_round, receive, cur_group):
        # Assert all untis to attack and fire buff lists are empty
        if len(all_units_to_attack) != 0 or len(fire_units_to_buff) != 0:
            print("Error in phase 4 about lists")
        pass
    
        # Apply healing
        for row_idx in range(len(sub_grid)):
            for col_idx in range(len(sub_grid)):
                unit = sub_grid[row_idx][col_idx]
                if unit == ".":
                    continue
                unit.heal()
                
        if last_round:
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
                time.sleep(0.5)
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
                time.sleep(0.5)
                comm.send(True, dest=MASTER, tag=READY_1)
            elif tag == START_PHASE_1_POST:
                print("Processor", rank, "starting post phase 1")
                success = incoming_data["success"]
                if not success:
                    print("Erron in post phase1")
                receive = incoming_data["receive"]
                cur_group = incoming_data["cur_group"]
                post_phase1(rank, cur_group, receive)
                time.sleep(0.5)
                comm.send(True, dest=MASTER, tag=READY_1_POST)
            elif tag == START_PHASE_1_POST_POST:
                print("Processor", rank, "starting post post phase 1")
                post_post_phase1()
                time.sleep(0.5)
                print("Sub grid of processor", rank, "after post post phase 1")
                debug_print_grid(sub_grid)
                comm.send(True, dest=MASTER, tag=READY_1_POST_POST)
            elif tag == START_PHASE_2:
                print("Processor", rank, "starting phase 2")
                success = incoming_data["success"]
                if not success:
                    print("Erron in post phase1")
                receive = incoming_data["receive"]
                cur_group = incoming_data["cur_group"]
                phase2(rank, cur_group, receive)
                time.sleep(0.5)
                comm.send(True, dest=MASTER, tag=READY_2)
            elif tag == START_PHASE_2_POST:
                print("Processor", rank, "starting post phase 2")
                success = incoming_data["success"]
                if not success:
                    print("Erron in post phase2")
                receive = incoming_data["receive"]
                cur_group = incoming_data["cur_group"]
                post_phase2(rank, cur_group, receive)
                time.sleep(0.5)
                comm.send(True, dest=MASTER, tag=READY_2_POST)
            elif tag == START_PHASE_3:
                print("Processor", rank, "starting phase 3")
                phase3(rank, cur_group, receive)
                time.sleep(0.5)
                comm.send(True, dest=MASTER, tag=READY_3)

            elif tag == START_PHASE_4:
                print("Processor", rank, "starting phase 4")
                last_round = incoming_data["last_round"]
                success = incoming_data["success"]
                if not success:
                    print("Erron in post phase2")
                receive = incoming_data["receive"]
                cur_group = incoming_data["cur_group"]
                final_sub_grid = phase4(last_round, receive, cur_group)
                time.sleep(0.5)
                comm.send(final_sub_grid, dest=MASTER, tag=READY_4)

        else:
            pass
