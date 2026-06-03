import json
import os

PROGRESS_FILE = "progress.json"

UNLOCK_THRESHOLDS = {
    "boost": 50,
    "screen_shake": 100,
    "shields": 200,
    "powerup_rapid_fire": 400,
    "particles": 700,
    "shop": 1000,
    "powerup_life": 1200,
    "powerup_laser": 1800,
    "powerup_double_shot": 2500,
    "powerup_homing": 3500,
    "settings": 5000,
    "art_tier2": 7500,
    "music": 10000,
    "secret": 20000,
}

UNLOCK_NAMES = {
    "boost": "Boost Sprint",
    "screen_shake": "Screen Shake",
    "shields": "Shield System",
    "powerup_rapid_fire": "Rapid Fire",
    "particles": "Particle Effects",
    "shop": "Shop",
    "powerup_life": "Extra Life Powerup",
    "powerup_laser": "Laser Powerup",
    "powerup_double_shot": "Double Shot",
    "powerup_homing": "Homing Missiles",
    "settings": "Settings",
    "art_tier2": "Enhanced Visuals",
    "music": "Background Music",
    "secret": "SECRET MODE",
}

TOGGLEABLE_FEATURES = [
    "boost", "screen_shake", "shields", "particles",
    "powerup_rapid_fire", "powerup_life", "powerup_laser",
    "powerup_double_shot", "powerup_homing", "secret",
]

STUB_FEATURES = {"art_tier2", "music"}

TOKEN_RATE = 50

UPGRADE_DEFS = {
    "bullet_speed": {
        "name": "Bullet Speed",
        "max_tier": 3,
        "costs": [2, 6, 12],
        "desc": ["Base", "+15% speed", "+30% speed", "+50% speed"],
    },
    "fire_rate": {
        "name": "Fire Rate",
        "max_tier": 3,
        "costs": [3, 8, 18],
        "desc": ["Base", "-15% cooldown", "-30% cooldown", "-45% cooldown"],
    },
    "max_lives": {
        "name": "Max Lives",
        "max_tier": 2,
        "costs": [5, 15],
        "desc": ["5 max", "6 max", "7 max"],
    },
    "max_shields": {
        "name": "Max Shields",
        "max_tier": 2,
        "costs": [4, 12],
        "desc": ["3 max", "4 max", "5 max"],
    },
    "move_speed": {
        "name": "Move Speed",
        "max_tier": 2,
        "costs": [3, 10],
        "desc": ["Base", "+15% speed", "+30% speed"],
    },
    "score_multiplier": {
        "name": "Score Multiplier",
        "max_tier": 3,
        "costs": [5, 12, 25],
        "desc": ["x1.0", "x1.1", "x1.25", "x1.5"],
    },
}

RUN_GEAR_DEFS = {
    "starting_shield": {
        "name": "Starting Shield",
        "cost": 2,
        "desc": "Start with 1 shield",
        "max_qty": 1,
    },
    "starting_rapid_fire": {
        "name": "Starting Rapid Fire",
        "cost": 4,
        "desc": "Start with 30s rapid fire",
        "max_qty": 1,
    },
    "starting_life": {
        "name": "Bonus Starting Life",
        "cost": 3,
        "desc": "Start with +1 life",
        "max_qty": 2,
    },
}

_lifetime_score: int = 0
_unlocked: set = set()
_active: set = set()
_tokens: int = 0
_upgrades: dict = {}
_run_gear: dict = {}


def load_progress() -> None:
    global _lifetime_score, _unlocked, _active, _tokens, _upgrades, _run_gear
    try:
        with open(PROGRESS_FILE) as f:
            data = json.load(f)
            _lifetime_score = int(data.get("lifetime_score", 0))
            _unlocked = set(data.get("unlocked_features", []))
            _tokens = int(data.get("tokens", 0))
            _upgrades = dict(data.get("upgrades", {}))
            _run_gear = dict(data.get("run_gear", {}))
            if "active_features" in data:
                _active = set(data["active_features"])
            else:
                _active = set(_unlocked)
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        _lifetime_score = 0
        _unlocked = set()
        _active = set()
        _tokens = 0
        _upgrades = {}
        _run_gear = {}
        if os.path.exists("highscore.txt"):
            try:
                with open("highscore.txt") as f:
                    _lifetime_score = int(f.read().strip())
            except (ValueError, OSError):
                pass
    _apply_thresholds()


def _apply_thresholds() -> None:
    for feature, threshold in UNLOCK_THRESHOLDS.items():
        if _lifetime_score >= threshold and feature not in _unlocked:
            _unlocked.add(feature)
            if feature not in STUB_FEATURES:
                _active.add(feature)
        elif _lifetime_score >= threshold:
            _unlocked.add(feature)


def save_progress() -> None:
    with open(PROGRESS_FILE, "w") as f:
        json.dump({
            "lifetime_score": _lifetime_score,
            "unlocked_features": list(_unlocked),
            "active_features": list(_active),
            "tokens": _tokens,
            "upgrades": _upgrades,
            "run_gear": _run_gear,
        }, f)


def add_session_score(session_score: int) -> set:
    global _lifetime_score, _tokens
    _tokens += session_score // TOKEN_RATE
    _lifetime_score += session_score
    newly_unlocked: set = set()
    for feature, threshold in UNLOCK_THRESHOLDS.items():
        if _lifetime_score >= threshold and feature not in _unlocked:
            _unlocked.add(feature)
            if feature not in STUB_FEATURES:
                _active.add(feature)
            newly_unlocked.add(feature)
    return newly_unlocked


def is_unlocked(feature: str) -> bool:
    return feature in _unlocked


def is_enabled(feature: str) -> bool:
    return feature in _active


def enable_feature(feature: str) -> None:
    if feature in _unlocked and feature not in STUB_FEATURES:
        _active.add(feature)
        save_progress()


def disable_feature(feature: str) -> None:
    _active.discard(feature)
    save_progress()


def toggle_feature(feature: str) -> None:
    if is_enabled(feature):
        disable_feature(feature)
    else:
        enable_feature(feature)


def get_toggleable_features() -> list:
    return [f for f in TOGGLEABLE_FEATURES if f in _unlocked]


def get_lifetime_score() -> int:
    return _lifetime_score


def get_tokens() -> int:
    return _tokens


def next_unlock() -> tuple:
    for feature, threshold in UNLOCK_THRESHOLDS.items():
        if feature not in _unlocked:
            return feature, threshold
    return None, None


# --- Shop: permanent upgrades ---

def get_upgrade(key: str) -> int:
    return _upgrades.get(key, 0)


def buy_upgrade(key: str) -> bool:
    global _tokens
    defn = UPGRADE_DEFS.get(key)
    if defn is None:
        return False
    tier = _upgrades.get(key, 0)
    if tier >= defn["max_tier"]:
        return False
    cost = defn["costs"][tier]
    if _tokens < cost:
        return False
    _tokens -= cost
    _upgrades[key] = tier + 1
    save_progress()
    return True


def get_upgrade_next_cost(key: str) -> int | None:
    defn = UPGRADE_DEFS.get(key)
    if defn is None:
        return None
    tier = _upgrades.get(key, 0)
    if tier >= defn["max_tier"]:
        return None
    return defn["costs"][tier]


def refund_upgrade(key: str) -> bool:
    global _tokens
    defn = UPGRADE_DEFS.get(key)
    if defn is None:
        return False
    tier = _upgrades.get(key, 0)
    if tier <= 0:
        return False
    _tokens += defn["costs"][tier - 1]
    _upgrades[key] = tier - 1
    save_progress()
    return True


def get_upgrade_refund_value(key: str) -> int | None:
    defn = UPGRADE_DEFS.get(key)
    if defn is None:
        return None
    tier = _upgrades.get(key, 0)
    if tier <= 0:
        return None
    return defn["costs"][tier - 1]


# --- Shop: run gear ---

def get_run_gear() -> dict:
    return dict(_run_gear)


def buy_run_gear(key: str) -> bool:
    global _tokens
    defn = RUN_GEAR_DEFS.get(key)
    if defn is None:
        return False
    current_qty = _run_gear.get(key, 0)
    if current_qty >= defn["max_qty"]:
        return False
    if _tokens < defn["cost"]:
        return False
    _tokens -= defn["cost"]
    _run_gear[key] = current_qty + 1
    save_progress()
    return True


def consume_run_gear() -> dict:
    global _run_gear
    gear = dict(_run_gear)
    _run_gear = {}
    save_progress()
    return gear


# --- Upgrade stat multipliers ---

def get_score_multiplier() -> float:
    return [1.0, 1.1, 1.25, 1.5][get_upgrade("score_multiplier")]


def get_bullet_speed_multiplier() -> float:
    return [1.0, 1.15, 1.3, 1.5][get_upgrade("bullet_speed")]


def get_fire_rate_multiplier() -> float:
    return [1.0, 0.85, 0.70, 0.55][get_upgrade("fire_rate")]


def get_move_speed_multiplier() -> float:
    return [1.0, 1.15, 1.3][get_upgrade("move_speed")]


def get_max_lives_bonus() -> int:
    return get_upgrade("max_lives")


def get_max_shields_bonus() -> int:
    return get_upgrade("max_shields")


# --- Debug helpers ---

def set_lifetime_score(score: int) -> None:
    global _lifetime_score, _unlocked, _active
    _lifetime_score = max(0, score)
    _unlocked = set()
    _active = set()
    _apply_thresholds()
    save_progress()


def adjust_lifetime_score(delta: int) -> None:
    set_lifetime_score(_lifetime_score + delta)


def adjust_tokens(delta: int) -> None:
    global _tokens
    _tokens = max(0, _tokens + delta)
    save_progress()


def reset_tokens() -> None:
    global _tokens
    _tokens = 0
    save_progress()
