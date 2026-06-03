import pygame
from shot import Shot
from laser import Laser
from circleshape import CircleShape
from constants import *
import progress

SHIELD_COLOR = (100, 149, 237)


class Player(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.cd_timer = 0.0
        self.shoot_cooldown = PLAYER_SHOOT_COOLDOWN_SECONDS * progress.get_fire_rate_multiplier()
        self._original_shoot_cooldown = self.shoot_cooldown
        self.powerup_time_remaining = 0.0
        self.shields = 0
        self.lives = PLAYER_STARTING_LIVES
        self.invincibility_timer = 0.0
        self.laser_mode = False
        self.laser_time_remaining = 0.0
        self.laser_level = 0
        self.double_shot = False
        self.double_shot_time_remaining = 0.0
        self.double_shot_level = 0
        self.homing_mode = False
        self.homing_time_remaining = 0.0
        self.homing_level = 0

    def triangle(self):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]

    def draw(self, screen):
        if self.invincibility_timer <= 0 or int(self.invincibility_timer * 8) % 2 == 0:
            pygame.draw.polygon(screen, "white", self.triangle(), LINE_WIDTH)
        for i in range(self.shields):
            pygame.draw.circle(screen, SHIELD_COLOR, self.position, self.radius + 8 + i * 8, 2)

    def rotate(self, dt):
        self.rotation += (PLAYER_TURN_SPEED * dt)

    def update(self, dt):
        if self.invincibility_timer > 0:
            self.invincibility_timer -= dt
        if self.laser_time_remaining > 0:
            self.laser_time_remaining -= dt
            if self.laser_time_remaining <= 0:
                self.laser_mode = False
                self.laser_level = 0
        if self.double_shot_time_remaining > 0:
            self.double_shot_time_remaining -= dt
            if self.double_shot_time_remaining <= 0:
                self.double_shot = False
                self.double_shot_level = 0
        if self.homing_time_remaining > 0:
            self.homing_time_remaining -= dt
            if self.homing_time_remaining <= 0:
                self.homing_mode = False
                self.homing_level = 0
        if getattr(self, "powerup_time_remaining", 0) > 0:
            self.powerup_time_remaining -= dt
            if self.powerup_time_remaining <= 0:
                self.shoot_cooldown = getattr(self, "_original_shoot_cooldown", self.shoot_cooldown)
                self.powerup_time_remaining = 0
        keys = pygame.key.get_pressed()
        self.cd_timer -= dt
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.rotate(-dt)
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.rotate(dt)
        boosted = (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and progress.is_enabled("boost")
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.move(dt, boosted)
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.move(-dt, boosted)
        if keys[pygame.K_SPACE]:
            if self.cd_timer <= 0:
                if self.laser_mode and self.laser_level > 1:
                    self.cd_timer = self.shoot_cooldown / self.laser_level
                else:
                    self.cd_timer = self.shoot_cooldown
                self.shoot()
        self.position.x %= SCREEN_WIDTH
        self.position.y %= SCREEN_HEIGHT

    def move(self, dt, boosted=False):
        unit_vector = pygame.Vector2(0, 1)
        rotated_vector = unit_vector.rotate(self.rotation)
        speed = PLAYER_SPEED * progress.get_move_speed_multiplier() * (PLAYER_BOOST_MULTIPLIER if boosted else 1.0)
        self.position += rotated_vector * speed * dt

    def shoot(self):
        bullet_speed = PLAYER_SHOOT_SPEED * progress.get_bullet_speed_multiplier()
        direction = pygame.Vector2(0, 1).rotate(self.rotation)

        _double_cone = {
            2: [-15, 15],
            3: [-15, 0, 15],
            4: [-20, -7, 7, 20],
            5: [-20, -10, 0, 10, 20],
        }
        _homing_spread = {
            2: [-10, 10],
            3: [-15, 0, 15],
            4: [-20, -7, 7, 20],
            5: [-20, -10, 0, 10, 20],
            6: [-25, -15, -5, 5, 15, 25],
        }

        shot_fired = False

        if self.laser_mode:
            shot_fired = True
            if self.double_shot and self.double_shot_level >= 2:
                for angle in _double_cone.get(self.double_shot_level, [0]):
                    Laser(self.position.x, self.position.y, self.rotation + angle)
            elif self.double_shot:
                for angle in (-8, 8):
                    Laser(self.position.x, self.position.y, self.rotation + angle)
            else:
                Laser(self.position.x, self.position.y, self.rotation)

        if self.homing_mode:
            shot_fired = True
            from shot import HomingShot
            count = self.homing_level + 1
            for angle in _homing_spread.get(count, [0]):
                HomingShot(self.position.x, self.position.y, self.rotation + angle, self.homing_level)

        if not shot_fired:
            if self.double_shot:
                if self.double_shot_level <= 1:
                    perp = pygame.Vector2(0, 1).rotate(self.rotation + 90)
                    for side in (-1, 1):
                        offset = perp * DOUBLE_SHOT_OFFSET * side
                        s = Shot(self.position.x + offset.x, self.position.y + offset.y)
                        s.velocity = direction * bullet_speed
                else:
                    cone_angles = {
                        2: [0, -15, 15],
                        3: [0, -15, 15, -30, 30],
                        4: [0, -20, 20, -40, 40],
                        5: [0, -15, 15, -30, 30, -45, 45],
                    }
                    for angle_offset in cone_angles.get(self.double_shot_level, [0]):
                        shot_dir = pygame.Vector2(0, 1).rotate(self.rotation + angle_offset)
                        s = Shot(self.position.x, self.position.y)
                        s.velocity = shot_dir * bullet_speed
            else:
                shot = Shot(self.position.x, self.position.y)
                shot.velocity = direction * bullet_speed
