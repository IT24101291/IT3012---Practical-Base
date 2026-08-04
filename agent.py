class SimpleReflexAgent:
    """
    Simple Reflex Agent.

    This agent uses only the current percept.
    It does not store previous percepts or actions.
    """

    def sense_and_act(self, percept: dict) -> str:
        # Condition 1: Food exists in the current cell.
        if percept["food_here"]:
            return "suck"

        # Condition 2: A wall exists directly ahead.
        if percept["wall_ahead"]:
            return "turn_left"

        # Otherwise, continue moving forward.
        return "move_forward"


class ModelBasedAgent:
    """
    Model-Based Agent.

    This agent maintains an internal model containing:
    - relative position
    - current direction
    - visited cells
    - blocked cells
    - percept history
    - previous action
    """

    DIRECTIONS = ["Up", "Right", "Down", "Left"]

    DIRECTION_VECTORS = {
        "Up": (0, 1),
        "Right": (1, 0),
        "Down": (0, -1),
        "Left": (-1, 0),
    }

    def __init__(self):
        # Relative starting position.
        self.position = (0, 0)

        # The agent initially faces upward.
        self.direction = "Up"

        # Internal memory.
        self.visited_cells = set()
        self.blocked_cells = set()
        self.percept_history = []

        self.last_action = None
        self.last_percept = None

    def get_next_cell(self, direction):
        """Calculate the next relative cell in a given direction."""

        x, y = self.position
        dx, dy = self.DIRECTION_VECTORS[direction]

        return x + dx, y + dy

    def get_left_direction(self):
        """Return the direction to the agent's left."""

        current_index = self.DIRECTIONS.index(self.direction)
        left_index = (current_index - 1) % len(self.DIRECTIONS)

        return self.DIRECTIONS[left_index]

    def get_right_direction(self):
        """Return the direction to the agent's right."""

        current_index = self.DIRECTIONS.index(self.direction)
        right_index = (current_index + 1) % len(self.DIRECTIONS)

        return self.DIRECTIONS[right_index]

    def update_internal_state(self):
        """
        Update the internal position or direction using the previous action.

        This represents part of the transition model.
        """

        if self.last_action == "turn_left":
            self.direction = self.get_left_direction()

        elif self.last_action == "turn_right":
            self.direction = self.get_right_direction()

        elif (
            self.last_action == "move_forward"
            and self.last_percept is not None
            and not self.last_percept["wall_ahead"]
        ):
            self.position = self.get_next_cell(self.direction)

    def select_action(self, percept):
        """Use the current percept and internal memory to choose an action."""

        if percept["food_here"]:
            return "suck"

        forward_cell = self.get_next_cell(self.direction)

        left_direction = self.get_left_direction()
        left_cell = self.get_next_cell(left_direction)

        right_direction = self.get_right_direction()
        right_cell = self.get_next_cell(right_direction)

        # Move forward when the path is clear and unvisited.
        if (
            not percept["wall_ahead"]
            and forward_cell not in self.visited_cells
        ):
            return "move_forward"

        # Example memory-based condition from the lab sheet:
        # IF wall_ahead AND left_is_visited THEN turn_right.
        if (
            percept["wall_ahead"]
            and left_cell in self.visited_cells
            and right_cell not in self.blocked_cells
        ):
            return "turn_right"

        # Prefer an unvisited cell on the left.
        if (
            left_cell not in self.visited_cells
            and left_cell not in self.blocked_cells
        ):
            return "turn_left"

        # Otherwise, try an unvisited cell on the right.
        if (
            right_cell not in self.visited_cells
            and right_cell not in self.blocked_cells
        ):
            return "turn_right"

        # Move forward when it is still possible.
        if (
            not percept["wall_ahead"]
            and forward_cell not in self.blocked_cells
        ):
            return "move_forward"

        # Final fallback rules.
        if left_cell not in self.blocked_cells:
            return "turn_left"

        return "turn_right"

    def sense_and_act(self, percept: dict) -> str:
        # 1. Update the state using the previous action.
        self.update_internal_state()

        # 2. Record the current relative position.
        self.visited_cells.add(self.position)

        # 3. Record a detected wall as a blocked cell.
        forward_cell = self.get_next_cell(self.direction)

        if percept["wall_ahead"]:
            self.blocked_cells.add(forward_cell)

        # 4. Store the current percept and previous action.
        self.percept_history.append(
            {
                "position": self.position,
                "direction": self.direction,
                "percept": percept.copy(),
                "last_action": self.last_action,
            }
        )

        # 5. Select an action using the percept and memory.
        action = self.select_action(percept)

        # 6. Save information for the next cycle.
        self.last_action = action
        self.last_percept = percept.copy()

        return action