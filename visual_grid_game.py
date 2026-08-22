import random
import tkinter as tk

# Practical 04:
# Import the SearchAgent containing BFS, DFS, UCS and A*
from agent import SearchAgent


class VisualGridHuntGame:
    """A flexible Pacman-style grid environment with configurable opponents."""

    def __init__(
        self,
        width=10,
        height=10,
        num_food=10,
        num_opponents=2,
        custom_walls=None,
    ):
        self.width = width
        self.height = height

        # Agent starts at coordinate (0, 0)
        self.agent_pos = [0, 0]

        # =================================================
        # WALLS
        # =================================================
        if custom_walls is not None:
            self.walls = set(custom_walls)
        else:
            self.walls = {
                (2, 2),
                (2, 3),
                (5, 5),
                (6, 5),
                (3, 7),
            }

        # =================================================
        # FOOD
        # =================================================
        self.food_positions = set()

        while len(self.food_positions) < num_food:
            position = (
                random.randint(0, self.width - 1),
                random.randint(0, self.height - 1),
            )

            if (
                position != (0, 0)
                and position not in self.walls
            ):
                self.food_positions.add(position)

        # =================================================
        # TOXIC TRAPS
        # =================================================
        self.toxic_traps = set()

        while len(self.toxic_traps) < 5:
            trap_position = (
                random.randint(0, self.width - 1),
                random.randint(0, self.height - 1),
            )

            if (
                trap_position != (0, 0)
                and trap_position not in self.walls
                and trap_position not in self.food_positions
            ):
                self.toxic_traps.add(trap_position)

        # =================================================
        # OPPONENTS
        # =================================================
        self.opponents = []

        while len(self.opponents) < num_opponents:
            opponent_position = [
                random.randint(0, self.width - 1),
                random.randint(0, self.height - 1),
            ]

            opponent_tuple = tuple(opponent_position)

            if (
                opponent_tuple != (0, 0)
                and opponent_tuple not in self.walls
                and opponent_tuple not in self.food_positions
                and opponent_tuple not in self.toxic_traps
                and opponent_position not in self.opponents
            ):
                self.opponents.append(opponent_position)

        self.score = 0
        self.steps = 0
        self.collision = False

    # =====================================================
    # EXPOSE GLOBAL STATE TO SEARCH AGENT
    # =====================================================
    def get_percept(self) -> dict:

        return {
            "agent_pos": list(self.agent_pos),

            "opponent_positions": [
                list(op)
                for op in self.opponents
            ],

            "smells_food": (
                tuple(self.agent_pos)
                in self.food_positions
            ),

            "hit_wall": (
                tuple(self.agent_pos)
                in self.walls
            ),

            "smells_toxin": (
                tuple(self.agent_pos)
                in self.toxic_traps
            ),

            "collision": self.collision,

            "score": self.score,

            "remaining_food": len(
                self.food_positions
            ),

            # Required information for search
            "grid_size": (
                self.width,
                self.height,
            ),

            "walls": list(
                self.walls
            ),

            "all_food": list(
                self.food_positions
            ),
        }

    # =====================================================
    # EXECUTE ACTION
    # =====================================================
    def execute_action(self, action: str):

        self.steps += 1

        new_pos = list(
            self.agent_pos
        )

        # =================================================
        # MOVE AGENT
        # =================================================
        if action == "Up":

            new_pos[1] = min(
                self.height - 1,
                new_pos[1] + 1,
            )

        elif action == "Down":

            new_pos[1] = max(
                0,
                new_pos[1] - 1,
            )

        elif action == "Left":

            new_pos[0] = max(
                0,
                new_pos[0] - 1,
            )

        elif action == "Right":

            new_pos[0] = min(
                self.width - 1,
                new_pos[0] + 1,
            )

        # =================================================
        # WALL COLLISION
        # =================================================
        if tuple(new_pos) in self.walls:

            self.score -= 5

        else:

            self.agent_pos = new_pos

        tuple_pos = tuple(
            self.agent_pos
        )

        # =================================================
        # FOOD
        # =================================================
        if tuple_pos in self.food_positions:

            self.food_positions.remove(
                tuple_pos
            )

            self.score += 20

        # =================================================
        # TOXIC TRAP
        # =================================================
        if tuple_pos in self.toxic_traps:

            self.score -= 15

        # =================================================
        # CHECK COLLISION
        # =================================================
        if any(
            op == self.agent_pos
            for op in self.opponents
        ):

            self.score -= 50
            self.collision = True

            return

        # =================================================
        # MOVE OPPONENTS
        # =================================================
        for op in self.opponents:

            move = random.choice(
                [
                    "Up",
                    "Down",
                    "Left",
                    "Right",
                    "Stay",
                ]
            )

            opponent_new_pos = list(op)

            if move == "Up":

                opponent_new_pos[1] = min(
                    self.height - 1,
                    opponent_new_pos[1] + 1,
                )

            elif move == "Down":

                opponent_new_pos[1] = max(
                    0,
                    opponent_new_pos[1] - 1,
                )

            elif move == "Left":

                opponent_new_pos[0] = max(
                    0,
                    opponent_new_pos[0] - 1,
                )

            elif move == "Right":

                opponent_new_pos[0] = min(
                    self.width - 1,
                    opponent_new_pos[0] + 1,
                )

            # Opponents cannot move through walls
            if (
                tuple(opponent_new_pos)
                not in self.walls
            ):

                op[0], op[1] = (
                    opponent_new_pos
                )

            # Collision with agent
            if op == self.agent_pos:

                self.score -= 50
                self.collision = True

                break

    # =====================================================
    # CHECK WHETHER SIMULATION IS FINISHED
    # =====================================================
    def is_done(self) -> bool:

        return (
            len(self.food_positions) == 0
            or self.steps >= 60
            or self.collision
        )


# =========================================================
# GRAPHICAL USER INTERFACE
# =========================================================
class GridGameGUI:

    """Tkinter GUI for Practical 04 A* Search."""

    def __init__(
        self,
        root,
        width=10,
        height=10,
        num_food=12,
        num_opponents=2,
        walls=None,
    ):

        self.root = root

        self.root.title(
            "IT3012 - Practical 04 - A* Informed Search"
        )

        # =================================================
        # CREATE ENVIRONMENT
        # =================================================
        self.env = VisualGridHuntGame(
            width=width,
            height=height,
            num_food=num_food,
            num_opponents=num_opponents,
            custom_walls=walls,
        )

        # =================================================
        # PRACTICAL 04 - CREATE A* SEARCH AGENT
        # =================================================
        self.agent = SearchAgent()

        # agent.py currently contains:
        # self.active_algo = 'AStar'

        # =================================================
        # GUI SIZE
        # =================================================
        max_canvas_dim = 600

        self.cell_size = max(
            20,
            min(
                max_canvas_dim // self.env.width,
                max_canvas_dim // self.env.height,
            ),
        )

        canvas_width = (
            self.env.width
            * self.cell_size
        )

        canvas_height = (
            self.env.height
            * self.cell_size
        )

        # =================================================
        # CANVAS
        # =================================================
        self.canvas = tk.Canvas(
            root,
            width=canvas_width,
            height=canvas_height,
            bg="white",
        )

        self.canvas.pack()

        # =================================================
        # INFORMATION LABEL
        # =================================================
        self.label = tk.Label(
            root,
            text="Algorithm: AStar | Score: 0 | Steps: 0",
            font=("Arial", 14),
        )

        self.label.pack(
            pady=10
        )

        # =================================================
        # START BUTTON
        # =================================================
        self.button = tk.Button(
            root,
            text="Start A* Simulation",
            command=self.run_loop,
            font=("Arial", 12),
            bg="#000066",
            fg="white",
        )

        self.button.pack(
            pady=5
        )

        self.draw_grid()

    # =====================================================
    # DRAW GRID
    # =====================================================
    def draw_grid(self):

        self.canvas.delete(
            "all"
        )

        # =================================================
        # DRAW CELLS AND WALLS
        # =================================================
        for x in range(
            self.env.width
        ):

            for y in range(
                self.env.height
            ):

                x1 = (
                    x
                    * self.cell_size
                )

                y1 = (
                    self.env.height
                    - 1
                    - y
                ) * self.cell_size

                x2 = (
                    x1
                    + self.cell_size
                )

                y2 = (
                    y1
                    + self.cell_size
                )

                color = (
                    "#64748b"
                    if (x, y) in self.env.walls
                    else "#f1f5f9"
                )

                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=color,
                    outline="#cbd5e1",
                )

                if (
                    self.cell_size >= 40
                    and (x, y) in self.env.walls
                ):

                    self.canvas.create_text(
                        x1 + self.cell_size / 2,
                        y1 + self.cell_size / 2,
                        text="W",
                        fill="white",
                        font=(
                            "Arial",
                            8,
                            "bold",
                        ),
                    )

        # =================================================
        # DRAW FOOD
        # =================================================
        for (
            food_x,
            food_y,
        ) in self.env.food_positions:

            offset = (
                self.cell_size
                * 0.25
            )

            x1 = (
                food_x
                * self.cell_size
                + offset
            )

            y1 = (
                self.env.height
                - 1
                - food_y
            ) * self.cell_size + offset

            self.canvas.create_oval(
                x1,
                y1,
                x1 + self.cell_size * 0.5,
                y1 + self.cell_size * 0.5,
                fill="#f59e0b",
                outline="#d97706",
            )

        # =================================================
        # DRAW TOXIC TRAPS
        # =================================================
        for (
            trap_x,
            trap_y,
        ) in self.env.toxic_traps:

            offset = (
                self.cell_size
                * 0.2
            )

            x1 = (
                trap_x
                * self.cell_size
                + offset
            )

            y1 = (
                self.env.height
                - 1
                - trap_y
            ) * self.cell_size + offset

            self.canvas.create_oval(
                x1,
                y1,
                x1 + self.cell_size * 0.6,
                y1 + self.cell_size * 0.6,
                fill="purple",
                outline="black",
            )

        # =================================================
        # DRAW OPPONENTS
        # =================================================
        for (
            opponent_x,
            opponent_y,
        ) in self.env.opponents:

            offset = (
                self.cell_size
                * 0.2
            )

            x1 = (
                opponent_x
                * self.cell_size
                + offset
            )

            y1 = (
                self.env.height
                - 1
                - opponent_y
            ) * self.cell_size + offset

            self.canvas.create_rectangle(
                x1,
                y1,
                x1 + self.cell_size * 0.6,
                y1 + self.cell_size * 0.6,
                fill="#990000",
                outline="#7a0000",
            )

        # =================================================
        # DRAW AGENT
        # =================================================
        agent_x, agent_y = (
            self.env.agent_pos
        )

        offset = (
            self.cell_size
            * 0.15
        )

        x1 = (
            agent_x
            * self.cell_size
            + offset
        )

        y1 = (
            self.env.height
            - 1
            - agent_y
        ) * self.cell_size + offset

        self.canvas.create_oval(
            x1,
            y1,
            x1 + self.cell_size * 0.7,
            y1 + self.cell_size * 0.7,
            fill="#000066",
            outline="#1e3a8a",
        )

    # =====================================================
    # PRACTICAL 04 - RUN A* SEARCH AGENT
    # =====================================================
    def run_loop(self):

        self.button.config(
            state="disabled"
        )

        def step():

            if not self.env.is_done():

                # Get current environment information
                percept = (
                    self.env.get_percept()
                )

                # Ask SearchAgent/A* for next action
                action = (
                    self.agent.sense_and_act(
                        percept
                    )
                )

                # No valid path
                if action is None:

                    self.label.config(
                        text="No path available."
                    )

                    self.button.config(
                        state="normal"
                    )

                    return

                # Execute action
                self.env.execute_action(
                    action
                )

                # Redraw GUI
                self.draw_grid()

                # Display A* information
                self.label.config(
                    text=(
                        f"Algorithm: "
                        f"{self.agent.active_algo}"
                        f" | Score: "
                        f"{self.env.score}"
                        f" | Steps: "
                        f"{self.env.steps}"
                        f" | Action: "
                        f"{action}"
                    )
                )

                self.root.after(
                    250,
                    step
                )

            else:

                if self.env.collision:

                    message = (
                        "Collision! Game Over! "
                        f"Final Score: "
                        f"{self.env.score}"
                    )

                else:

                    message = (
                        "Finished! "
                        f"Final Score: "
                        f"{self.env.score}"
                    )

                self.label.config(
                    text=message
                )

                self.button.config(
                    state="normal"
                )

        step()


# =========================================================
# MAIN PROGRAM
# =========================================================
if __name__ == "__main__":

    root = tk.Tk()

    app = GridGameGUI(
        root,
        width=12,
        height=12,
        num_food=15,
        num_opponents=2,
    )

    root.mainloop()