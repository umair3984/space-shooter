import pygame
import random
import os
import sys
import asyncio
from pygame import mixer

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Set up the game window
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Load sounds
current_dir = os.path.dirname(os.path.abspath(__file__))
shoot_sound_path = os.path.join(current_dir, 'shoot.mp3')
explosion_sound_path = os.path.join(current_dir, 'explosion.mp3')
background_music_path = os.path.join(current_dir, 'background_music.mp3')

shoot_sound = pygame.mixer.Sound(shoot_sound_path)
explosion_sound = pygame.mixer.Sound(explosion_sound_path)
pygame.mixer.music.load(background_music_path)
pygame.mixer.music.play(-1)  # -1 means loop indefinitely

# Load spaceship images
player_ship_path = os.path.join(current_dir, 'player_ship.png')
enemy_ship_path = os.path.join(current_dir, 'enemy_ship.png')

# Load and scale the images
player_ship = pygame.image.load(player_ship_path)
player_ship = pygame.transform.scale(player_ship, (50, 50))  # Adjust size as needed

enemy_ship = pygame.image.load(enemy_ship_path)
enemy_ship = pygame.transform.scale(enemy_ship, (40, 40))  # Adjust size as needed

# Load assets
bullet_img = pygame.Surface((10, 20))  # Placeholder, replace with actual sprite
bullet_img.fill((255, 255, 0))

# Touch controls for mobile
touch_controls = {
    'left_button': pygame.Rect(50, HEIGHT - 100, 60, 60),
    'right_button': pygame.Rect(120, HEIGHT - 100, 60, 60),
    'shoot_button': pygame.Rect(WIDTH - 110, HEIGHT - 100, 60, 60)
}

class Player:
    def __init__(self):
        self.image = player_ship
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speed = 5
        self.lives = 3
        self.score = 0
        self.power_level = 1
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.power_level == 1:
                bullets.append(Bullet(self.rect.centerx, self.rect.top))
            elif self.power_level == 2:
                bullets.append(Bullet(self.rect.centerx - 10, self.rect.top))
                bullets.append(Bullet(self.rect.centerx + 10, self.rect.top))
            shoot_sound.play()


class Enemy:
    def __init__(self):
        self.image = enemy_ship
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 4)
        self.health = 2

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)


class Bullet:
    def __init__(self, x, y):
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = -10

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            bullets.remove(self)


class PowerUp:
    def __init__(self, x, y):
        self.image = pygame.Surface((20, 20))
        self.image.fill((0, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            power_ups.remove(self)


async def main():
    # Game objects
    player = Player()
    enemies = [Enemy() for _ in range(8)]
    bullets = []
    power_ups = []

    # Game loop
    running = True
    game_over = False
    clock = pygame.time.Clock()

    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over:
                    player.shoot()
                if event.key == pygame.K_r and game_over:
                    # Reset game
                    game_over = False
                    player = Player()
                    enemies = [Enemy() for _ in range(8)]
                    bullets = []
                    power_ups = []
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Handle touch controls
                pos = event.pos
                if touch_controls['left_button'].collidepoint(pos):
                    player.rect.x = max(0, player.rect.x - player.speed)
                elif touch_controls['right_button'].collidepoint(pos):
                    player.rect.x = min(WIDTH - player.rect.width, player.rect.x + player.speed)
                elif touch_controls['shoot_button'].collidepoint(pos) and not game_over:
                    player.shoot()

        if not game_over:
            # Update
            player.update()
            for enemy in enemies[:]:
                enemy.update()
                # Check collision with player
                if enemy.rect.colliderect(player.rect):
                    player.lives -= 1
                    enemies.remove(enemy)
                    if player.lives <= 0:
                        game_over = True

            for bullet in bullets[:]:
                bullet.update()
                # Check collision with enemies
                for enemy in enemies[:]:
                    if bullet.rect.colliderect(enemy.rect):
                        enemy.health -= 1
                        if enemy.health <= 0:
                            enemies.remove(enemy)
                            player.score += 100
                            if random.random() < 0.1:  # 10% chance for power-up
                                power_ups.append(PowerUp(enemy.rect.x, enemy.rect.y))
                            enemies.append(Enemy())
                        try:
                            bullets.remove(bullet)
                        except ValueError:
                            pass
                        break

            for power_up in power_ups[:]:
                power_up.update()
                if power_up.rect.colliderect(player.rect):
                    player.power_level = min(player.power_level + 1, 2)
                    player.shoot_delay = max(player.shoot_delay - 50, 150)
                    power_ups.remove(power_up)

        # Draw
        screen.fill((0, 0, 0))
        if not game_over:
            screen.blit(player_ship, (player.rect.x, player.rect.y))
            for enemy in enemies:
                screen.blit(enemy_ship, (enemy.rect.x, enemy.rect.y))
            for bullet in bullets:
                screen.blit(bullet_img, bullet.rect)
            for power_up in power_ups:
                pygame.draw.rect(screen, (0, 255, 255), power_up.rect)

            # Draw HUD
            font = pygame.font.Font(None, 36)
            score_text = font.render(f'Score: {player.score}', True, (255, 255, 255))
            lives_text = font.render(f'Lives: {player.lives}', True, (255, 255, 255))
            screen.blit(score_text, (10, 10))
            screen.blit(lives_text, (10, 40))

            # Draw touch controls
            pygame.draw.rect(screen, (100, 100, 100), touch_controls['left_button'])
            pygame.draw.rect(screen, (100, 100, 100), touch_controls['right_button'])
            pygame.draw.rect(screen, (100, 100, 100), touch_controls['shoot_button'])
        else:
            # Game Over screen
            font = pygame.font.Font(None, 74)
            text = font.render('GAME OVER', True, (255, 0, 0))
            text_rect = text.get_rect(center=(WIDTH / 2, HEIGHT / 2))
            screen.blit(text, text_rect)

            font = pygame.font.Font(None, 36)
            restart_text = font.render('Press R to restart', True, (255, 255, 255))
            restart_rect = restart_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 50))
            screen.blit(restart_text, restart_rect)

        pygame.display.flip()
        await asyncio.sleep(0)

    pygame.quit()

asyncio.run(main())
