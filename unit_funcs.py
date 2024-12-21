from enum_util import EARTH, FIRE, WATER, AIR

# This function calculates the attackable units given by the air unit
# takes a subgrid (5x5) at whose center lies the air unit we are interested at
def calc_air_attackables(attack_grid):
    cur_x = 2
    cur_y = 2
    attackables = []

    # Chek bottom location
    if attack_grid[cur_x + 1][cur_y] == ".":
        if attack_grid[cur_x + 2][cur_y] != ".":
          # Check if unit is enemy
          if attack_grid[cur_x + 2][cur_y].faction != AIR:
            attackables.append(attack_grid[cur_x + 2][cur_y])
    else:
        # Check if unit is enemy
        if attack_grid[cur_x + 1][cur_y].faction != AIR:
            attackables.append(attack_grid[cur_x + 1][cur_y])

    # Check top location
    if attack_grid[cur_x - 1][cur_y] == ".":
        if attack_grid[cur_x - 2][cur_y] != ".":
          # Check if unit is enemy
          if attack_grid[cur_x - 2][cur_y].faction != AIR:
            attackables.append(attack_grid[cur_x - 2][cur_y])
    else:
        # Check if unit is enemy
        if attack_grid[cur_x - 1][cur_y].faction != AIR:
            attackables.append(attack_grid[cur_x - 1][cur_y])

    # Check left location
    if attack_grid[cur_x][cur_y - 1] == ".":
        if attack_grid[cur_x][cur_y - 2] != ".":
          # Check if unit is enemy
          if attack_grid[cur_x][cur_y - 2].faction != AIR:
            attackables.append(attack_grid[cur_x][cur_y - 2])
    else:
        # Check if unit is enemy
        if attack_grid[cur_x][cur_y - 1].faction != AIR:
            attackables.append(attack_grid[cur_x][cur_y - 1])

    # Check right location
    if attack_grid[cur_x][cur_y + 1] == ".":
        if attack_grid[cur_x][cur_y + 2] != ".":
          # Check if unit is enemy
          if attack_grid[cur_x][cur_y + 2].faction != AIR:
            attackables.append(attack_grid[cur_x][cur_y + 2])
    else:
        # Check if unit is enemy
        if attack_grid[cur_x][cur_y + 1].faction != AIR:
            attackables.append(attack_grid[cur_x][cur_y + 1])

    # Check top left
    if attack_grid[cur_x - 1][cur_y - 1] == ".":
        if attack_grid[cur_x - 2][cur_y - 2] != ".":
          # Check if unit is enemy
          if attack_grid[cur_x - 2][cur_y - 2].faction != AIR:
            attackables.append(attack_grid[cur_x - 2][cur_y - 2])
    else:
        # Check if unit is enemy
        if attack_grid[cur_x - 1][cur_y - 1].faction != AIR:
            attackables.append(attack_grid[cur_x - 1][cur_y - 1])

    # Check top right
    if attack_grid[cur_x - 1][cur_y + 1] == ".":
        if attack_grid[cur_x - 2][cur_y + 2] != ".":
          # Check if unit is enemy
          if attack_grid[cur_x - 2][cur_y + 2].faction != AIR:
            attackables.append(attack_grid[cur_x - 2][cur_y + 2])
    else:
        # Check if unit is enemy
        if attack_grid[cur_x - 1][cur_y + 1].faction != AIR:
            attackables.append(attack_grid[cur_x - 1][cur_y + 1])

    # Check bottom left
    if attack_grid[cur_x + 1][cur_y - 1] == ".":
        if attack_grid[cur_x + 2][cur_y - 2] != ".":
          # Check if unit is enemy
          if attack_grid[cur_x + 2][cur_y - 2].faction != AIR:
            attackables.append(attack_grid[cur_x + 2][cur_y - 2])
    else:
        # Check if unit is enemy
        if attack_grid[cur_x + 1][cur_y - 1].faction != AIR:
            attackables.append(attack_grid[cur_x + 1][cur_y - 1])

    # Check bottom right
    if attack_grid[cur_x + 1][cur_y + 1] == ".":
        if attack_grid[cur_x + 2][cur_y + 2] != ".":
          # Check if unit is enemy
          if attack_grid[cur_x + 2][cur_y + 2].faction != AIR:
            attackables.append(attack_grid[cur_x + 2][cur_y + 2])
    else:
        # Check if unit is enemy
        if attack_grid[cur_x + 1][cur_y + 1].faction != AIR:
            attackables.append(attack_grid[cur_x + 1][cur_y + 1])

    return attackables

# This function calculates the attackable units given by the eart unit
# takes a subgrid (5x5) at whose center lies the earth unit we are interested at
def calc_earth_attackables(attack_grid):
    cur_x = 2
    cur_y = 2
    attackables = []

    # Check bottom location
    if attack_grid[cur_x + 1][cur_y] != ".":
        # Check if unit is enemy
        if attack_grid[cur_x + 1][cur_y].faction != EARTH:
            attackables.append(attack_grid[cur_x + 1][cur_y])

    # Check top location
    if attack_grid[cur_x - 1][cur_y] != ".":
        # Check if unit is enemy
        if attack_grid[cur_x - 1][cur_y].faction != EARTH:
            attackables.append(attack_grid[cur_x - 1][cur_y])

    # Check left location
    if attack_grid[cur_x][cur_y - 1] != ".":
        # Check if unit is enemy
        if attack_grid[cur_x][cur_y - 1].faction != EARTH:
            attackables.append(attack_grid[cur_x][cur_y - 1])

    # Check right location
    if attack_grid[cur_x][cur_y + 1] != ".":
        # Check if unit is enemy
        if attack_grid[cur_x][cur_y + 1].faction != EARTH:
            attackables.append(attack_grid[cur_x][cur_y + 1])

    return attackables

# This function calculates the attackable units given by the water unit
# takes a subgrid (5x5) at whose center lies the water unit we are interested at
def calc_water_attackables(attack_grid):
    cur_x = 2
    cur_y = 2
    attackables = []

    # Water attack only to diagonals
    
    # Check top left
    if attack_grid[cur_x - 1][cur_y - 1] != ".":
        # Check if unit is enemy
        if attack_grid[cur_x - 1][cur_y - 1].faction != WATER:
            attackables.append(attack_grid[cur_x - 1][cur_y - 1])
    
    # Check top right
    if attack_grid[cur_x - 1][cur_y + 1] != ".":
        # Check if unit is enemy
        if attack_grid[cur_x - 1][cur_y + 1].faction != WATER:
            attackables.append(attack_grid[cur_x - 1][cur_y + 1])
            
    # Check bottom left
    if attack_grid[cur_x + 1][cur_y - 1] != ".":
        # Check if unit is enemy
        if attack_grid[cur_x + 1][cur_y - 1].faction != WATER:
            attackables.append(attack_grid[cur_x + 1][cur_y - 1])
            
    # Check bottom right
    if attack_grid[cur_x + 1][cur_y + 1] != ".":
        # Check if unit is enemy
        if attack_grid[cur_x + 1][cur_y + 1].faction != WATER:
            attackables.append(attack_grid[cur_x + 1][cur_y + 1])
            
    return attackables
  
# This function calculates the attackable units given by the fire unit
# takes a subgrid (5x5) at whose center lies the fire unit we are interested at
# Fire attacks all directions
def calc_fire_attackables(attack_grid):
    cur_x = 2
    cur_y = 2
    attackables = []

    # Check bottom location
    if attack_grid[cur_x + 1][cur_y] != ".":
        # Check if unit is enemy
        if attack_grid[cur_x + 1][cur_y].faction != FIRE:
            attackables.append(attack_grid[cur_x + 1][cur_y])

    # Check top location
    if attack_grid[cur_x - 1][cur_y] != ".":
        # Check if unit is enemy
        if attack_grid[cur_x - 1][cur_y].faction != FIRE:
            attackables.append(attack_grid[cur_x - 1][cur_y])

    # Check left location
    if attack_grid[cur_x][cur_y - 1] != ".":
        # Check if unit is enemy
        if attack_grid[cur_x][cur_y - 1].faction != FIRE:
            attackables.append(attack_grid[cur_x][cur_y - 1])

    # Check right location
    if attack_grid[cur_x][cur_y + 1] != ".":
        # Check if unit is enemy
        if attack_grid[cur_x][cur_y + 1].faction != FIRE:
            attackables.append(attack_grid[cur_x][cur_y + 1])

    # Check top left
    if attack_grid[cur_x - 1][cur_y - 1] != ".":
        # Check if unit is enemy
        if attack_grid[cur_x - 1][cur_y - 1].faction != FIRE:
            attackables.append(attack_grid[cur_x - 1][cur_y - 1])

    # Check top right
    if attack_grid[cur_x - 1][cur_y + 1] != ".":
        # Check if unit is enemy
        if attack_grid[cur_x - 1][cur_y + 1].faction != FIRE:
            attackables.append(attack_grid[cur_x - 1][cur_y + 1])

    # Check bottom left
    if attack_grid[cur_x + 1][cur_y - 1] != ".":
        # Check if unit is enemy
        if attack_grid[cur_x + 1][cur_y - 1].faction != FIRE:
            attackables.append(attack_grid[cur_x + 1][cur_y - 1])
    
    # Check bottom right
    if attack_grid[cur_x + 1][cur_y + 1] != ".":
        # Check if unit is enemy
        if attack_grid[cur_x + 1][cur_y + 1].faction != FIRE:
            attackables.append(attack_grid[cur_x + 1][cur_y + 1])
            
    return attackables


def calc_air_attackables_count(attack_grid):
    return len(calc_air_attackables(attack_grid))



class Unit:
    def set_props(self, faction):
        self.will_heal = False
        self.damage_queue = 0
        self.fire_attackers = []
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

    def attack_or_heal(self, source_unit, search_grid):
        # Decite to heal
        if self.hp < self.max_hp / 2:
            print(self.faction, "unit at", self.x, self.y, "has health" , self.hp, "/", self.max_hp, "and skip attack to heal")
            self.will_heal = True
            return []
        else:  # Attack
            if source_unit.faction == EARTH:
                attackables = calc_earth_attackables(search_grid)
            elif source_unit.faction == FIRE:
                attackables = calc_fire_attackables(search_grid)
            elif source_unit.faction == WATER:
                attackables = calc_water_attackables(search_grid)
            elif source_unit.faction == AIR:
                attackables = calc_air_attackables(search_grid)
            #print("Attackables for unit at", self.x, self.y, "are:")
            
            # If no enmy target available heal
            if len(attackables) == 0:
                print(self.faction, "unit at", self.x, self.y, "has no valid targets")
                self.will_heal = True
            return attackables

    def heal(self):
        self.hp += self.heal_rate
        self.hp = min(self.hp, self.max_hp)
        self.will_heal = False
        print(self.faction, "unit at", self.x, self.y, "healed to", self.hp, "hp")

    def apply_damage(self):
        # Earth special ability
        is_dead = False
        if self.faction == EARTH:
            self.damage_queue = self.damage_queue // 2

        self.hp -= self.damage_queue
        print(self.faction, "at", self.x, self.y, "took", self.damage_queue , "damage and now has", self.hp, "hp")
        if self.hp <= 0:
            print(self.faction, "at", self.x, self.y, "is dead")
            is_dead = True
        

        return self.fire_attackers, is_dead
