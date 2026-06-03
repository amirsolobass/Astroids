import pygame
import random
from constants import *
from circleshape import CircleShape
import progress

POWERUP_TYPES = ["rapid_fire", "life", "laser", "double_shot", "homing"]

POWERUP_COLORS = {
    "rapid_fire": (255, 215, 0),
    "life": (255, 0, 0),
    "laser": (255, 165, 0),
    "double_shot": (100, 200, 255),
    "homing": (200, 100, 255),
}


class PowerUp(CircleShape):
    def __init__(self, x, y, kind=None):
        super().__init__(x, y, POWERUP_RADIUS)
        self.position = pygame.Vector2(x, y)
        self.age = 0.0
        if kind is not None:
            self.kind = kind
        else:
            available = [t for t in POWERUP_TYPES if progress.is_enabled(f"powerup_{t}")]
            self.kind = random.choice(available) if available else None

    def draw(self, screen):
        if self.kind is None:
            return
        color = POWERUP_COLORS.get(self.kind, "green")
        pygame.draw.circle(screen, color, self.position, self.radius, 2)
        pygame.draw.circle(screen, color, self.position, self.radius // 2)

    def update(self, dt):
        if self.kind is None:
            self.kill()
            return
        self.age += dt
        if self.age > POWERUP_LIFESPAN_SECONDS:
            self.kill()

    def apply_effect(self, player):
        if self.kind == "rapid_fire":
            if player.powerup_time_remaining > 0:
                player.powerup_time_remaining += POWERUP_EFFECT_DURATION_SECONDS * 0.7
            else:
                player._original_shoot_cooldown = PLAYER_SHOOT_COOLDOWN_SECONDS * progress.get_fire_rate_multiplier()
                player.shoot_cooldown = player._original_shoot_cooldown / POWERUP_RAPID_FIRE_MULTIPLIER
                player.powerup_time_remaining = POWERUP_EFFECT_DURATION_SECONDS

        elif self.kind == "life":
            player.lives = min(player.lives + 1, PLAYER_MAX_LIVES + progress.get_max_lives_bonus())

        elif self.kind == "laser":
            if player.laser_mode:
                player.laser_level = min(player.laser_level + 1, 5)
            else:
                player.laser_mode = True
                player.laser_level = 1
            player.laser_time_remaining = POWERUP_EFFECT_DURATION_SECONDS

        elif self.kind == "double_shot":
            if player.double_shot:
                player.double_shot_level = min(player.double_shot_level + 1, 5)
            else:
                player.double_shot = True
                player.double_shot_level = 1
            player.double_shot_time_remaining = POWERUP_EFFECT_DURATION_SECONDS

        elif self.kind == "homing":
            if player.homing_mode:
                player.homing_level = min(player.homing_level + 1, 5)
            else:
                player.homing_mode = True
                player.homing_level = 1
            player.homing_time_remaining = POWERUP_EFFECT_DURATION_SECONDS
