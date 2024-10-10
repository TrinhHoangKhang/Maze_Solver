from pygame_app import run_simulation

# Note: ChatGPT referenced
def handle_terminal():
    # Define valid algorithms
    valid_algos = ['A*', 'DFS', 'BFS']
    algo = input("Enter search algo (A*, DFS, BFS): ")

    # Ensure the chosen algorithm is valid
    while algo not in valid_algos:
        print(
            f"Invalid choice! Please choose one of the following: {', '.join(valid_algos)}")
        algo = input("Enter search algo (A*, DFS, BFS): ")

    # Get maze size with default value
    maze_size_input = input("Enter maze size (default 40): ")
    # Use 40 if no input
    maze_size = int(maze_size_input) if maze_size_input else 40

    # Get square size with default value
    square_size_input = input("Enter square size (default 15): ")
    # Use 15 if no input
    square_size = int(square_size_input) if square_size_input else 15

    # Get random mode choice
    while True:
        random_input = input("Activate random mode? (y/n): ").strip().lower()
        if random_input in ('y', 'yes'):
            random_mode = True
            break
        elif random_input in ('n', 'no'):
            random_mode = False
            break
        else:
            print("Invalid input! Please enter 'y' for yes or 'n' for no.")

    # Call the run_simulation function with the validated inputs
    run_simulation(algo, maze_size, maze_size, square_size, random_mode)


if __name__ == "__main__":

    handle_terminal()
