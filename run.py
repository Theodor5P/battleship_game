import random
import os
import time


class Ship:
    def __init__(self, name, size):
        self.name = name
        self.size = size
        self.hits = 0
        self.coordinates = []
        self.is_sunk = False

    def hit(self):
        self.hits += 1
        if self.hits == self.size:
            self.is_sunk = True
            return True
        return False
    

class Board:
    def __init__(self, size):
        self.size = size
        self.grid = [["~" for _ in range(size)] for _ in range(size)]
        self.ships = []
        self.shots = set()

    def display(self, hide_ships=True):
        # Display column headers (A, B, C, etc.)
        print("  ", end="")
        for i in range(self.size):
            print(chr(65 + i), end=" ")
        print()

        # Display rows with row numbers
        for i in range(self.size):
            print(f"{i + 1:2d}", end=" ")
            for j in range(self.size):
                cell = self.grid[i][j]
                # Hide ships on opponent's board
                if hide_ships and cell == "O":
                    print("~", end=" ")
                else:
                    print(cell, end=" ")
            print()

    def place_ship(self, ship, row, col, is_horizontal):
        # Check if the ship fits on the board
        if is_horizontal:
            if col + ship.size > self.size:
                return False
            # Check if the cells are free
            for c in range(col, col + ship.size):
                if self.grid[row][c] != "~":
                    return False
            # Place the ship
            for c in range(col, col + ship.size):
                self.grid[row][c] = "O"
                ship.coordinates.append((row, c))
        else:  # vertical placement
            if row + ship.size > self.size:
                return False
            # Check if the cells are free
            for r in range(row, row + ship.size):
                if self.grid[r][col] != "~":
                    return False
            # Place the ship
            for r in range(row, row + ship.size):
                self.grid[r][col] = "O"
                ship.coordinates.append((r, col))

        self.ships.append(ship)
        return True

    def place_ships_randomly(self, ships_config):
        for name, size in ships_config:
            ship = Ship(name, size)
            placed = False

            # Try to place the ship until it fits
            attempt = 0
            max_attempts = 100  # prevent infinite loop
            while not placed and attempt < max_attempts:
                is_horizontal = random.choice([True, False])
                if is_horizontal:
                    row = random.randint(0, self.size - 1)
                    col = random.randint(0, self.size - ship.size)
                else:
                    row = random.randint(0, self.size - ship.size)
                    col = random.randint(0, self.size - 1)

                placed = self.place_ship(ship, row, col, is_horizontal)
                attempt += 1

            if not placed:
                # If we couldn't place a ship after many attempts, start over
                self.grid = [["~" for _ in range(self.size)] for _ in
                             range(self.size)]
                self.ships = []
                return self.place_ships_randomly(ships_config)

        return True

    def receive_shot(self, row, col):
        # Record the shot
        self.shots.add((row, col))

        # If the shot hits water
        if self.grid[row][col] == "~":
            self.grid[row][col] = "M"  # Miss
            return "miss", None

        # If the shot hits a ship
        elif self.grid[row][col] == "O":
            self.grid[row][col] = "X"  # Hit
            # Find which ship was hit
            for ship in self.ships:
                if (row, col) in ship.coordinates:
                    sunk = ship.hit()
                    if sunk:
                        return "sunk", ship.name
                    return "hit", None

        # If the cell was already shot (shouldn't happen with proper game
        # logic)
        return "already_shot", None


