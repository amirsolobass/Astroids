import pygame
import sys
import random
from score_manager import load_high_score, save_high_score
from logger import log_state, log_event
from constants import (
    POWERUP_MIN_RADIUS, SCREEN_WIDTH, SCREEN_HEIGHT,
    MENU, PLAYING, GAME_OVER, SETTINGS, SHOP,
    PLAYER_SHIELD_CAPACITY, PLAYER_INVINCIBILITY_SECONDS, PLAYER_STARTING_LIVES,
    PLAYER_MAX_LIVES, POWERUP_RAPID_FIRE_MULTIPLIER,
    PLAYER_SHOOT_COOLDOWN_SECONDS,
    SHAKE_DURATION, SHAKE_INTENSITY,
    PARTICLE_COUNT, PARTICLE_SPEED_MIN, PARTICLE_SPEED_MAX, PARTICLE_LIFESPAN,
    HOMING_TURN_RATE,
)
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot, HomingShot
from powerup import PowerUp
from shield import Shield
from laser import Laser
import progress
import settings_screen
import shop_screen


def spawn_particles(particles, pos, color):
    for _ in range(PARTICLE_COUNT):
        angle = random.uniform(0, 360)
        speed = random.uniform(PARTICLE_SPEED_MIN, PARTICLE_SPEED_MAX)
        vel = pygame.Vector2(0, 1).rotate(angle) * speed
        particles.append({
            "pos": pygame.Vector2(pos),
            "vel": vel,
            "life": PARTICLE_LIFESPAN,
            "max_life": PARTICLE_LIFESPAN,
            "color": color,
        })


def reset_player(player):
    player.position = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    player.velocity = pygame.Vector2(0, 0)
    player.rotation = 0
    player.shields = 0
    player.lives = PLAYER_STARTING_LIVES
    player.invincibility_timer = 0.0
    player.laser_mode = False
    player.laser_time_remaining = 0.0
    player.double_shot = False
    player.double_shot_time_remaining = 0.0
    player.homing_mode = False
    player.homing_time_remaining = 0.0
    player.powerup_time_remaining = 0.0
    player.shoot_cooldown = PLAYER_SHOOT_COOLDOWN_SECONDS * progress.get_fire_rate_multiplier()
    player._original_shoot_cooldown = player.shoot_cooldown


def apply_run_gear(player, gear):
    max_shields = PLAYER_SHIELD_CAPACITY + progress.get_max_shields_bonus()
    max_lives = PLAYER_MAX_LIVES + progress.get_max_lives_bonus()
    if gear.get("starting_shield", 0):
        player.shields = min(player.shields + 1, max_shields)
    if gear.get("starting_life", 0):
        player.lives = min(player.lives + gear["starting_life"], max_lives)
    if gear.get("starting_rapid_fire", 0):
        base_cooldown = PLAYER_SHOOT_COOLDOWN_SECONDS * progress.get_fire_rate_multiplier()
        player._original_shoot_cooldown = base_cooldown
        player.shoot_cooldown = base_cooldown / POWERUP_RAPID_FIRE_MULTIPLIER
        player.powerup_time_remaining = 30.0


def main():
    print(f"Starting Asteroids with pygame version: {pygame.version.ver}")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")

    progress.load_progress()

    current_state = MENU
    score = 0
    high_score = 0
    notification_text = ""
    notification_timer = 0.0
    session_processed = False
    newly_unlocked: set = set()
    debug_mode = False

    settings_items: list = []
    settings_selected = 0
    settings_return_state = MENU
    shop_tab = 0
    shop_selected = 0

    particles: list = []
    shake_timer = 0.0

    _DEBUG_TIERS = list(progress.UNLOCK_THRESHOLDS.values())
    _DEBUG_TIER_KEYS = [
        pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
        pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9,
    ]

    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    dt = 0.0

    font = pygame.font.SysFont("arial", 36)
    small_font = pygame.font.SysFont("arial", 24)

    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    shields = pygame.sprite.Group()
    lasers = pygame.sprite.Group()
    homing_shots = pygame.sprite.Group()

    high_score = load_high_score()
    Asteroid.containers = (asteroids, updatable, drawable)
    Player.containers = (updatable, drawable)
    AsteroidField.containers = updatable
    Shot.containers = (shots, updatable, drawable)
    HomingShot.containers = (homing_shots, shots, updatable, drawable)
    PowerUp.containers = (powerups, updatable, drawable)
    Shield.containers = (shields, updatable, drawable)
    Laser.containers = (lasers, updatable, drawable)

    asteroid_field = AsteroidField()
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            # Debug key handling on MENU and GAME_OVER
            if event.type == pygame.KEYDOWN and current_state in (MENU, GAME_OVER):
                if event.key == pygame.K_d:
                    debug_mode = not debug_mode
                elif debug_mode:
                    if event.key == pygame.K_LEFT:
                        progress.adjust_lifetime_score(-100)
                    elif event.key == pygame.K_RIGHT:
                        progress.adjust_lifetime_score(100)
                    elif event.key == pygame.K_UP:
                        progress.adjust_tokens(10)
                    elif event.key == pygame.K_DOWN:
                        progress.adjust_tokens(-10)
                    elif event.key == pygame.K_0:
                        progress.reset_tokens()
                    else:
                        for i, tier_key in enumerate(_DEBUG_TIER_KEYS):
                            if event.key == tier_key and i < len(_DEBUG_TIERS):
                                progress.set_lifetime_score(_DEBUG_TIERS[i])

            # Settings screen events
            if current_state == SETTINGS:
                action, settings_selected = settings_screen.handle_settings_event(
                    event, settings_items, settings_selected
                )
                if action == "back":
                    current_state = settings_return_state

            # Shop screen events
            if current_state == SHOP:
                action, shop_tab, shop_selected = shop_screen.handle_shop_event(
                    event, shop_tab, shop_selected
                )
                if action == "back":
                    current_state = GAME_OVER

        # ── MENU ──────────────────────────────────────────────────
        if current_state == MENU:
            screen.fill("black")
            title_text = font.render("Astroids - Press R to Start", True, "white")
            tutorial_text = font.render("Move with the arrow keys, shoot with SPACE", True, "red")
            screen.blit(
                title_text,
                ((SCREEN_WIDTH - title_text.get_width()) / 2, (SCREEN_HEIGHT - title_text.get_height()) / 2),
            )
            screen.blit(
                tutorial_text,
                ((SCREEN_WIDTH - tutorial_text.get_width()) / 2, (SCREEN_HEIGHT - tutorial_text.get_height()) / 2 + 100),
            )

            if progress.is_unlocked("settings"):
                settings_hint = small_font.render("[S] Settings", True, (130, 130, 130))
                screen.blit(settings_hint, ((SCREEN_WIDTH - settings_hint.get_width()) / 2, (SCREEN_HEIGHT - settings_hint.get_height()) / 2 + 150))

            debug_label = small_font.render(
                f"[D] Debug: {'ON' if debug_mode else 'OFF'}", True,
                (255, 215, 0) if debug_mode else (100, 100, 100)
            )
            screen.blit(debug_label, (10, SCREEN_HEIGHT - 180))
            if debug_mode:
                _draw_debug_panel(screen, small_font)

            keys = pygame.key.get_pressed()
            if keys[pygame.K_r] and not debug_mode:
                current_state = PLAYING
                gear = progress.consume_run_gear()
                apply_run_gear(player, gear)
            if keys[pygame.K_s] and progress.is_unlocked("settings") and not debug_mode:
                settings_items = settings_screen.build_settings_items()
                settings_selected = 0
                settings_return_state = MENU
                current_state = SETTINGS

        # ── PLAYING ───────────────────────────────────────────────
        elif current_state == PLAYING:
            for obj in updatable:
                obj.update(dt)

            # Homing shot steering
            if asteroids:
                for shot in list(homing_shots):
                    nearest = min(asteroids, key=lambda a: shot.position.distance_to(a.position))
                    to_target = nearest.position - shot.position
                    if to_target.length() > 0:
                        new_dir = shot.velocity.normalize().lerp(to_target.normalize(), HOMING_TURN_RATE)
                        if new_dir.length() > 0:
                            shot.velocity = new_dir.normalize() * shot.velocity.length()

            # Shot-asteroid collisions
            for asteroid in list(asteroids):
                for shot in list(shots):
                    if asteroid.collides_with(shot):
                        pos = pygame.Vector2(asteroid.position)
                        asteroid.split()
                        shot.kill()
                        score += int(10 * progress.get_score_multiplier())
                        shake_timer = SHAKE_DURATION
                        if progress.is_enabled("particles"):
                            spawn_particles(particles, pos, (255, 200, 100))

            # Laser-asteroid collisions
            for laser in lasers:
                for asteroid in list(asteroids):
                    if laser.hits(asteroid):
                        pos = pygame.Vector2(asteroid.position)
                        asteroid.split()
                        score += int(10 * progress.get_score_multiplier())
                        shake_timer = SHAKE_DURATION
                        if progress.is_enabled("particles"):
                            spawn_particles(particles, pos, (255, 200, 100))

            # Shield pickups
            for shield in list(shields):
                if player.collides_with(shield):
                    log_event("shield_collected")
                    shield.apply_effect(player)
                    shield.kill()
                    score += int(15 * progress.get_score_multiplier())
                    notification_text = "Shield Collected!"
                    notification_timer = 2.0

            # Powerup pickups
            for powerup in list(powerups):
                if powerup.collides_with(player):
                    log_event("powerup_collected")
                    powerup.apply_effect(player)
                    powerup.kill()
                    score += int(25 * progress.get_score_multiplier())
                    notification_text = "Powerup Collected!"
                    notification_timer = 2.0

            # Asteroid-player collision
            for asteroid in list(asteroids):
                if asteroid.collides_with(player) and player.invincibility_timer <= 0:
                    if player.shields > 0:
                        player.shields -= 1
                        player.invincibility_timer = PLAYER_INVINCIBILITY_SECONDS
                        if player.shields == PLAYER_SHIELD_CAPACITY + progress.get_max_shields_bonus() - 1:
                            asteroid.kill()
                        else:
                            asteroid.split()
                        notification_text = "Shield absorbed hit!"
                        notification_timer = 1.5
                    else:
                        player.lives -= 1
                        player.invincibility_timer = PLAYER_INVINCIBILITY_SECONDS
                        asteroid.split()
                        notification_text = "Life lost!"
                        notification_timer = 1.5
                        if player.lives <= 0:
                            if score > high_score:
                                high_score = score
                                save_high_score(high_score)
                            if not session_processed:
                                newly_unlocked = progress.add_session_score(score)
                                progress.save_progress()
                                session_processed = True
                            current_state = GAME_OVER

            # Shield item spawning
            if progress.is_enabled("shields") and len(shields) < 1 and pygame.time.get_ticks() % 10000 < 50:
                shield_x = pygame.time.get_ticks() % (SCREEN_WIDTH - 100) + 50
                shield_y = pygame.time.get_ticks() % (SCREEN_HEIGHT - 100) + 50
                Shield(shield_x, shield_y, POWERUP_MIN_RADIUS)

            screen.fill("black")

            for thing in drawable:
                thing.draw(screen)

            # Particles
            particles[:] = [p for p in particles if p["life"] > 0]
            for p in particles:
                p["pos"] += p["vel"] * dt
                p["life"] -= dt
                if p["life"] > 0:
                    alpha = p["life"] / p["max_life"]
                    r = max(1, int(3 * alpha))
                    pygame.draw.circle(screen, p["color"], (int(p["pos"].x), int(p["pos"].y)), r)

            score_text = font.render(f"Score: {score}   Lives: {player.lives}", True, "white")
            screen.blit(score_text, (10, 10))

            if notification_timer > 0:
                notify_surf = font.render(notification_text, True, "yellow")
                screen.blit(notify_surf, (SCREEN_WIDTH / 2 - notify_surf.get_width() / 2, 50))
                notification_timer -= dt

            # Screen shake (apply after all drawing)
            if shake_timer > 0 and progress.is_enabled("screen_shake"):
                sx = random.randint(-SHAKE_INTENSITY, SHAKE_INTENSITY)
                sy = random.randint(-SHAKE_INTENSITY, SHAKE_INTENSITY)
                buf = screen.copy()
                screen.fill("black")
                screen.blit(buf, (sx, sy))
                shake_timer -= dt
            else:
                shake_timer = max(0.0, shake_timer - dt)

        # ── GAME OVER ─────────────────────────────────────────────
        elif current_state == GAME_OVER:
            screen.fill("black")
            y = SCREEN_HEIGHT / 2 - 130

            game_over_surf = font.render("GAME OVER", True, "red")
            screen.blit(game_over_surf, (SCREEN_WIDTH / 2 - game_over_surf.get_width() / 2, y))
            y += 50

            score_surf = font.render(f"Final Score: {score}  High Score: {high_score}", True, "white")
            screen.blit(score_surf, (SCREEN_WIDTH / 2 - score_surf.get_width() / 2, y))
            y += 40

            lifetime_surf = small_font.render(
                f"Lifetime Score: {progress.get_lifetime_score()}   Tokens: {progress.get_tokens()}",
                True, (180, 180, 180)
            )
            screen.blit(lifetime_surf, (SCREEN_WIDTH / 2 - lifetime_surf.get_width() / 2, y))
            y += 32

            next_feature, next_threshold = progress.next_unlock()
            if next_feature:
                next_name = progress.UNLOCK_NAMES.get(next_feature, next_feature)
                next_surf = small_font.render(
                    f"Next unlock: {next_name} at {next_threshold} lifetime pts",
                    True, (130, 130, 130)
                )
            else:
                next_surf = small_font.render("All features unlocked!", True, (130, 130, 130))
            screen.blit(next_surf, (SCREEN_WIDTH / 2 - next_surf.get_width() / 2, y))
            y += 40

            if newly_unlocked:
                names = [progress.UNLOCK_NAMES[f] if f in progress.UNLOCK_NAMES else f for f in newly_unlocked]
                unlock_surf = font.render(f"UNLOCKED: {', '.join(names)}!", True, (255, 215, 0))
                screen.blit(unlock_surf, (SCREEN_WIDTH / 2 - unlock_surf.get_width() / 2, y))
                y += 55

            # Navigation options
            nav_items = ["[R] Restart"]
            if progress.is_unlocked("shop"):
                nav_items.append("[TAB] Shop")
            if progress.is_unlocked("settings"):
                nav_items.append("[S] Settings")
            nav_items.append("[Q] Quit")

            nav_surf = small_font.render("   ".join(nav_items), True, (200, 200, 200))
            screen.blit(nav_surf, (SCREEN_WIDTH / 2 - nav_surf.get_width() / 2, y))

            pending_gear = progress.get_run_gear()
            if pending_gear:
                gear_parts = []
                for k, qty in pending_gear.items():
                    name = progress.RUN_GEAR_DEFS[k]["name"]
                    gear_parts.append(f"{name} x{qty}")
                gear_surf = small_font.render(f"Run gear: {', '.join(gear_parts)}", True, (100, 200, 100))
                screen.blit(gear_surf, (SCREEN_WIDTH / 2 - gear_surf.get_width() / 2, y + 40))

            debug_label = small_font.render(
                f"[D] Debug: {'ON' if debug_mode else 'OFF'}", True,
                (255, 215, 0) if debug_mode else (100, 100, 100)
            )
            screen.blit(debug_label, (10, SCREEN_HEIGHT - 180))
            if debug_mode:
                _draw_debug_panel(screen, small_font)

            keys = pygame.key.get_pressed()
            if keys[pygame.K_r] and not debug_mode:
                current_state = PLAYING
                score = 0
                session_processed = False
                newly_unlocked = set()
                particles.clear()
                shake_timer = 0.0
                for asteroid in list(asteroids):
                    asteroid.kill()
                for shot in list(shots):
                    shot.kill()
                for powerup in list(powerups):
                    powerup.kill()
                reset_player(player)
                gear = progress.consume_run_gear()
                apply_run_gear(player, gear)
                asteroid_field.kill()
                asteroid_field = AsteroidField()

            if keys[pygame.K_q]:
                return

            if keys[pygame.K_TAB] and progress.is_unlocked("shop") and not debug_mode:
                current_state = SHOP
                shop_tab = 0
                shop_selected = 0

            if keys[pygame.K_s] and progress.is_unlocked("settings") and not debug_mode:
                settings_items = settings_screen.build_settings_items()
                settings_selected = 0
                settings_return_state = GAME_OVER
                current_state = SETTINGS

        # ── SETTINGS ──────────────────────────────────────────────
        elif current_state == SETTINGS:
            settings_screen.draw_settings(screen, font, small_font, settings_items, settings_selected)

        # ── SHOP ──────────────────────────────────────────────────
        elif current_state == SHOP:
            shop_screen.draw_shop(screen, font, small_font, shop_tab, shop_selected)

        pygame.display.flip()
        dt = clock.tick(60) / 1000


def _draw_debug_panel(screen, small_font):
    sh = screen.get_height()
    lines = [
        f"Lifetime: {progress.get_lifetime_score()}   [← / → ±100]   [1-9: jump to tier]",
        f"Tokens: {progress.get_tokens()}   [↑ / ↓ ±10]   [0: reset tokens]",
        "Tiers: 1=Boost(50)  2=Shake(100)  3=Shields(200)  4=RF(400)  5=Parts(700)",
        "       6=Shop(1000)  7=Life(1200)  8=Laser(1800)  9=DblShot(2500)",
    ]
    for i, line in enumerate(lines):
        surf = small_font.render(line, True, (255, 215, 0))
        screen.blit(surf, (10, sh - 150 + i * 30))


if __name__ == "__main__":
    main()
