import pygame
from circleshape import CircleShape
from constants import SHIELD_AMOUNT, PLAYER_SHIELD_CAPACITY, SHIELD_LIFESPAN_SECONDS
import progress


class Shield(CircleShape):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)
        self.position = pygame.Vector2(x, y)
        self.age = 0.0

    def draw(self, screen):
        pygame.draw.circle(screen, "blue", self.position, self.radius, 2)

    def update(self, dt):
        self.age += dt
        if self.age > SHIELD_LIFESPAN_SECONDS:
            self.kill()

    def apply_effect(self, player):
        player.shields = min(player.shields + SHIELD_AMOUNT, PLAYER_SHIELD_CAPACITY + progress.get_max_shields_bonus())