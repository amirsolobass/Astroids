### Quick context

- This repository is a small Pygame-based Asteroids clone. The runtime entrypoint is `main.py` in the repository root (`Astroids/main.py`). The project uses `pygame==2.6.1` (see `pyproject.toml`) and targets Python >= 3.14.

### High-level architecture

- `main.py`: orchestrates the game loop and three high-level game states (MENU, PLAYING, GAME_OVER). It creates and wires the core sprite groups used by the engine.
- Sprite classes: game objects subclass `CircleShape` (`circleshape.py`) which itself subclasses `pygame.sprite.Sprite`. Core object modules: `player.py`, `asteroid.py`, `shot.py`, `powerup.py`, `asteroidfield.py`.
- Groups: the code uses explicit `updatable`, `drawable`, and per-type groups (e.g., `asteroids`, `shots`). Classes are added to groups by assigning a class attribute `containers = (group1, group2, ...)` before instantiation — see `main.py` where `Asteroid.containers = (asteroids, updatable, drawable)`.
- Persistence/logging: `score_manager.py` reads/writes `highscore.txt`. `logger.py` writes `game_state.jsonl` and `game_events.jsonl` for debugging snapshots/events.

### Key project-specific patterns (very important)

- Container pattern: set `Class.containers = (group_a, group_b, ...)` on the class (in `main.py`) and then instantiate the class. `CircleShape.__init__` calls `super().__init__(self.containers)` so the new sprite is automatically added to those groups. Example from `main.py`:

  - `Asteroid.containers = (asteroids, updatable, drawable)`
  - `player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)`

- Update & draw loop: the main loop calls `obj.update(dt)` for every object in `updatable` and `obj.draw(screen)` for every object in `drawable`. Implement both `update(self, dt)` and `draw(self, screen)` on new sprite types.

- Collision handling: objects use `collides_with(other)` from `CircleShape` (distance check). On collision call `.kill()` to remove sprites from groups (e.g., `shot.kill()` or `asteroid.kill()`). Splitting logic for asteroids is in `asteroid.split()`.

- Timers & spawn logic: `AsteroidField` is a `pygame.sprite.Sprite` that uses `update(dt)` and internal timers (`spawn_timer`) to spawn asteroids at screen edges.

### Running the project (developer workflow)

- Quick run (from the repo root `Astroids/`):

  ```bash
  cd /path/to/Astroids
  python3 main.py
  ```

- Recommended virtualenv and dependency install (pygame pinned in `pyproject.toml`):

  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  python3 -m pip install pygame==2.6.1
  python3 main.py
  ```

- There are no automated tests in the repo. Use the interactive run to validate gameplay and log files.

### File & behavior callouts (good places to start edits)

- `main.py`: game state machine and wiring of groups; update here if you need to add a global group or change game state flow.
- `circleshape.py`: base class to subclass for new game objects — implement `update`/`draw` and rely on `collides_with`.
- `asteroidfield.py`: example of a spawner sprite; copy this pattern to add other periodic spawners (powerups, enemies).
- `score_manager.py`: reads/writes `highscore.txt` in repository root — be careful when running tests because it mutates that file.
- `logger.py`: creates `game_state.jsonl` and `game_events.jsonl` snapshots. These are useful for debugging — they are created in the working directory when logging is invoked.

### Guidelines for an AI agent making changes here

- Preserve the `containers` wiring pattern: add new sprite classes by subclassing `CircleShape` and ensure the calling code assigns `YourClass.containers = (updatable, drawable[, other_group])` prior to instantiation.
- Implement `update(self, dt)` and `draw(self, screen)` — the main loop depends on those method signatures and a float `dt` timestep.
- Use `.kill()` to remove sprites from groups and avoid directly mutating group internals.
- When adding new persistent files, update `logger.py` or `score_manager.py` usage and ensure safe reads/writes (these modules read/write plain text/JSONL in the repo root).
- Keep gameplay-affecting constants in `constants.py`. New features should add new constants there rather than hardcoding numbers in modules.

### Useful examples (copy/paste-ready)

- Add a simple powerup class:

  ```py
  # file: powerup.py (exists)
  class Powerup(CircleShape):
      def __init__(self, x, y):
          super().__init__(x, y, POWERUP_RADIUS)

      def draw(self, screen):
          pygame.draw.circle(screen, "green", self.position, self.radius)

      def update(self, dt):
          # rotate visual representation, or implement lifespan
          pass
  ```

  In `main.py` register it: `Powerup.containers = (updatable, drawable)` then instantiate.

### What I did not assume

- There are no unit tests or CI config to run. Do not add or rely on hidden test runners.
- The project expects interactive runs; file-based logs and `highscore.txt` are real side effects — avoid destructive edits to them without explicit user consent.

If any sections here are unclear or you want more granular conventions (naming, branching, commit messages, or example PR templates), tell me which area to expand and I will iterate. 
