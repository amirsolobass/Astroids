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
