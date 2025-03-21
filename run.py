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


class BattleshipGame:
    def __init__(self):
        self.player_name = ""
        self.board_size = 0
        self.player_board = None
        self.computer_board = None
        self.ships_config = []
        self.game_over = False
        self.player_shots = 0
        self.computer_shots = 0
        self.player_hits = 0
        self.computer_hits = 0

    def clear_screen(self):
        # Clear the screen for better user experience
        os.system('cls' if os.name == 'nt' else 'clear')

    def setup_game(self):
        self.clear_screen()
        print("\n" + "=" * 50)
        print("Welcome to BATTLESHIP COMMAND LINE GAME!")
        print("=" * 50 + "\n")

        # Get player name
        self.player_name = input("Enter your name: ")
        if not self.player_name:
            self.player_name = "Player"

        # Get board size
        while True:
            try:
                size_input = input("Enter board size (5-10): ")
                self.board_size = int(size_input)
                if 5 <= self.board_size <= 10:
                    break
                else:
                    print("Board size must be between 5 and 10.")
            except ValueError:
                print("Please enter a valid number.")

        # Define ships based on board size
        if self.board_size <= 6:
            self.ships_config = [
                ("Destroyer", 2),
                ("Submarine", 3),
                ("Battleship", 4)
            ]
        else:
            self.ships_config = [
                ("Destroyer", 2),
                ("Submarine", 3),
                ("Cruiser", 3),
                ("Battleship", 4),
                ("Carrier", 5)
            ]

        # Create boards
        self.player_board = Board(self.board_size)
        self.computer_board = Board(self.board_size)

        # Place ships
        print("\nPlacing ships...")
        self.player_board.place_ships_randomly(self.ships_config)
        self.computer_board.place_ships_randomly(self.ships_config)

        print(f"\n{self.player_name}'s board has been set up with the \
              following ships:")
        for name, size in self.ships_config:
            print(f"- {name} ({size} cells)")

        input("\nPress Enter to start the game...")

    def display_boards(self):
        self.clear_screen()
        print("\n" + "=" * 50)
        print(f"{self.player_name}'s Board:")
        self.player_board.display(hide_ships=False)
        print("\nComputer's Board:")
        self.computer_board.display(hide_ships=True)
        print("=" * 50)
        print(f"Your shots: {self.player_shots} (Hits: {self.player_hits})")
        print(f"Computer shots: {self.computer_shots} \
              (Hits: {self.computer_hits})")
        print("=" * 50 + "\n")

    def parse_coordinates(self, coordinate_str):
        # Convert input like "A5" to row and column indices
        if len(coordinate_str) < 2:
            return None, None

        col_str = coordinate_str[0].upper()
        row_str = coordinate_str[1:]

        # Convert column letter to index (A=0, B=1, etc.)
        if not 'A' <= col_str <= chr(64 + self.board_size):
            return None, None

        col = ord(col_str) - 65  # Convert ASCII to 0-based index

        # Convert row number to index
        try:
            row = int(row_str) - 1  # Convert to 0-based index
            if not (0 <= row < self.board_size):
                return None, None
        except ValueError:
            return None, None

        return row, col

    def player_turn(self):
        valid_shot = False

        while not valid_shot:
            shot_input = input(f"{self.player_name}, enter coordinates to \
                               fire (e.g., A5): ")
            row, col = self.parse_coordinates(shot_input)

            if row is None or col is None:
                print(f"Invalid coordinates! Please use format like A1 to "
                      f"{chr(64 + self.board_size)}{self.board_size}")
                continue

            # Check if these coordinates were already targeted
            if (row, col) in self.computer_board.shots:
                print("You've already fired at these coordinates. Try again.")
                continue

            valid_shot = True
            self.player_shots += 1
            result, ship_name = self.computer_board.receive_shot(row, col)

            if result == "miss":
                print("You missed!")
            elif result == "hit":
                print("Hit! You struck an enemy ship!")
                self.player_hits += 1
            elif result == "sunk":
                print(f"You sunk the enemy's {ship_name}!")
                self.player_hits += 1

            time.sleep(1)

    def computer_turn(self):
        print("\nComputer's turn...")
        time.sleep(1)

        # Simple AI: randomly select an untargeted cell
        available_shots = [
            (r, c) for r in range(self.board_size) for c in
            range(self.board_size)
            if (r, c) not in self.player_board.shots
        ]

        if available_shots:
            row, col = random.choice(available_shots)
            self.computer_shots += 1
            result, ship_name = self.player_board.receive_shot(row, col)

            # Convert coordinates to human-readable format (e.g., A5)
            col_letter = chr(65 + col)
            human_coords = f"{col_letter}{row + 1}"

            if result == "miss":
                print(f"Computer fires at {human_coords} and misses!")
            elif result == "hit":
                print(f"Computer fires at {human_coords} and hits your ship!")
                self.computer_hits += 1
            elif result == "sunk":
                print(f"Computer fires at {human_coords} and sinks your \
                     {ship_name}!")
                self.computer_hits += 1

            time.sleep(1)

    def check_game_over(self):
        # Check if all player ships are sunk
        player_ships_sunk = all(ship.is_sunk for ship in
                                self.player_board.ships)
        if player_ships_sunk:
            self.display_boards()
            print(f"\nGame Over! All of {self.player_name}'s ships have \
                  been sunk!")
            print("Computer wins!")
            self.game_over = True
            return True

        # Check if all computer ships are sunk
        computer_ships_sunk = all(ship.is_sunk for ship in
                                  self.computer_board.ships)
        if computer_ships_sunk:
            self.display_boards()
            print("\nCongratulations! You've sunk all of the computer's \
                  ships!")
            print(f"{self.player_name} wins!")
            self.game_over = True
            return True

        return False

    def play_game(self):
        self.setup_game()

        while not self.game_over:
            self.display_boards()
            self.player_turn()
            if self.check_game_over():
                break
            self.computer_turn()
            if self.check_game_over():
                break

        # Ask to play again
        play_again = input("\nWould you like to play again? (y/n): ").lower()
        if play_again == 'y':
            # Reset game state
            self.__init__()
            self.play_game()
        else:
            print("\nThank you for playing Battleship! Goodbye!")
