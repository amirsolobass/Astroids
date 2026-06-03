# Astroids

A fully playable Asteroids clone built with Pygame. My first game.

## Features

- Rotation-based thrust with momentum
- Asteroids split into smaller fragments on impact
- Continuous procedural spawning that escalates over time
- Shooting with cooldown
- Shield mechanic with limited duration
- Power-ups with varied effects
- High score system persisted to disk
- Full menu, game loop, and end screen
- Game events and state snapshots logged to JSONL

## Run

```bash
uv run python main.py
```

## Version History

- **v0.5b** — Powerup improvements
  - Homing missiles now fire multiple shots per trigger based on level (Lv.1 = 2 shots, up to Lv.5 = 6 shots in a spread)
  - Rapid fire now stacks on re-pickup: collecting while active extends duration by 70% instead of resetting
  - All powerups now work simultaneously — laser, homing, and double shot fire independently on the same trigger; laser + double shot fires a cone of laser beams
  - Fixed: permanent upgrades are now refundable in the shop (Backspace to refund one tier, tokens returned)
  - Fixed: homing missiles were turning too slowly; turn rate increased 4×
  - Fixed: multiple unlocks at once no longer overflow the screen — text wraps to a new line
- **v0.5a** — Powerup system expansion
  - Powerup level system: collect the same powerup while it's active to level it up (max Lv.5)
  - Laser levels: each level multiplies fire rate (Lv.5 = 5× faster)
  - Double Shot levels: Lv.2+ expands into a cone spread (up to 7 shots at Lv.5)
  - Homing levels: Lv.2–5 add an explosion on impact with increasing radius (30–100px), chaining splits to nearby asteroids
  - In-game powerup HUD: shows active powerup name, level, and time remaining
  - Powerup collection notification now shows the specific powerup name (and level if upgraded)
  - In-game token counter: HUD shows projected tokens earned this session
  - Fixed: Double Shot and Homing powerups were missing from the spawn list and never appeared
  - Increased powerup on-screen duration (5s → 15s), spawn frequency (10s → 6s), and effect duration (8s → 12s)
- **v0.4b** — Bug fixes
  - Fixed player not wrapping around screen edges
- **v0.4a** — Full roguelite progression expansion
  - Persistent upgrade shop: 6 permanent upgrades (bullet speed, fire rate, move speed, max lives, max shields, score multiplier) purchased with tokens across sessions
  - Per-run gear: buy starting shields, starting rapid fire, or bonus lives before each run
  - Settings screen: toggle each unlocked feature on/off independently for challenge runs
  - 14-tier unlock tree gated by lifetime score (boost → screen shake → shields → powerups → shop → settings → secret mode)
  - New powerup types: double shot (twin parallel bullets) and homing missiles (seek nearest asteroid)
  - Visual effects: screen shake on asteroid destruction, particle bursts on split (both toggleable)
  - Secret mode: asteroids cycle neon rainbow colors at lifetime score 20,000
  - Stubs for future asset tiers: art_tier2 and music (shown as "Coming Soon" in settings)
  - Score multiplier upgrade applies to all asteroid kills
  - Boost sprint (Shift key) gated behind first unlock tier
  - All gameplay features respect `is_enabled()` so settings toggles take effect immediately
- **v0.3a** — Power-up infrastructure, shield mechanic
- **v0.2a** — Menu screen, end screen, high score system
- **v0.1a** — Core loop: player movement, collision detection, asteroid splitting
