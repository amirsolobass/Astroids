import pygame
from circleshape import CircleShape
from constants import SHOT_RADIUS, PLAYER_SHOOT_SPEED, SCREEN_WIDTH, SCREEN_HEIGHT, HOMING_LIFESPAN
import progress


class Shot(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, SHOT_RADIUS)

    def draw(self, screen):
        pygame.draw.circle(screen, "red", self.position, self.radius)

    def update(self, dt):
        self.position += self.velocity * dt


class HomingShot(CircleShape):
    containers: tuple = ()

    def __init__(self, x, y, rotation, level=1):
        super().__init__(x, y, SHOT_RADIUS)
        self.velocity = pygame.Vector2(0, 1).rotate(rotation) * PLAYER_SHOOT_SPEED * progress.get_bullet_speed_multiplier()
        self.life = HOMING_LIFESPAN
        self.level = level

    def draw(self, screen):
        pygame.draw.circle(screen, (200, 100, 255), self.position, self.radius)

    def update(self, dt):
        self.life -= dt
        if (
            self.life <= 0
            or self.position.x < -50
            or self.position.x > SCREEN_WIDTH + 50
            or self.position.y < -50
            or self.position.y > SCREEN_HEIGHT + 50
        ):
            self.kill()
            return
        self.position += self.velocity * dt
