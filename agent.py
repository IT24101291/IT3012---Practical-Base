# agent.py

from collections import deque
import heapq
import math


class SearchAgent:
    """
    Goal-Based / Planning Agent.

    Search algorithms:
    - Breadth-First Search (BFS)
    - Depth-First Search (DFS)
    - Uniform-Cost Search (UCS)
    - A* Search

    Practical 04 also includes:
    - Manhattan Distance Heuristic
    - Euclidean Distance Heuristic
    """

    def __init__(self):

        # Stores the sequence of planned actions.
        self.plan = []

        # Practical 04:
        # Use A* Search
        self.active_algo = 'AStar'


    # =====================================================
    # HEURISTIC FUNCTIONS
    # =====================================================

    def manhattan_distance(self, pos, goal):
        """
        Calculate Manhattan distance.

        h(n) = |x1 - x2| + |y1 - y2|
        """

        x1, y1 = pos
        x2, y2 = goal

        return abs(x1 - x2) + abs(y1 - y2)


    def euclidean_distance(self, pos, goal):
        """
        Calculate Euclidean distance.

        h(n) = sqrt((x1-x2)^2 + (y1-y2)^2)
        """

        x1, y1 = pos
        x2, y2 = goal

        return math.sqrt(
            (x1 - x2) ** 2 +
            (y1 - y2) ** 2
        )


    # =====================================================
    # FIND VALID NEIGHBOURS
    # =====================================================

    def get_neighbors(self, position, grid_size, walls):
        """
        Return all valid neighbouring cells and the action
        required to reach each neighbour.
        """

        x, y = position
        width, height = grid_size

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

            # Valid neighbour must:
            # 1. Stay inside the grid
            # 2. Not be a wall

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
        Select the closest food pellet using
        Manhattan distance.
        """

        if not all_food:
            return None

        closest_food = min(
            all_food,
            key=lambda food: self.manhattan_distance(
                position,
                food
            )
        )

        return tuple(closest_food)


    # =====================================================
    # BREADTH-FIRST SEARCH
    # =====================================================

    def bfs_search(self, start, goal, grid_size, walls):
        """
        BFS uses a FIFO queue.
        """

        frontier = deque()

        frontier.append(
            (start, [])
        )

        reached = {start}

        while frontier:

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

        return []


    # =====================================================
    # DEPTH-FIRST SEARCH
    # =====================================================

    def dfs_search(self, start, goal, grid_size, walls):
        """
        DFS uses a LIFO stack.
        """

        frontier = [
            (start, [])
        ]

        reached = {start}

        while frontier:

            current_position, path = frontier.pop()

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

        return []


    # =====================================================
    # UNIFORM-COST SEARCH
    # =====================================================

    def ucs_search(self, start, goal, grid_size, walls):
        """
        UCS expands the node with the smallest
        path cost g(n).
        """

        frontier = []

        # Tuple:
        # (cost, current_position, path_taken)
        heapq.heappush(
            frontier,
            (
                0,
                start,
                []
            )
        )

        reached = {}

        while frontier:

            cost, current_position, path = heapq.heappop(
                frontier
            )

            # Goal test
            if current_position == goal:
                return path

            # Skip if already reached using a cheaper cost
            if (
                current_position in reached
                and reached[current_position] <= cost
            ):
                continue

            reached[current_position] = cost

            # Expand neighbours
            for next_position, action in self.get_neighbors(
                current_position,
                grid_size,
                walls
            ):

                # Each movement has cost 1
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

        return []


    # =====================================================
    # A* SEARCH - PRACTICAL 04
    # =====================================================

    def astar_search(
        self,
        start_pos,
        goal_pos,
        walls,
        grid_size,
        heuristic_type='manhattan'
    ):
        """
        A* Search uses:

        f(n) = g(n) + h(n)

        g(n) = actual path cost from start
        h(n) = estimated cost to goal
        f(n) = estimated total cost
        """

        # Empty priority queue
        frontier = []

        # Empty set for reached states
        reached_states = set()

        # ---------------------------------------------
        # Calculate heuristic for starting position
        # ---------------------------------------------

        if heuristic_type == 'euclidean':

            start_h = self.euclidean_distance(
                start_pos,
                goal_pos
            )

        else:

            start_h = self.manhattan_distance(
                start_pos,
                goal_pos
            )

        # Starting node:
        # g(n) = 0
        # f(n) = g(n) + h(n)
        start_g = 0
        start_f = start_g + start_h

        # Required A* tuple:
        # (f_cost, g_cost, current_pos, path_taken)
        heapq.heappush(
            frontier,
            (
                start_f,
                start_g,
                start_pos,
                []
            )
        )

        # ---------------------------------------------
        # A* MAIN LOOP
        # ---------------------------------------------

        while frontier:

            (
                f_cost,
                g_cost,
                current_pos,
                path_taken
            ) = heapq.heappop(frontier)

            # Goal test
            if current_pos == goal_pos:
                return path_taken

            # Avoid processing the same state again
            if current_pos in reached_states:
                continue

            reached_states.add(current_pos)

            # -----------------------------------------
            # EXPAND FOUR ADJACENT CELLS
            # -----------------------------------------

            for next_pos, action in self.get_neighbors(
                current_pos,
                grid_size,
                walls
            ):

                if next_pos not in reached_states:

                    # Every move costs 1
                    new_g = g_cost + 1

                    # Calculate heuristic h(n)
                    if heuristic_type == 'euclidean':

                        new_h = self.euclidean_distance(
                            next_pos,
                            goal_pos
                        )

                    else:

                        new_h = self.manhattan_distance(
                            next_pos,
                            goal_pos
                        )

                    # Calculate:
                    # f(n) = g(n) + h(n)
                    new_f = new_g + new_h

                    # Add current action to path
                    new_path = path_taken + [action]

                    # Push into priority queue
                    heapq.heappush(
                        frontier,
                        (
                            new_f,
                            new_g,
                            next_pos,
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
        Receive information from the environment.

        If there is no existing plan:
        1. Find the closest food pellet.
        2. Run the selected search algorithm.
        3. Store the returned actions in self.plan.

        The agent then executes one action at a time.
        """

        # Current agent position
        start = tuple(
            percept['agent_pos']
        )

        # Grid size
        grid_size = tuple(
            percept['grid_size']
        )

        # Convert walls into tuples
        walls = {
            tuple(wall)
            for wall in percept['walls']
        }

        # Food positions
        all_food = [
            tuple(food)
            for food in percept['all_food']
        ]

        # No food remaining
        if not all_food:
            return None


        # =================================================
        # CREATE A NEW PLAN
        # =================================================

        if not self.plan:

            # Find closest food pellet
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


            # ---------------------------------------------
            # A* SEARCH - PRACTICAL 04
            # ---------------------------------------------

            elif self.active_algo == 'AStar':

                self.plan = self.astar_search(
                    start,
                    goal,
                    walls,
                    grid_size,
                    heuristic_type='manhattan'
                )


            else:

                print(
                    "Invalid search algorithm:",
                    self.active_algo
                )

                return None


        # =================================================
        # EXECUTE FIRST ACTION FROM PLAN
        # =================================================

        if self.plan:

            return self.plan.pop(0)

        return None


# =========================================================
# PRACTICAL 04 - HEURISTIC TESTING CHECKPOINT
# =========================================================

if __name__ == "__main__":

    agent = SearchAgent()

    start_test = (0, 0)
    goal_test = (3, 4)

    print(
        "Manhattan:",
        agent.manhattan_distance(
            start_test,
            goal_test
        )
    )

    print(
        "Euclidean:",
        agent.euclidean_distance(
            start_test,
            goal_test
        )
    )