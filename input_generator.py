import random

def generate_input_file(file_name, N, W, T, R):
    """
    Generates an input file for the project.
    
    Parameters:
        file_name (str): Name of the output file.
        N (int): Size of the grid (N x N).
        W (int): Number of waves.
        T (int): Number of units per faction per wave.
        R (int): Number of rounds per wave.
    """
    def generate_unique_coordinates(N, T):
        """Generates T unique coordinates within the N x N grid."""
        coordinates = set()
        while len(coordinates) < T:
            coordinates.add((random.randint(0, N - 1), random.randint(0, N - 1)))
        return list(coordinates)
    
    with open(file_name, 'w') as f:
        # Write the header: N, W, T, R
        f.write(f"{N} {W} {T} {R}\n")
        
        for wave in range(W):
            f.write(f"Wave {wave + 1}:\n")
            
            # Generate unique coordinates for each faction
            all_coordinates = set()
            factions = {'E': [], 'F': [], 'W': [], 'A': []}
            
            for faction in factions.keys():
                faction_coords = generate_unique_coordinates(N, T)
                while any(coord in all_coordinates for coord in faction_coords):
                    faction_coords = generate_unique_coordinates(N, T)
                factions[faction] = faction_coords
                all_coordinates.update(faction_coords)
            
            # Write the faction coordinates to the file
            for faction, coords in factions.items():
                coords_str = ', '.join(f"{r} {c}" for r, c in coords)
                f.write(f"{faction}: {coords_str}\n")

if __name__ == "__main__":
    # Example usage
    grid_size = 100  # Grid size N x N
    num_waves = 10   # Number of waves
    units_per_faction = 15  # Number of units per faction per wave
    rounds_per_wave = 10  # Number of rounds per wave
    
    generate_input_file("input.txt", grid_size, num_waves, units_per_faction, rounds_per_wave)
    print("Input file 'input.txt' has been generated.")
