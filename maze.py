import numpy as np
import random
from collections import deque
import time

# Return a matrix of 0(path) and 1(wall)
def generate_maze(maze_rows, maze_cols):
    maze = np.ones((maze_rows, maze_cols))
    start = (1, 1)
    parrent = {}

    def get_valid_neighbor(position):
        results = []
        row, col = position
        possible_moves = [(row - 2, col), (row, col - 2),
                          (row + 2, col), (row, col + 2)]
        random.shuffle(possible_moves)
        for move in possible_moves:
            if (
                0 <= move[0] < maze_rows and
                0 <= move[1] < maze_cols and
                move not in closed_list
            ):
                results.append(move)

        return results

    open_list = [start]
    closed_list = []
    while open_list:
        top = open_list[-1]
        open_list.pop()
        closed_list.append(top)
        maze[top] = 0
        if top != start:
            previous = parrent[top]
            maze[(previous[0] + top[0]) // 2, (previous[1] + top[1]) // 2] = 0

        valid_neighbors = get_valid_neighbor(top)
        if valid_neighbors:
            for neighbor in valid_neighbors:
                open_list.append(neighbor)
                parrent[neighbor] = top

    return maze

# Return a maze solver object
def create_maze_solver_random(maze_rows, maze_cols):
    maze = generate_maze(maze_rows, maze_cols)
    return Maze_Solver(maze)

class Maze_Solver:
    def __init__(self, maze) -> None:
        # Maze info
        self.maze_rows = maze.shape[0]
        self.maze_cols = maze.shape[1]
        self.walls = set()
        self.spaces = set()
        for row in range(self.maze_rows):
            for col in range(self.maze_cols):
                if maze[row, col] == 1:
                    self.walls.add((row, col))
                else:
                    self.spaces.add((row, col))

        # Start and Goal
        self.start = random.choice(list(self.spaces))
        self.end = random.choice(list(self.spaces))
        while self.end == self.start:
            self.end = random.choice(self.spaces)

        # info use for Search algos
        self.open_list = []
        self.closed_set = set()
        self.open_set = set()
        self.parent = {}
        self.route = []
        self.route_exist = False

    # Trace back the route using the parrent dict
    # The list it return go from end to start
    def get_route(self):
        self.route.append(self.end)
        curr = self.end

        while curr != self.start:
            curr = self.parent[curr]
            self.route.append(curr)

    # Help: BFS, DFS
    # Given a position, return list of valid neighbor
    # Valid means:
    # - Not go out of bound of the maze
    # - Exclude the ones that in either open_list or closed_list
    def find_valid_neighbors(self, position):
        final_result = []
        row, col = position
        candidates = [(row - 1, col), (row + 1, col),
                      (row, col - 1), (row, col + 1)]

        for candidate in candidates:
            if (
                0 <= candidate[0] < self.maze_cols and
                0 <= candidate[1] < self.maze_rows and
                candidate not in self.closed_set and
                candidate not in self.open_set and
                candidate not in self.walls
            ):
                final_result.append(candidate)

        return final_result

    def perform_BFS(self, wait=True, wait_time=0.02):
        self.open_list.append(self.start)
        self.open_set.add(self.start)

        while self.open_list:
            if wait:
                time.sleep(wait_time)

            # Pop the front one
            front_pos = self.open_list[0]
            self.open_list = self.open_list[1:]
            self.open_set.remove(front_pos)
            # Add it to the closed list
            self.closed_set.add(front_pos)
            # Check if it is the goal
            if front_pos == self.end:
                self.route_exist = True
                break

            # Check the valid neighbors of it
            valid_neighbors = self.find_valid_neighbors(front_pos)
            if valid_neighbors:
                # Add the neighbors to the open list
                for neighbor in valid_neighbors:
                    self.open_list.append(neighbor)
                    self.open_set.add(neighbor)
                    # Update the parrent
                    self.parent[neighbor] = front_pos

        # Update the route after done
        if self.route_exist:
            self.get_route()

    # DFS
    def perform_DFS(self, wait=True, wait_time=0.02):
        self.open_list.append(self.start)

        while self.open_list:
            if wait:
                time.sleep(wait_time)

            # Pop the top pos
            top_pos = self.open_list[-1]
            self.open_list.pop()
            self.closed_set.add(top_pos)

            if top_pos == self.end:
                self.route_exist = True
                break

            # Find the pos neighbor
            valid_neighbors = self.find_valid_neighbors(top_pos)
            if valid_neighbors:
                for neighbor in valid_neighbors:
                    self.open_list.append(neighbor)
                    # Update the parrent
                    self.parent[neighbor] = top_pos

        if self.route_exist:
            self.get_route()

    # A*
    def perform_AStar(self, wait=True, wait_time=0.02):

        def heuristic(position):
            y, x = position
            y_e, x_e = self.end
            return np.abs(x - x_e) + np.abs(y - y_e)

        def f(position):
            return heuristic(position)  # + back_cost[position]

        def find_valid_neighbor_AStar(position):
            final_result = []
            row, col = position
            candidates = [(row - 1, col), (row + 1, col),
                          (row, col - 1), (row, col + 1)]

            for candidate in candidates:
                if (
                    0 <= candidate[0] < self.maze_rows and
                    0 <= candidate[1] < self.maze_cols and
                    candidate not in self.walls and
                    candidate not in self.closed_set
                ):
                    final_result.append(candidate)

            return final_result

        back_cost = {}
        # Push the start state to the open list
        self.open_list.append(self.start)
        back_cost[self.start] = 0

        while self.open_list:
            if wait:
                time.sleep(wait_time)

            self.open_list.sort(key=lambda x: f(x), reverse=True)
            min_position = self.open_list[-1]
            self.open_list.pop()
            self.closed_set.add(min_position)

            if min_position == self.end:
                self.route_exist = True
                break

            # Find the valid neighbor
            valid_neighbors = find_valid_neighbor_AStar(min_position)
            if valid_neighbors:
                for neighbor in valid_neighbors:
                    # We dont push them into open list yet
                    # In case the neighbor already in open list
                    back_cost_this_path = back_cost[min_position] + 1
                    if neighbor in self.open_list:
                        if (neighbor not in back_cost) or (back_cost[neighbor] > back_cost_this_path):
                            back_cost[neighbor] = back_cost_this_path
                            self.parent[neighbor] = min_position
                        else:
                            pass  # Nothing happen
                    else:
                        self.open_list.append(neighbor)
                        self.parent[neighbor] = min_position
                        back_cost[neighbor] = back_cost_this_path

        if self.route_exist:
            self.get_route()

    # Refresh the search info
    def refresh(self):
        self.open_list = []
        self.open_set = set()
        self.closed_set = set()
        self.parent = {}
        self.walls = set()
        self.route = []
        self.route_exist = False
