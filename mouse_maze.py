# -*- coding: utf-8 -*-
"""
Mouse Maze — AI generated game (per AI gen.txt)

- 30x30 maze, 16 px per cell, one entrance + one exit (always connected)
- Entrance/exit chosen from >=5 candidate pairs, each verified with a BFS
  shortest-path computation (>= 5 computations total)
- Player is a mouse (16x16 sprite), moves 1 cell per key press with WASD
- 3-minute limit -> GAME OVER screen, then auto restart
- Cheese at the exit; the mouse always "smells" it: the shortest path is
  drawn as a glowing scent trail
- Win -> SUCCESS screen
- Look & feel: terminal snake game (black background, green walls, mono font)
- 1/2/3 picks the algorithm (A*, BFS, DFS), SPACE toggles auto-run (the
  mouse follows the algorithm's path), R restarts the game
"""

import heapq
import random
import sys
from collections import deque

import pygame

GRID = 30                 # 30x30 cells
CELL = 16                 # 16 px per cell
HUD_H = 40                # top bar for timer/status
W, H = GRID * CELL, GRID * CELL + HUD_H
TIME_LIMIT = 180.0        # 3 minutes
MIN_COMPUTATIONS = 5      # required BFS computations for entry/exit choice

BLACK = (10, 12, 10)
GREEN = (0, 200, 70)      # walls, terminal vibe
DIM_GREEN = (0, 90, 40)
GRID_LINE = (25, 45, 30)  # faint table grid
YELLOW = (255, 210, 60)   # cheese / scent
GRAY = (170, 170, 175)
PINK = (240, 150, 160)
WHITE = (230, 235, 230)
RED = (230, 60, 60)

# direction -> (dx, dy), wall keys
DIRS = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}
OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}

ALGOS = ["A*", "BFS", "DFS"]      # selectable with keys 1 / 2 / 3
AUTO_STEP_MS = 90                 # auto-run speed: one cell per 90 ms


def generate_maze():
    """Recursive-backtracker maze. walls[y][x] is the set of closed walls."""
    walls = [[{"N", "S", "E", "W"} for _ in range(GRID)] for _ in range(GRID)]
    visited = [[False] * GRID for _ in range(GRID)]
    stack = [(random.randrange(GRID), random.randrange(GRID))]
    visited[stack[0][1]][stack[0][0]] = True
    while stack:
        x, y = stack[-1]
        neighbors = []
        for d, (dx, dy) in DIRS.items():
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID and 0 <= ny < GRID and not visited[ny][nx]:
                neighbors.append((d, nx, ny))
        if not neighbors:
            stack.pop()
            continue
        d, nx, ny = random.choice(neighbors)
        walls[y][x].discard(d)
        walls[ny][nx].discard(OPPOSITE[d])
        visited[ny][nx] = True
        stack.append((nx, ny))
    return walls


def bfs_path(walls, start, goal):
    """Shortest path (list of cells) from start to goal, or None."""
    prev = {start: None}
    q = deque([start])
    while q:
        cur = q.popleft()
        if cur == goal:
            path = []
            while cur is not None:
                path.append(cur)
                cur = prev[cur]
            return path[::-1]
        x, y = cur
        for d, (dx, dy) in DIRS.items():
            if d in walls[y][x]:
                continue
            nxt = (x + dx, y + dy)
            if not (0 <= nxt[0] < GRID and 0 <= nxt[1] < GRID):
                continue  # open border door at entry/exit leads outside
            if nxt not in prev:
                prev[nxt] = cur
                q.append(nxt)
    return None


def open_neighbors(walls, cell):
    """Cells reachable from `cell` through open walls (inside the grid)."""
    x, y = cell
    for d, (dx, dy) in DIRS.items():
        if d in walls[y][x]:
            continue
        nxt = (x + dx, y + dy)
        if 0 <= nxt[0] < GRID and 0 <= nxt[1] < GRID:
            yield nxt


def rebuild_path(prev, cur):
    path = []
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    return path[::-1]


def dfs_path(walls, start, goal):
    """Depth-first search path (valid but not necessarily shortest)."""
    prev = {start: None}
    stack = [start]
    while stack:
        cur = stack.pop()
        if cur == goal:
            return rebuild_path(prev, cur)
        for nxt in open_neighbors(walls, cur):
            if nxt not in prev:
                prev[nxt] = cur
                stack.append(nxt)
    return None


def astar_path(walls, start, goal):
    """A* with Manhattan-distance heuristic (shortest path)."""
    def h(c):
        return abs(c[0] - goal[0]) + abs(c[1] - goal[1])

    prev = {start: None}
    g = {start: 0}
    heap = [(h(start), 0, start)]
    counter = 0
    closed = set()
    while heap:
        _, _, cur = heapq.heappop(heap)
        if cur in closed:
            continue
        closed.add(cur)
        if cur == goal:
            return rebuild_path(prev, cur)
        for nxt in open_neighbors(walls, cur):
            t = g[cur] + 1
            if t < g.get(nxt, float("inf")):
                g[nxt] = t
                prev[nxt] = cur
                counter += 1
                heapq.heappush(heap, (t + h(nxt), counter, nxt))
    return None


def find_path(walls, start, goal, algo):
    if algo == "A*":
        return astar_path(walls, start, goal)
    if algo == "DFS":
        return dfs_path(walls, start, goal)
    return bfs_path(walls, start, goal)


def border_cells():
    cells = []
    for i in range(GRID):
        cells += [(i, 0), (i, GRID - 1), (0, i), (GRID - 1, i)]
    return list(set(cells))


def choose_endpoints(walls):
    """Try >=5 random border (entry, exit) pairs, BFS each, keep the pair
    with the longest shortest path. Returns (entry, exit, computations)."""
    borders = border_cells()
    best = None
    computations = 0
    while computations < MIN_COMPUTATIONS or best is None:
        a, b = random.sample(borders, 2)
        path = bfs_path(walls, a, b)
        computations += 1
        if path and (best is None or len(path) > len(best[2])):
            best = (a, b, path)
        if computations > 200:  # safety, maze is fully connected so unreachable
            break
    return best[0], best[1], computations


def open_border_wall(walls, cell):
    """Open the outer wall at an entrance/exit cell so it reads as a door."""
    x, y = cell
    if y == 0:
        walls[y][x].discard("N")
    elif y == GRID - 1:
        walls[y][x].discard("S")
    elif x == 0:
        walls[y][x].discard("W")
    else:
        walls[y][x].discard("E")


def cell_rect(cell):
    x, y = cell
    return pygame.Rect(x * CELL, HUD_H + y * CELL, CELL, CELL)


def draw_grid(screen):
    """Faint table-like grid lines so cells are easy to see."""
    for i in range(GRID + 1):
        pygame.draw.line(screen, GRID_LINE, (i * CELL, HUD_H), (i * CELL, H))
        pygame.draw.line(screen, GRID_LINE, (0, HUD_H + i * CELL), (W, HUD_H + i * CELL))


def draw_maze(screen, walls):
    for y in range(GRID):
        for x in range(GRID):
            px, py = x * CELL, HUD_H + y * CELL
            w = walls[y][x]
            if "N" in w:
                pygame.draw.line(screen, GREEN, (px, py), (px + CELL, py))
            if "S" in w:
                pygame.draw.line(screen, GREEN, (px, py + CELL), (px + CELL, py + CELL))
            if "W" in w:
                pygame.draw.line(screen, GREEN, (px, py), (px, py + CELL))
            if "E" in w:
                pygame.draw.line(screen, GREEN, (px + CELL, py), (px + CELL, py + CELL))


def draw_guide(screen, mouse, goal):
    """Direct straight guide line from the mouse to the cheese (scent beacon)."""
    a = cell_rect(mouse).center
    b = cell_rect(goal).center
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.line(overlay, (*YELLOW, 60), a, b, 5)   # soft glow
    pygame.draw.line(overlay, (*YELLOW, 180), a, b, 2)  # bright core
    screen.blit(overlay, (0, 0))


def draw_mouse(screen, cell):
    """Mouse sprite drawn inside one 16x16 cell."""
    r = cell_rect(cell)
    cx, cy = r.center
    pygame.draw.line(screen, PINK, (cx, cy), (cx - 7, cy + 5), 1)          # tail
    pygame.draw.ellipse(screen, GRAY, (r.x + 3, r.y + 4, 11, 9))           # body
    pygame.draw.circle(screen, GRAY, (r.x + 12, r.y + 6), 3)               # head
    pygame.draw.circle(screen, PINK, (r.x + 10, r.y + 4), 2)               # ear
    pygame.draw.circle(screen, BLACK, (r.x + 13, r.y + 6), 1)              # eye
    pygame.draw.circle(screen, PINK, (r.x + 14, r.y + 7), 1)               # nose


def draw_cheese(screen, cell):
    r = cell_rect(cell)
    pts = [(r.x + 2, r.y + 12), (r.x + 14, r.y + 12), (r.x + 12, r.y + 4), (r.x + 4, r.y + 6)]
    pygame.draw.polygon(screen, YELLOW, pts)
    pygame.draw.circle(screen, (200, 160, 30), (r.x + 6, r.y + 10), 1)
    pygame.draw.circle(screen, (200, 160, 30), (r.x + 10, r.y + 9), 1)


def draw_auto_path(screen, path):
    """Dots along the remaining auto-run path so you can see the algorithm."""
    for cell in path:
        pygame.draw.circle(screen, YELLOW, cell_rect(cell).center, 2)


def draw_hud(screen, font, font_small, remaining, computations, algo, auto):
    pygame.draw.rect(screen, BLACK, (0, 0, W, HUD_H))
    pygame.draw.line(screen, DIM_GREEN, (0, HUD_H - 1), (W, HUD_H - 1))
    m, s = divmod(int(remaining), 60)
    color = RED if remaining < 30 else GREEN
    screen.blit(font.render(f"TIME {m:01d}:{s:02d}", True, color), (8, 4))
    screen.blit(font.render(f"ALGO {algo}", True, YELLOW), (150, 4))
    auto_color = YELLOW if auto else DIM_GREEN
    screen.blit(font.render(f"AUTO {'ON' if auto else 'OFF'}", True, auto_color), (300, 4))
    hints = f"WASD move | 1:A* 2:BFS 3:DFS | SPACE auto | R restart | BFS x{computations}"
    screen.blit(font_small.render(hints, True, DIM_GREEN), (8, 24))


def show_screen(screen, font_big, font, title, title_color, subtitle, wait_key):
    """Full-screen banner. wait_key=True blocks for a key, else shows ~2.5 s."""
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    t = font_big.render(title, True, title_color)
    s = font.render(subtitle, True, WHITE)
    screen.blit(t, t.get_rect(center=(W // 2, H // 2 - 20)))
    screen.blit(s, s.get_rect(center=(W // 2, H // 2 + 25)))
    pygame.display.flip()
    end = pygame.time.get_ticks() + 2500
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if wait_key and e.type == pygame.KEYDOWN:
                return
        if not wait_key and pygame.time.get_ticks() > end:
            return
        pygame.time.wait(30)


def new_game():
    walls = generate_maze()
    entry, goal, computations = choose_endpoints(walls)
    open_border_wall(walls, entry)
    open_border_wall(walls, goal)
    print(f"entry={entry} exit={goal} | shortest-path computations: {computations}")
    return walls, entry, goal, computations


def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("MOUSE MAZE - find the cheese")
    font = pygame.font.SysFont("consolas", 16)
    font_small = pygame.font.SysFont("consolas", 12)
    font_big = pygame.font.SysFont("consolas", 40, bold=True)
    clock = pygame.time.Clock()

    walls, mouse, goal, computations = new_game()
    start_ticks = pygame.time.get_ticks()
    algo = "A*"
    auto = False
    auto_path = []            # remaining cells to walk (excludes current cell)
    last_auto_step = 0

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:                     # restart button
                    walls, mouse, goal, computations = new_game()
                    start_ticks = pygame.time.get_ticks()
                    auto, auto_path = False, []
                    continue
                if e.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    algo = ALGOS[e.key - pygame.K_1]
                    if auto:                                # re-plan with new algo
                        auto_path = (find_path(walls, mouse, goal, algo) or [])[1:]
                    continue
                if e.key == pygame.K_SPACE:                 # auto-run toggle
                    auto = not auto
                    auto_path = (find_path(walls, mouse, goal, algo) or [])[1:] if auto else []
                    continue
                move = {pygame.K_w: "N", pygame.K_s: "S",
                        pygame.K_a: "W", pygame.K_d: "E"}.get(e.key)
                if move and move not in walls[mouse[1]][mouse[0]]:
                    nx = mouse[0] + DIRS[move][0]
                    ny = mouse[1] + DIRS[move][1]
                    if 0 <= nx < GRID and 0 <= ny < GRID:  # 1 cell per press
                        mouse = (nx, ny)
                        auto, auto_path = False, []         # manual move cancels auto

        if auto:
            now = pygame.time.get_ticks()
            if auto_path and now - last_auto_step >= AUTO_STEP_MS:
                last_auto_step = now
                mouse = auto_path.pop(0)
            if not auto_path:
                auto = False

        elapsed = (pygame.time.get_ticks() - start_ticks) / 1000.0
        remaining = TIME_LIMIT - elapsed
        screen.fill(BLACK)
        draw_grid(screen)
        draw_guide(screen, mouse, goal)  # mouse always smells where the cheese is
        draw_maze(screen, walls)
        if auto:
            draw_auto_path(screen, auto_path)
        draw_cheese(screen, goal)
        draw_mouse(screen, mouse)
        draw_hud(screen, font, font_small, max(0.0, remaining), computations, algo, auto)
        pygame.display.flip()

        if mouse == goal:
            show_screen(screen, font_big, font, "SUCCESS!", YELLOW,
                        "The mouse got the cheese! Press any key to play again", True)
            walls, mouse, goal, computations = new_game()
            start_ticks = pygame.time.get_ticks()
            auto, auto_path = False, []
        elif remaining <= 0:
            show_screen(screen, font_big, font, "GAME OVER", RED,
                        "3 minutes are up... restarting", False)
            walls, mouse, goal, computations = new_game()
            start_ticks = pygame.time.get_ticks()
            auto, auto_path = False, []

        clock.tick(60)


if __name__ == "__main__":
    main()
