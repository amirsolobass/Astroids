import pygame

LASER_FLASH_DURATION = 0.08
LASER_COLOR = (255, 80, 80)

class Laser(pygame.sprite.Sprite):
    containers: tuple = ()

    def __init__(self, x, y, rotation):
        super().__init__(self.containers)
        self.position = pygame.Vector2(x, y)
        self.direction = pygame.Vector2(0, 1).rotate(rotation).normalize()
        self.age = 0.0

    def hits(self, asteroid):
        to_center = asteroid.position - self.position
        proj = to_center.dot(self.direction)
        if proj < 0:
            return False
        closest = self.position + self.direction * proj
        return (asteroid.position - closest).length() <= asteroid.radius

    def draw(self, screen):
        screen_diag = pygame.Vector2(screen.get_width(), screen.get_height()).length()
        end = self.position + self.direction * screen_diag
        pygame.draw.line(screen, LASER_COLOR, self.position, end, 3)

    def update(self, dt):
        self.age += dt
        if self.age > LASER_FLASH_DURATION:
            self.kill()
