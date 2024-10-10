import pygame
import numpy as np
from maze import create_maze_solver_random
from maze import Maze_Solver
import threading

def run_simulation(search_algo, maze_rows=21, maze_cols=21, square_size=15, random_mode=False):
    # Constant
    MAZE_WIDTH = maze_cols * square_size
    MAZE_HEIGHT = maze_rows * square_size
    SCREEN_HEIGHT = MAZE_HEIGHT + MAZE_HEIGHT / 8
    SCREEN_WIDTH = MAZE_WIDTH

    # Basic region
    region_1 = pygame.Rect(0, 0, MAZE_WIDTH, MAZE_HEIGHT)
    region_2 = pygame.Rect(0, MAZE_HEIGHT, MAZE_WIDTH, MAZE_HEIGHT / 8)
    MAZE_SQUARE_OFFSET = 0.1 * square_size
    BUTTON_OFFSET = 0.05 * MAZE_HEIGHT / 8
    button_1 = pygame.Rect(BUTTON_OFFSET, MAZE_HEIGHT + BUTTON_OFFSET,
                           MAZE_WIDTH / 2 - 2 * BUTTON_OFFSET, MAZE_HEIGHT / 8 - 2 * BUTTON_OFFSET)
    button_2 = pygame.Rect(MAZE_WIDTH / 2 + BUTTON_OFFSET, MAZE_HEIGHT + BUTTON_OFFSET,
                           MAZE_WIDTH / 2 - 2 * BUTTON_OFFSET, MAZE_HEIGHT / 8 - 2 * BUTTON_OFFSET)

    # Color
    REGION_1_COLOR = (0, 0, 200)            # Blue
    REGION_2_COLOR = (96, 96, 96)           # Gray
    MAZE_SQUARE_COLOR = (255, 255, 255)     # White
    START_SQUARE_COLOR = (0, 255, 0)        # Green
    END_SQUARE_COLOR = (255, 0, 0)          # Red
    WALL_COLOR = (0, 0, 0)                  # Black
    OPEN_LIST_COLOR = (255, 128, 0)         # Orange
    CLOSED_LIST_COLOR = (255, 255, 0)       # Yellow
    TRACE_ROUTE_COLOR = (255, 0, 230)        # Gray
    BUTTON_1_COLOR = (0, 200, 0)            # Green
    BUTTON_2_COLOR = (0, 200, 0)            # Green

    # Init a Maze solver
    if random_mode:
        maze_solver = create_maze_solver_random(maze_rows, maze_cols)
    else:
        maze_solver = Maze_Solver(np.zeros((maze_rows, maze_cols)))

    # State variable
    game_state = 'default'
    Running = True
    Dragging = False
    start_chosen = False
    end_chosen = False

    # ====================================================================================
    # Init pygame
    pygame.init()
    pygame.display.set_caption("Maze game")

    # Set up the window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Init the font
    font = pygame.font.SysFont(None, 40)

    # Set the clock
    clock = pygame.time.Clock()

    def draw_region():
        pygame.draw.rect(screen, REGION_1_COLOR, region_1)
        pygame.draw.rect(screen, REGION_2_COLOR, region_2)

    # Draw the Chess board
    def draw_chessboard():
        for row in range(maze_rows):
            for col in range(maze_cols):
                square_color = MAZE_SQUARE_COLOR

                if (row, col) in maze_solver.walls:
                    square_color = WALL_COLOR
                if (row, col) in maze_solver.open_list:
                    square_color = OPEN_LIST_COLOR
                if (row, col) in maze_solver.closed_set:
                    square_color = CLOSED_LIST_COLOR
                if (row, col) in maze_solver.route:
                    square_color = TRACE_ROUTE_COLOR
                if (row, col) == maze_solver.start:
                    square_color = START_SQUARE_COLOR
                if (row, col) == maze_solver.end:
                    square_color = END_SQUARE_COLOR

                pygame.draw.rect(
                    screen,
                    square_color,
                    (col * square_size + MAZE_SQUARE_OFFSET,
                     row * square_size + MAZE_SQUARE_OFFSET,
                     square_size - 2 * MAZE_SQUARE_OFFSET,
                     square_size - 2 * MAZE_SQUARE_OFFSET)
                )

    def draw_button():
        # Refresh
        pygame.draw.rect(screen, BUTTON_1_COLOR, button_1)
        text_surface = font.render('Refresh', True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=button_1.center)
        screen.blit(text_surface, text_rect)

        # Search
        pygame.draw.rect(screen, BUTTON_2_COLOR, button_2)
        text_surface = font.render('Search', True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=button_2.center)
        screen.blit(text_surface, text_rect)

    def get_square(mouse_pos):
        x, y = mouse_pos
        row = y // square_size
        col = x // square_size
        if row >= maze_rows or col >= maze_cols:
            return None
        return int(row), int(col)

    def restart_game():
        nonlocal start_chosen, end_chosen, maze_solver
        if random_mode == True:
            maze_solver = create_maze_solver_random(maze_rows, maze_cols)
        else:
            maze_solver.refresh()
        start_chosen = False
        end_chosen = False

    if not random_mode:  # Fix that wierd bug, but if in random mode we cant refresh
        restart_game()
    while Running:

        for event in pygame.event.get():
            # Check if user quit game
            if event.type == pygame.QUIT:
                Running = False

            # When there is mouse click
            if event.type == pygame.MOUSEBUTTONDOWN:
                Dragging = True

                # ===== Default state ====
                # - Freely draw
                # - Can press any button
                # - Can be reset
                if game_state == 'default':
                    square_pos = get_square(event.pos)

                    if square_pos:
                        if not start_chosen:
                            maze_solver.start = square_pos
                            start_chosen = True
                        elif not end_chosen:
                            maze_solver.end = square_pos
                            end_chosen = True
                        else:
                            # Can only draw wall if random mode is off
                            if (not random_mode) and square_pos != maze_solver.start and square_pos != maze_solver.end:
                                maze_solver.walls.add(square_pos)

                    # If start search button is cliked
                    if button_2.collidepoint(event.pos):
                        game_state = 'search'
                        if search_algo == 'BFS':
                            t = threading.Thread(
                                target=maze_solver.perform_BFS)
                            t.start()
                        elif search_algo == 'DFS':
                            t = threading.Thread(
                                target=maze_solver.perform_DFS)
                            t.start()
                        elif search_algo == 'A*':
                            t = threading.Thread(
                                target=maze_solver.perform_AStar)
                            t.start()

                    # If cliked the refresh button
                    if button_1.collidepoint(event.pos):
                        restart_game()

                # If it search state:
                # Just watch, after the search is done you can choose only refresh button
                elif game_state == 'search':
                    # Check if the search ended
                    if not t.is_alive():
                        if button_1.collidepoint(event.pos):
                            game_state = 'default'
                            restart_game()

            if event.type == pygame.MOUSEBUTTONUP:
                Dragging = False

        # Handle dragging
        if Dragging:
            square_pos = get_square(pygame.mouse.get_pos())
            # Can only add wall if the random mode is off
            if not random_mode and square_pos and square_pos != maze_solver.start and square_pos != maze_solver.end:
                maze_solver.walls.add(square_pos)

        # Draw something
        draw_chessboard()
        draw_region()
        draw_chessboard()
        draw_button()

        # Update the display
        pygame.display.flip()

        # Limit frame rates
        clock.tick(240)

    pygame.quit()
