# agent.py

from collections import deque
import heapq
import math

from logic_engine import KnowledgeBase


class SearchAgent:
    """
    Goal-Based / Planning Agent.

    Search algorithms:
    - Breadth-First Search
    - Depth-First Search
    - Uniform-Cost Search
    - A* Search

    Practical 05 extension:
    - Knowledge Base
    - Forward Chaining
    - Logical feasibility checking
    """

    def __init__(self):

        # Stores planned actions
        self.plan = []

        # Use A* for the current practical
        self.active_algo = 'AStar'

        # =================================================
        # PRACTICAL 05 - KNOWLEDGE BASE
        # =================================================

        self.kb = KnowledgeBase()

        # Rule 1:
        # TargetVisible AND HasDust
        # -> SafeToEngage
        self.kb.tell_rule(
            [
                'TargetVisible',
                'HasDust'
            ],
            'SafeToEngage'
        )

        # Rule 2:
        # SafeToEngage AND BloodseekerMissing
        # -> Retreat
        self.kb.tell_rule(
            [
                'SafeToEngage',
                'BloodseekerMissing'
            ],
            'Retreat'
        )

    # =====================================================
    # HEURISTIC FUNCTIONS
    # =====================================================

    def manhattan_distance(
        self,
        pos,
        goal
    ):

        x1, y1 = pos
        x2, y2 = goal

        return (
            abs(x1 - x2)
            +
            abs(y1 - y2)
        )

    def euclidean_distance(
        self,
        pos,
        goal
    ):

        x1, y1 = pos
        x2, y2 = goal

        return math.sqrt(
            (x1 - x2) ** 2
            +
            (y1 - y2) ** 2
        )

    # =====================================================
    # VALID NEIGHBOURS
    # =====================================================

    def get_neighbors(
        self,
        position,
        grid_size,
        walls
    ):

        x, y = position

        width, height = grid_size

        possible_moves = [

            (
                (x, y + 1),
                'Up'
            ),

            (
                (x, y - 1),
                'Down'
            ),

            (
                (x - 1, y),
                'Left'
            ),

            (
                (x + 1, y),
                'Right'
            ),
        ]

        neighbors = []

        for (
            next_position,
            action
        ) in possible_moves:

            nx, ny = (
                next_position
            )

            # Reachability check:
            # inside grid and not wall
            if (
                0 <= nx < width
                and
                0 <= ny < height
                and
                next_position
                not in walls
            ):

                neighbors.append(
                    (
                        next_position,
                        action
                    )
                )

        return neighbors

    # =====================================================
    # CLOSEST FOOD
    # =====================================================

    def find_closest_food(
        self,
        position,
        all_food
    ):

        if not all_food:

            return None

        return min(
            all_food,
            key=lambda food:
                self.manhattan_distance(
                    position,
                    food
                )
        )

    # =====================================================
    # TILE FACTS
    # =====================================================

    def get_tile_facts(
        self,
        position,
        percept
    ):
        """
        Return logical facts associated
        with a particular tile.
        """

        if percept is None:

            return []

        tile_facts = percept.get(
            'tile_facts',
            {}
        )

        # Supports tuple keys
        if position in tile_facts:

            return tile_facts[
                position
            ]

        # Also supports string keys such as "1,0"
        position_key = (
            f"{position[0]},"
            f"{position[1]}"
        )

        if position_key in tile_facts:

            return tile_facts[
                position_key
            ]

        return []

    # =====================================================
    # BFS
    # =====================================================

    def bfs_search(
        self,
        start,
        goal,
        grid_size,
        walls
    ):

        frontier = deque()

        frontier.append(
            (
                start,
                []
            )
        )

        reached = {
            start
        }

        while frontier:

            (
                current_position,
                path
            ) = frontier.popleft()

            if (
                current_position
                == goal
            ):

                return path

            for (
                next_position,
                action
            ) in self.get_neighbors(
                current_position,
                grid_size,
                walls
            ):

                if (
                    next_position
                    not in reached
                ):

                    reached.add(
                        next_position
                    )

                    frontier.append(
                        (
                            next_position,
                            path + [action]
                        )
                    )

        return []

    # =====================================================
    # DFS
    # =====================================================

    def dfs_search(
        self,
        start,
        goal,
        grid_size,
        walls
    ):

        frontier = [
            (
                start,
                []
            )
        ]

        reached = {
            start
        }

        while frontier:

            (
                current_position,
                path
            ) = frontier.pop()

            if (
                current_position
                == goal
            ):

                return path

            for (
                next_position,
                action
            ) in self.get_neighbors(
                current_position,
                grid_size,
                walls
            ):

                if (
                    next_position
                    not in reached
                ):

                    reached.add(
                        next_position
                    )

                    frontier.append(
                        (
                            next_position,
                            path + [action]
                        )
                    )

        return []

    # =====================================================
    # UCS
    # =====================================================

    def ucs_search(
        self,
        start,
        goal,
        grid_size,
        walls
    ):

        frontier = []

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

            (
                cost,
                current_position,
                path
            ) = heapq.heappop(
                frontier
            )

            if (
                current_position
                == goal
            ):

                return path

            if (
                current_position
                in reached
                and
                reached[
                    current_position
                ] <= cost
            ):

                continue

            reached[
                current_position
            ] = cost

            for (
                next_position,
                action
            ) in self.get_neighbors(
                current_position,
                grid_size,
                walls
            ):

                new_cost = (
                    cost + 1
                )

                heapq.heappush(
                    frontier,
                    (
                        new_cost,
                        next_position,
                        path + [action]
                    )
                )

        return []

    # =====================================================
    # A* SEARCH
    # =====================================================

    def astar_search(
        self,
        start_pos,
        goal_pos,
        walls,
        grid_size,
        heuristic_type='manhattan',
        percept=None
    ):

        frontier = []

        reached_states = set()

        if (
            heuristic_type
            == 'euclidean'
        ):

            start_h = (
                self.euclidean_distance(
                    start_pos,
                    goal_pos
                )
            )

        else:

            start_h = (
                self.manhattan_distance(
                    start_pos,
                    goal_pos
                )
            )

        heapq.heappush(
            frontier,
            (
                start_h,
                0,
                start_pos,
                []
            )
        )

        while frontier:

            (
                f_cost,
                g_cost,
                current_pos,
                path_taken
            ) = heapq.heappop(
                frontier
            )

            if (
                current_pos
                == goal_pos
            ):

                return path_taken

            if (
                current_pos
                in reached_states
            ):

                continue

            reached_states.add(
                current_pos
            )

            for (
                next_pos,
                action
            ) in self.get_neighbors(
                current_pos,
                grid_size,
                walls
            ):

                if (
                    next_pos
                    in reached_states
                ):

                    continue

                # =========================================
                # PRACTICAL 05
                # LOGICAL FEASIBILITY CHECK
                # =========================================

                self.kb.clear_facts()

                facts = (
                    self.get_tile_facts(
                        next_pos,
                        percept
                    )
                )

                for fact in facts:

                    self.kb.tell_fact(
                        fact
                    )

                self.kb.forward_chain()

                # If Retreat is inferred,
                # this neighbour is logically infeasible.
                if (
                    'Retreat'
                    in self.kb.facts
                ):

                    continue

                # =========================================
                # NORMAL A* CALCULATION
                # =========================================

                new_g = (
                    g_cost + 1
                )

                if (
                    heuristic_type
                    == 'euclidean'
                ):

                    new_h = (
                        self.euclidean_distance(
                            next_pos,
                            goal_pos
                        )
                    )

                else:

                    new_h = (
                        self.manhattan_distance(
                            next_pos,
                            goal_pos
                        )
                    )

                new_f = (
                    new_g
                    +
                    new_h
                )

                new_path = (
                    path_taken
                    +
                    [action]
                )

                heapq.heappush(
                    frontier,
                    (
                        new_f,
                        new_g,
                        next_pos,
                        new_path
                    )
                )

        return []

    # =====================================================
    # SENSE AND ACT
    # =====================================================

    def sense_and_act(
        self,
        percept
    ):

        start = tuple(
            percept[
                'agent_pos'
            ]
        )

        grid_size = tuple(
            percept[
                'grid_size'
            ]
        )

        walls = {
            tuple(wall)
            for wall
            in percept[
                'walls'
            ]
        }

        all_food = [
            tuple(food)
            for food
            in percept[
                'all_food'
            ]
        ]

        if not all_food:

            return None

        if not self.plan:

            goal = (
                self.find_closest_food(
                    start,
                    all_food
                )
            )

            if (
                self.active_algo
                == 'BFS'
            ):

                self.plan = (
                    self.bfs_search(
                        start,
                        goal,
                        grid_size,
                        walls
                    )
                )

            elif (
                self.active_algo
                == 'DFS'
            ):

                self.plan = (
                    self.dfs_search(
                        start,
                        goal,
                        grid_size,
                        walls
                    )
                )

            elif (
                self.active_algo
                == 'UCS'
            ):

                self.plan = (
                    self.ucs_search(
                        start,
                        goal,
                        grid_size,
                        walls
                    )
                )

            elif (
                self.active_algo
                == 'AStar'
            ):

                self.plan = (
                    self.astar_search(
                        start,
                        goal,
                        walls,
                        grid_size,
                        heuristic_type='manhattan',
                        percept=percept
                    )
                )

            else:

                print(
                    "Invalid search algorithm:",
                    self.active_algo
                )

                return None

        if self.plan:

            return (
                self.plan.pop(0)
            )

        return None


# =========================================================
# TEST HEURISTICS
# =========================================================

if __name__ == "__main__":

    agent = SearchAgent()

    start_test = (
        0,
        0
    )

    goal_test = (
        3,
        4
    )

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