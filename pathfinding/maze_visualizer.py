"""
Pathfinding visualizer  —  A* / BFS / DFS on a grid.

Features
  - pick the algorithm (A*, BFS, DFS)
  - Auto-run (Run/Pause) + single Step
  - Restart button (clears the search, keeps your walls)
  - left-drag = draw walls, right-drag = erase, plus Clear / Random maze
  - speed slider

The maze is KNOWN to the algorithm (this is a search visualizer, not an
unknown-maze mouse). Start = top-left (green), Goal = bottom-right (red).

Run:  python maze_visualizer.py
"""

import heapq
import random
import tkinter as tk
from collections import deque
from tkinter import ttk

ROWS, COLS = 25, 35        # grid size (cells)
CELL       = 22            # pixel size of each cell
WALL_DENSITY = 0.28        # for the random-maze button

# colors
C_EMPTY    = "#ffffff"
C_WALL     = "#2c3e50"
C_START    = "#2ecc71"
C_GOAL     = "#e74c3c"
C_EXPLORED = "#aed6f1"     # already expanded
C_FRONTIER = "#f7dc6f"     # waiting in the frontier
C_PATH     = "#f39c12"     # final path
C_GRID     = "#d5d8dc"

NEIGHBORS = [(-1, 0), (0, 1), (1, 0), (0, -1)]   # up, right, down, left


# --------------------------------------------------------------------------- #
#  Pure search logic (no GUI) — one expansion per step() so the UI can animate #
# --------------------------------------------------------------------------- #
class Solver:
    def __init__(self, walls, start, goal, algo):
        self.walls = walls          # 2D list[bool]
        self.rows = len(walls)
        self.cols = len(walls[0])
        self.start = start
        self.goal = goal
        self.algo = algo

        self.came_from = {start: None}
        self.explored = set()        # expanded (light blue)
        self.frontier_set = {start}  # pending (yellow)
        self.path = []
        self.done = False
        self.found = False

        if algo == "BFS":
            self.frontier = deque([start])          # FIFO queue
        elif algo == "DFS":
            self.frontier = [start]                 # LIFO stack
        else:  # A*
            self.g = {start: 0}
            self.counter = 0
            self.frontier = [(self._h(start), 0, start)]   # min-heap on f

    def _h(self, cell):                              # Manhattan distance
        return abs(cell[0] - self.goal[0]) + abs(cell[1] - self.goal[1])

    def _neighbors(self, cell):
        r, c = cell
        for dr, dc in NEIGHBORS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols and not self.walls[nr][nc]:
                yield (nr, nc)

    def step(self):
        """Expand exactly one node."""
        if self.done:
            return

        # pop the next node according to the algorithm
        if self.algo == "BFS":
            if not self.frontier:
                self._finish(False); return
            current = self.frontier.popleft()
        elif self.algo == "DFS":
            while self.frontier and self.frontier[-1] in self.explored:
                self.frontier.pop()
            if not self.frontier:
                self._finish(False); return
            current = self.frontier.pop()
        else:  # A* — skip stale heap entries
            current = None
            while self.frontier:
                _, _, cell = heapq.heappop(self.frontier)
                if cell not in self.explored:
                    current = cell; break
            if current is None:
                self._finish(False); return

        self.frontier_set.discard(current)
        self.explored.add(current)

        if current == self.goal:
            self._finish(True); return

        for n in self._neighbors(current):
            if self.algo == "A*":
                tentative = self.g[current] + 1
                if tentative < self.g.get(n, float("inf")):
                    self.came_from[n] = current
                    self.g[n] = tentative
                    self.counter += 1
                    heapq.heappush(self.frontier, (tentative + self._h(n), self.counter, n))
                    self.frontier_set.add(n)
            else:  # BFS / DFS
                if n not in self.explored and n not in self.frontier_set:
                    self.came_from[n] = current
                    self.frontier.append(n)
                    self.frontier_set.add(n)

    def _finish(self, found):
        self.done = True
        self.found = found
        if found:
            cell = self.goal
            while cell is not None:
                self.path.append(cell)
                cell = self.came_from[cell]
            self.path.reverse()


# --------------------------------------------------------------------------- #
#  GUI                                                                          #
# --------------------------------------------------------------------------- #
class MazeApp:
    def __init__(self, root):
        self.root = root
        root.title("Pathfinding Visualizer  —  A* / BFS / DFS")

        self.walls = [[False] * COLS for _ in range(ROWS)]
        self.start = (0, 0)
        self.goal = (ROWS - 1, COLS - 1)
        self.solver = None
        self.running = False
        self.steps = 0
        self.algo = tk.StringVar(value="A*")

        self._build_controls()

        self.canvas = tk.Canvas(root, width=COLS * CELL, height=ROWS * CELL,
                                highlightthickness=0, bg=C_GRID)
        self.canvas.pack(padx=8, pady=8)
        self.rects = [[None] * COLS for _ in range(ROWS)]
        for r in range(ROWS):
            for c in range(COLS):
                x0, y0 = c * CELL, r * CELL
                self.rects[r][c] = self.canvas.create_rectangle(
                    x0, y0, x0 + CELL, y0 + CELL, fill=C_EMPTY, outline=C_GRID)

        # left = draw wall, right = erase
        self.canvas.bind("<Button-1>", lambda e: self._paint(e, True))
        self.canvas.bind("<B1-Motion>", lambda e: self._paint(e, True))
        self.canvas.bind("<Button-3>", lambda e: self._paint(e, False))
        self.canvas.bind("<B3-Motion>", lambda e: self._paint(e, False))

        self.redraw()
        self.update_status()

    def _build_controls(self):
        bar = ttk.Frame(self.root)
        bar.pack(fill="x", padx=8, pady=(8, 0))

        ttk.Label(bar, text="Algorithm:").pack(side="left")
        algo_menu = ttk.OptionMenu(bar, self.algo, "A*", "A*", "BFS", "DFS",
                                   command=lambda _: self.reset_search())
        algo_menu.pack(side="left", padx=(2, 12))

        self.run_btn = ttk.Button(bar, text="▶ Run", command=self.toggle_run)
        self.run_btn.pack(side="left")
        ttk.Button(bar, text="⏭ Step", command=self.single_step).pack(side="left", padx=4)
        ttk.Button(bar, text="↻ Restart", command=self.reset_search).pack(side="left", padx=4)
        ttk.Button(bar, text="Clear walls", command=self.clear_walls).pack(side="left", padx=4)
        ttk.Button(bar, text="Random maze", command=self.random_maze).pack(side="left", padx=4)

        ttk.Label(bar, text="Speed:").pack(side="left", padx=(12, 2))
        self.speed = tk.IntVar(value=30)     # ms delay; lower = faster
        ttk.Scale(bar, from_=100, to=1, orient="horizontal", variable=self.speed,
                  length=120).pack(side="left")

        self.status = ttk.Label(self.root, text="", anchor="w")
        self.status.pack(fill="x", padx=10, pady=(4, 0))

    # ---- cell coloring ---------------------------------------------------- #
    def _color(self, r, c):
        cell = (r, c)
        if cell == self.start:
            return C_START
        if cell == self.goal:
            return C_GOAL
        if self.walls[r][c]:
            return C_WALL
        if self.solver:
            if cell in self.solver.path:
                return C_PATH
            if cell in self.solver.frontier_set:
                return C_FRONTIER
            if cell in self.solver.explored:
                return C_EXPLORED
        return C_EMPTY

    def redraw(self):
        for r in range(ROWS):
            for c in range(COLS):
                self.canvas.itemconfig(self.rects[r][c], fill=self._color(r, c))

    # ---- wall editing ----------------------------------------------------- #
    def _paint(self, event, wall):
        c, r = event.x // CELL, event.y // CELL
        if not (0 <= r < ROWS and 0 <= c < COLS):
            return
        if (r, c) in (self.start, self.goal) or self.walls[r][c] == wall:
            return
        self.walls[r][c] = wall
        if self.solver:                 # editing invalidates the current search
            self.reset_search()
        else:
            self.canvas.itemconfig(self.rects[r][c], fill=self._color(r, c))

    # ---- buttons ---------------------------------------------------------- #
    def toggle_run(self):
        if self.running:
            self.running = False
            self.run_btn.config(text="▶ Run")
        else:
            if self.solver and self.solver.done:
                self.reset_search()
            self.running = True
            self.run_btn.config(text="⏸ Pause")
            self._loop()

    def _loop(self):
        if not self.running:
            return
        if self.do_step():              # returns True when finished
            self.running = False
            self.run_btn.config(text="▶ Run")
            return
        self.root.after(self.speed.get(), self._loop)

    def single_step(self):
        self.running = False
        self.run_btn.config(text="▶ Run")
        self.do_step()

    def do_step(self):
        if self.solver is None:
            self.solver = Solver(self.walls, self.start, self.goal, self.algo.get())
            self.steps = 0
        if not self.solver.done:
            self.solver.step()
            self.steps += 1
        self.redraw()
        self.update_status()
        return self.solver.done

    def reset_search(self):
        self.running = False
        self.run_btn.config(text="▶ Run")
        self.solver = None
        self.steps = 0
        self.redraw()
        self.update_status()

    def clear_walls(self):
        self.walls = [[False] * COLS for _ in range(ROWS)]
        self.reset_search()

    def random_maze(self):
        self.walls = [[random.random() < WALL_DENSITY for _ in range(COLS)]
                      for _ in range(ROWS)]
        self.walls[self.start[0]][self.start[1]] = False
        self.walls[self.goal[0]][self.goal[1]] = False
        self.reset_search()

    def update_status(self):
        msg = f"{self.algo.get()}   |   steps: {self.steps}"
        if self.solver and self.solver.done:
            if self.solver.found:
                msg += f"   |   PATH FOUND, length {len(self.solver.path)}"
            else:
                msg += "   |   NO PATH"
        self.status.config(text=msg)


def main():
    root = tk.Tk()
    MazeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
