import pygame
import random
from constants import * 
from circleshape import CircleShape
from constants import POWERUP_RADIUS

class PowerUp(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, POWERUP_RADIUS)
        self.position = pygame.Vector2(x, y)
        self.age = 0.0
        self.rotation = 0.0


    def draw(self, screen):
        pos = (int(self.position.x), int(self.position.y))
        pygame.draw.circle(screen, "green", self.position, self.radius)


    def update(self, dt):
        self.rotation += 90 * dt
        self.age += dt
        if self.age > POWERUP_LIFESPAN_SECONDS:
            self.kill()
        
    def apply_effect(self, player):
        if hasattr(player, "shoot_cooldown"):
            # preserve original cooldown
            if not hasattr(player, "_original_shoot_cooldown"):
                player._original_shoot_cooldown = player.shoot_cooldown
            # apply powerup effect
            player.shoot_cooldown *= POWERUP_COOLDOWN_MULTIPLIER
            player.powerup_time_remaining = getattr(player, "powerup_time_remaining", 0) + POWERUP_EFFECT_DURATION_SECONDS
        else:
            font = pygame.font.SysFont("arial", 36)
            text = font.render("Powerup has no effect!", True, "red")
            screen = pygame.display.get_surface()
            # place the text above the powerup
            screen.blit(text, (self.position.x - text.get_width() // 2, self.position.y - self.radius - 30))
            
        
