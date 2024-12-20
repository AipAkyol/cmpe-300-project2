# This file contains all the enumerations and related functions

from math import sqrt

# Define faction enum
EARTH = "E"
FIRE = "F"
WATER = "W"
AIR = "A"

# DEFINE READFY FLAGS
READY_1 = 11  # Phase 1 is complete and ready for next
READY_1_POST = 22
READY_1_POST_POST = 23
READY_2 = 33
READY_2_POST = 34
READY_3 = 44
READY_4 = 55
WAVE_READY = 66

# Inter Worker Tags
AIR_LOC_INFO = 432
AIR_NEW_LOC_INFO = 543
ATTACK_LOC_INFO = 654 
DAMAGE_LIST_INFO = 765
FIRE_LIST_INFO = 876

# Define master commands
START_PHASE_1 = 1
START_PHASE_1_POST = 2
START_PHASE_1_POST_POST = 3
START_PHASE_2 = 4
START_PHASE_2_POST = 41
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


def get_group_string(group):
    if group == EVEN_EVEN:
        return "EVEN_EVEN"
    elif group == ODD_EVEN:
        return "ODD_EVEN"
    elif group == EVEN_ODD:
        return "EVEN_ODD"
    elif group == ODD_ODD:
        return "ODD_ODD"


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