# Graph Report - G:/AI/HW1  (2026-07-06)

## Corpus Check
- Corpus is ~1,369 words - fits in a single context window. You may not need a graph.

## Summary
- 38 nodes · 59 edges · 8 communities (7 shown, 1 thin omitted)
- Extraction: 73% EXTRACTED · 25% INFERRED · 2% AMBIGUOUS · INFERRED: 15 edges (avg confidence: 0.89)
- Token cost: 34,084 input · 4,200 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Cheese Guide & Pathfinding|Cheese Guide & Pathfinding]]
- [[_COMMUNITY_Game Loop & Screens|Game Loop & Screens]]
- [[_COMMUNITY_Game Spec & Terminal Style|Game Spec & Terminal Style]]
- [[_COMMUNITY_Maze Generation & Rendering|Maze Generation & Rendering]]
- [[_COMMUNITY_EntryExit Selection|Entry/Exit Selection]]
- [[_COMMUNITY_Mouse Player Sprite|Mouse Player Sprite]]
- [[_COMMUNITY_Claude Code Permissions|Claude Code Permissions]]
- [[_COMMUNITY_Round Setup & Border Doors|Round Setup & Border Doors]]

## God Nodes (most connected - your core abstractions)
1. `main()` - 11 edges
2. `bfs_path()` - 7 edges
3. `generate_maze()` - 6 edges
4. `choose_endpoints()` - 6 edges
5. `draw_guide()` - 6 edges
6. `draw_mouse()` - 5 edges
7. `new_game()` - 5 edges
8. `open_border_wall()` - 4 edges
9. `cell_rect()` - 4 edges
10. `draw_cheese()` - 4 edges

## Surprising Connections (you probably didn't know these)
- `choose_endpoints()` --implements--> `Requirement: entry/exit mutually reachable, >=5 computations`  [INFERRED]
  mouse_maze.py → AI gen.txt
- `generate_maze()` --implements--> `Requirement: 30x30 maze, 16 per cell, one entry + one exit`  [INFERRED]
  mouse_maze.py → AI gen.txt
- `bfs_path()` --implements--> `Requirement: entry/exit mutually reachable, >=5 computations`  [INFERRED]
  mouse_maze.py → AI gen.txt
- `open_border_wall()` --implements--> `Requirement: 30x30 maze, 16 per cell, one entry + one exit`  [INFERRED]
  mouse_maze.py → AI gen.txt
- `draw_guide()` --implements--> `Requirement: cheese at finish, shortest path shown as scent light`  [AMBIGUOUS]
  mouse_maze.py → AI gen.txt

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Walls Grid (list of wall-sets) shared data flow** — mouse_maze_generate_maze, mouse_maze_bfs_path, mouse_maze_choose_endpoints, mouse_maze_open_border_wall, mouse_maze_draw_maze, mouse_maze_new_game, mouse_maze_main [EXTRACTED 1.00]
- **Per-frame render pipeline in game loop** — mouse_maze_draw_grid, mouse_maze_draw_guide, mouse_maze_draw_maze, mouse_maze_draw_cheese, mouse_maze_draw_mouse, mouse_maze_draw_hud [EXTRACTED 1.00]
- **Entry/exit selection via >=5 BFS computations** — mouse_maze_border_cells, mouse_maze_bfs_path, mouse_maze_choose_endpoints, mouse_maze_open_border_wall, aigen_entry_exit_connectivity [INFERRED 0.85]

## Communities (8 total, 1 thin omitted)

### Community 0 - "Cheese Guide & Pathfinding"
Cohesion: 0.32
Nodes (8): Requirement: cheese at finish, shortest path shown as scent light, Requirement: entry/exit mutually reachable, >=5 computations, bfs_path(), cell_rect(), draw_cheese(), draw_guide(), Direct straight guide line from the mouse to the cheese (scent beacon)., Shortest path (list of cells) from start to goal, or None.

### Community 1 - "Game Loop & Screens"
Cohesion: 0.25
Nodes (8): Requirement: SUCCESS screen on win, Requirement: 3-minute limit -> GAME OVER + restart, Requirement: WASD movement (forward/back/left/right), draw_grid(), main(), Faint table-like grid lines so cells are easy to see., Full-screen banner. wait_key=True blocks for a key, else shows ~2.5 s., show_screen()

### Community 2 - "Game Spec & Terminal Style"
Cohesion: 0.40
Nodes (5): AI gen.txt Game Spec (Thai), Requirement: interface like terminal snake game, draw_hud(), Mouse Maze Game Module, Claude Code Local Permission Allowlist

### Community 3 - "Maze Generation & Rendering"
Cohesion: 0.50
Nodes (4): Requirement: 30x30 maze, 16 per cell, one entry + one exit, draw_maze(), generate_maze(), Recursive-backtracker maze. walls[y][x] is the set of closed walls.

### Community 4 - "Entry/Exit Selection"
Cohesion: 0.67
Nodes (3): border_cells(), choose_endpoints(), Try >=5 random border (entry, exit) pairs, BFS each, keep the pair     with the

### Community 5 - "Mouse Player Sprite"
Cohesion: 0.67
Nodes (3): Requirement: mouse player sprite <=16x16, moves 1 cell per press, draw_mouse(), Mouse sprite drawn inside one 16x16 cell.

### Community 7 - "Round Setup & Border Doors"
Cohesion: 0.67
Nodes (3): new_game(), open_border_wall(), Open the outer wall at an entrance/exit cell so it reads as a door.

## Ambiguous Edges - Review These
- `draw_guide()` → `Requirement: cheese at finish, shortest path shown as scent light`  [AMBIGUOUS]
  mouse_maze.py · relation: implements

## Knowledge Gaps
- **3 isolated node(s):** `allow`, `AI gen.txt Game Spec (Thai)`, `Claude Code Local Permission Allowlist`
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `draw_guide()` and `Requirement: cheese at finish, shortest path shown as scent light`?**
  _Edge tagged AMBIGUOUS (relation: implements) - confidence is low._
- **Why does `main()` connect `Game Loop & Screens` to `Cheese Guide & Pathfinding`, `Game Spec & Terminal Style`, `Maze Generation & Rendering`, `Entry/Exit Selection`, `Mouse Player Sprite`, `Round Setup & Border Doors`?**
  _High betweenness centrality (0.204) - this node is a cross-community bridge._
- **Why does `draw_hud()` connect `Game Spec & Terminal Style` to `Game Loop & Screens`, `Entry/Exit Selection`?**
  _High betweenness centrality (0.180) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `main()` (e.g. with `Requirement: 3-minute limit -> GAME OVER + restart` and `Requirement: WASD movement (forward/back/left/right)`) actually correct?**
  _`main()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `bfs_path()` (e.g. with `Requirement: cheese at finish, shortest path shown as scent light` and `Requirement: entry/exit mutually reachable, >=5 computations`) actually correct?**
  _`bfs_path()` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `generate_maze()` (e.g. with `Requirement: 30x30 maze, 16 per cell, one entry + one exit` and `bfs_path()`) actually correct?**
  _`generate_maze()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `allow`, `Recursive-backtracker maze. walls[y][x] is the set of closed walls.`, `Shortest path (list of cells) from start to goal, or None.` to the rest of the system?**
  _15 weakly-connected nodes found - possible documentation gaps or missing edges._