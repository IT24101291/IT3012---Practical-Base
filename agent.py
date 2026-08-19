# agent.py

from collections import deque
import heapq


class SearchAgent:
    """
    Goal-Based / Planning Agent for Practical 03.

    The agent can use:
    - Breadth-First Search (BFS)
    - Depth-First Search (DFS)
    - Uniform-Cost Search (UCS)

    It creates a complete path to a food pellet and then
    executes that plan one action at a time.
    """

    def __init__(self):

        # Stores the sequence of planned actions.
        self.plan = []

        # Change this value to:
        # 'BFS', 'DFS', or 'UCS'
        self.active_algo = 'UCS'

    # =====================================================
    # FIND VALID NEIGHBOURS
    # =====================================================
    def get_neighbors(self, position, grid_size, walls):
        """
        Return all valid neighboring cells and the action
        required to reach each neighbor.
        """

        x, y = position
        width, height = grid_size

        # IMPORTANT:
        # These directions match visual_grid_game.py
        #
        # Up    -> y + 1
        # Down  -> y - 1
        # Left  -> x - 1
        # Right -> x + 1

        possible_moves = [
            ((x, y + 1), 'Up'),
            ((x, y - 1), 'Down'),
            ((x - 1, y), 'Left'),
            ((x + 1, y), 'Right'),
        ]

        neighbors = []

        for next_position, action in possible_moves:

            nx, ny = next_position

            # Check that the new position:
            # 1. stays inside the grid
            # 2. is not a wall

            if (
                0 <= nx < width
                and 0 <= ny < height
                and next_position not in walls
            ):
                neighbors.append(
                    (next_position, action)
                )

        return neighbors

    # =====================================================
    # FIND CLOSEST FOOD
    # =====================================================
    def find_closest_food(self, position, all_food):
        """
        Select the food pellet that is closest to the agent
        using Manhattan distance.
        """

        if not all_food:
            return None

        x, y = position

        closest_food = min(
            all_food,
            key=lambda food:
                abs(food[0] - x)
                + abs(food[1] - y)
        )

        return tuple(closest_food)

    # =====================================================
    # BREADTH-FIRST SEARCH
    # =====================================================
    def bfs_search(self, start, goal, grid_size, walls):
        """
        BFS uses a FIFO queue.

        It explores the shallowest states first.
        """

        # Frontier stores:
        # (current_position, path_so_far)

        frontier = deque()

        frontier.append(
            (start, [])
        )

        # Reached prevents repeated states.
        reached = {start}

        while frontier:

            # FIFO:
            # Remove the oldest node.
            current_position, path = frontier.popleft()

            # Goal test
            if current_position == goal:
                return path

            # Expand current node
            for next_position, action in self.get_neighbors(
                current_position,
                grid_size,
                walls
            ):

                if next_position not in reached:

                    reached.add(next_position)

                    new_path = path + [action]

                    frontier.append(
                        (
                            next_position,
                            new_path
                        )
                    )

        # No path found
        return []

    # =====================================================
    # DEPTH-FIRST SEARCH
    # =====================================================
    def dfs_search(self, start, goal, grid_size, walls):
        """
        DFS uses a LIFO stack.

        It explores the deepest states first.
        """

        # Frontier stores:
        # (current_position, path_so_far)

        frontier = [
            (start, [])
        ]

        reached = {start}

        while frontier:

            # LIFO:
            # Remove the most recently added node.
            current_position, path = frontier.pop()

            # Goal test
            if current_position == goal:
                return path

            # Expand node
            for next_position, action in self.get_neighbors(
                current_position,
                grid_size,
                walls
            ):

                if next_position not in reached:

                    reached.add(next_position)

                    new_path = path + [action]

                    frontier.append(
                        (
                            next_position,
                            new_path
                        )
                    )

        # No path found
        return []

    # =====================================================
    # UNIFORM-COST SEARCH
    # =====================================================
    def ucs_search(self, start, goal, grid_size, walls):
        """
        UCS uses a priority queue.

        The node with the smallest total path cost g(n)
        is expanded first.
        """

        # Frontier stores:
        # (cost, position, path)

        frontier = []

        heapq.heappush(
            frontier,
            (
                0,
                start,
                []
            )
        )

        # Store the cheapest known cost
        # for each reached state.
        reached = {}

        while frontier:

            cost, current_position, path = heapq.heappop(
                frontier
            )

            # Goal test
            if current_position == goal:
                return path

            # If this position has already been reached
            # using a cheaper path, ignore this path.
            if (
                current_position in reached
                and reached[current_position] <= cost
            ):
                continue

            reached[current_position] = cost

            # Expand node
            for next_position, action in self.get_neighbors(
                current_position,
                grid_size,
                walls
            ):

                # Every movement costs 1 in this grid.
                new_cost = cost + 1

                new_path = path + [action]

                heapq.heappush(
                    frontier,
                    (
                        new_cost,
                        next_position,
                        new_path
                    )
                )

        # No path found
        return []

    # =====================================================
    # SENSE AND ACT
    # =====================================================
    def sense_and_act(self, percept: dict):
        """
        Receive the environment percept.

        If there is no existing plan:
        1. Find the closest food.
        2. Run BFS / DFS / UCS.
        3. Save the resulting actions in self.plan.

        Then execute the plan one action at a time.
        """

        # Current agent position
        start = tuple(
            percept['agent_pos']
        )

        # Size of the environment
        grid_size = tuple(
            percept['grid_size']
        )

        # Convert walls to tuples
        walls = {
            tuple(wall)
            for wall in percept['walls']
        }

        # Convert food positions to tuples
        all_food = [
            tuple(food)
            for food in percept['all_food']
        ]

        # If there is no food left,
        # there is nothing to search for.
        if not all_food:
            return None

        # =================================================
        # CREATE A NEW PLAN
        # =================================================
        if not self.plan:

            # Find nearest food pellet.
            goal = self.find_closest_food(
                start,
                all_food
            )

            # ---------------------------------------------
            # BFS
            # ---------------------------------------------
            if self.active_algo == 'BFS':

                self.plan = self.bfs_search(
                    start,
                    goal,
                    grid_size,
                    walls
                )

            # ---------------------------------------------
            # DFS
            # ---------------------------------------------
            elif self.active_algo == 'DFS':

                self.plan = self.dfs_search(
                    start,
                    goal,
                    grid_size,
                    walls
                )

            # ---------------------------------------------
            # UCS
            # ---------------------------------------------
            elif self.active_algo == 'UCS':

                self.plan = self.ucs_search(
                    start,
                    goal,
                    grid_size,
                    walls
                )

            else:

                print(
                    "Invalid search algorithm:",
                    self.active_algo
                )

                return None

        # =================================================
        # EXECUTE FIRST ACTION FROM THE PLAN
        # =================================================
        if self.plan:

            return self.plan.pop(0)

        # If no path exists
        return None