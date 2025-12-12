import pygame
import sys
from score_manager import load_high_score, save_high_score
from logger import log_state, log_event
from constants import SCREEN_WIDTH, SCREEN_HEIGHT
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot
from powerup import PowerUp

def main():
    print(f"Starting Asteroids with pygame version: {pygame.version.ver}")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")
    # Game states
    MENU = 0
    PLAYING = 1
    GAME_OVER = 2
    SETTINGS = 3
    current_state = MENU
    score = 0
    high_score = 0
    notification_text = ""
    notification_timer = 0.0
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock() # create clock to manage frame rate
    dt = 0.0
    updatable = pygame.sprite.Group() # sprites that need updating
    drawable = pygame.sprite.Group() # sprites that need drawing
    asteroids = pygame.sprite.Group() 
    shots = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    high_score = load_high_score() # load high score from file
    Asteroid.containers = (asteroids, updatable, drawable)
    Player.containers = (updatable, drawable)
    AsteroidField.containers = updatable 
    Shot.containers = (shots, updatable, drawable)
    PowerUp.containers = (powerups, updatable, drawable)
    asteroid_field = AsteroidField()
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    while True:
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT: # Quit the game
                return
            
        screen.fill("black")

        if current_state == MENU:
            # draw menu text
            font = pygame.font.SysFont("arial", 36)
            title_text = font.render("Astroids - Press SPACE to Start", True, "white")
            # center text
            screen.blit(
                title_text,
                (
                    (SCREEN_WIDTH - title_text.get_width()) / 2,
                    (SCREEN_HEIGHT - title_text.get_height()) / 2,
                ),
            )

        # Check for game start
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                current_state = PLAYING

        elif current_state == PLAYING:
            # update game objects
            for obj in updatable:
                obj.update(dt)
            # check for collisions
            for asteroid in asteroids:
                for shot in shots:
                    if asteroid.collides_with(shot):
                        asteroid.split()
                        shot.kill()
                        score += 10
            for powerup in powerups:
                if powerup.collides_with(player):
                    log_event("powerup_collected")
                    powerup.apply_effect(player)
                    powerup.kill()
                    # indicate powerup collected on screen
                    notification_text = "Powerup Collected!"
                    notification_timer = 2.0  # show for 2 seconds
                    # align with powerup position
                    screen.blit(font.render(notification_text, True, "yellow"), (player.position.x - 50, player.position.y - 50))
            # check for player collisions and update high score and game state
            for asteroid in asteroids:
                if asteroid.collides_with(player):
                    if score > high_score:
                        high_score = score
                        save_high_score(high_score)
                    current_state = GAME_OVER
            # draw game objects
            for thing in drawable:
                thing.draw(screen)
            # draw score
            score_text = font.render(f"Score: {score}", True, "white")
            screen.blit(score_text, (10, 10)) # top-left corner
            # draw notification text if any
            if notification_timer > 0:
                notify_surf = font.render(notification_text, True, "yellow")
                # center at top of screen
                screen.blit(notify_surf, (SCREEN_WIDTH/2 - notify_surf.get_width()/2, 50))
                notification_timer -= dt

        elif current_state == GAME_OVER:
            # Draw Game Over Text
            game_over_text = font.render("GAME OVER", True, "red")
            score_text = font.render(f"Final Score: {score}  High Score: {high_score}", True, "white")
            restart_text = font.render("Press R to Restart", True, "white")
            # center texts
            screen.blit(game_over_text, (SCREEN_WIDTH/2 - game_over_text.get_width()/2, SCREEN_HEIGHT/2 - 50))
            screen.blit(score_text, (SCREEN_WIDTH/2 - score_text.get_width()/2, SCREEN_HEIGHT/2))
            screen.blit(restart_text, (SCREEN_WIDTH/2 - restart_text.get_width()/2, SCREEN_HEIGHT/2 + 50))
            # Check for restart
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                current_state = PLAYING
                score = 0
                for asteroid in asteroids:
                    asteroid.kill()
                for shot in shots:
                    shot.kill()
                for powerup in powerups:
                    powerup.kill()
                player.position = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
                player.velocity = pygame.Vector2(0, 0)
                asteroid_field.kill()
                asteroid_field = AsteroidField()


        pygame.display.flip()   
        dt = clock.tick(60) / 1000  # limit to 60 FPS
        
        

if __name__ == "__main__":
    main()
