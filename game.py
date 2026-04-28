import math
import random
from dataclasses import dataclass

import pygame


# --- Configuration ---
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
FPS = 60
TILE_SIZE = 48
GRAVITY = 0.85
MAX_FALL_SPEED = 18
PLAYER_SPEED = 5
PLAYER_JUMP_POWER = 16
BG_COLOR = (108, 193, 255)


LEVEL_MAP = [
    "........................................................................................",
    "........................................................................................",
    "........................................................................................",
    "...........................C.........................................................F...",
    "............C.....................#####............................C............#######...",
    "..P......#####..............E...............#####.....E.................................",
    "################....###########..................##########..............#####...........",
    "....................#....................C...............................................",
    "....................#............######.....................E............................",
    ".................####....................................................#####............",
    "...........C.............................................................................",
    "#############################....#########################....########################....",
    "##############################################################################....########",
]


@dataclass
class Camera:
    offset_x: float = 0

    def update(self, target_rect: pygame.Rect) -> None:
        target_x = target_rect.centerx - SCREEN_WIDTH // 2
        self.offset_x += (target_x - self.offset_x) * 0.15
        self.offset_x = max(0, self.offset_x)


class Platform(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill((64, 45, 32))
        pygame.draw.rect(self.image, (92, 70, 50), (4, 4, TILE_SIZE - 8, TILE_SIZE - 8))
        self.rect = self.image.get_rect(topleft=(x, y))


class Coin(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int):
        super().__init__()
        self.base_y = y + 10
        self.time_offset = random.random() * math.pi * 2
        self.image = pygame.Surface((26, 26), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, (255, 216, 64), (0, 0, 26, 26))
        pygame.draw.ellipse(self.image, (255, 239, 150), (4, 4, 18, 18))
        self.rect = self.image.get_rect(midbottom=(x + TILE_SIZE // 2, y + TILE_SIZE))

    def update(self, dt: float) -> None:
        t = pygame.time.get_ticks() / 500 + self.time_offset
        self.rect.y = int(self.base_y + math.sin(t) * 6)


class GoalFlag(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE * 2), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (220, 220, 220), (8, 0, 6, TILE_SIZE * 2))
        pygame.draw.polygon(
            self.image,
            (255, 65, 65),
            [(14, 8), (44, 20), (14, 30)],
        )
        self.rect = self.image.get_rect(bottomleft=(x, y + TILE_SIZE))


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int):
        super().__init__()
        self.image = pygame.Surface((38, 28), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, (177, 88, 47), (0, 2, 38, 24))
        pygame.draw.rect(self.image, (77, 38, 28), (6, 18, 8, 6))
        pygame.draw.rect(self.image, (77, 38, 28), (24, 18, 8, 6))
        self.rect = self.image.get_rect(midbottom=(x + TILE_SIZE // 2, y + TILE_SIZE))
        self.vx = random.choice([-1.8, 1.8])
        self.vy = 0.0

    def update(self, platforms: pygame.sprite.Group) -> None:
        self.vy = min(self.vy + GRAVITY, MAX_FALL_SPEED)

        self.rect.x += int(self.vx)
        if pygame.sprite.spritecollideany(self, platforms):
            self.rect.x -= int(self.vx)
            self.vx *= -1

        self.rect.y += int(self.vy)
        collisions = pygame.sprite.spritecollide(self, platforms, False)
        if collisions:
            for platform in collisions:
                if self.vy > 0 and self.rect.bottom >= platform.rect.top:
                    self.rect.bottom = platform.rect.top
                    self.vy = 0

        front_probe = self.rect.midbottom
        probe_rect = pygame.Rect(front_probe[0] + (12 if self.vx > 0 else -12), front_probe[1] + 2, 2, 2)
        if not any(platform.rect.colliderect(probe_rect) for platform in platforms):
            self.vx *= -1


class Player(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int):
        super().__init__()
        self.image = pygame.Surface((34, 46), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (197, 45, 47), (6, 2, 22, 16))
        pygame.draw.rect(self.image, (47, 104, 199), (4, 16, 26, 24))
        pygame.draw.rect(self.image, (242, 214, 181), (10, 8, 14, 10))
        self.rect = self.image.get_rect(midbottom=(x + TILE_SIZE // 2, y + TILE_SIZE))
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.spawn = pygame.Vector2(self.rect.x, self.rect.y)
        self.score = 0
        self.health = 3

    def handle_input(self, keys: pygame.key.ScancodeWrapper) -> None:
        self.vx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_q]:
            self.vx = -PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = PLAYER_SPEED

        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_z]) and self.on_ground:
            self.vy = -PLAYER_JUMP_POWER
            self.on_ground = False

    def physics_step(self, platforms: pygame.sprite.Group) -> None:
        self.rect.x += int(self.vx)
        for platform in pygame.sprite.spritecollide(self, platforms, False):
            if self.vx > 0:
                self.rect.right = platform.rect.left
            elif self.vx < 0:
                self.rect.left = platform.rect.right

        self.vy = min(self.vy + GRAVITY, MAX_FALL_SPEED)
        self.rect.y += int(self.vy)
        self.on_ground = False
        for platform in pygame.sprite.spritecollide(self, platforms, False):
            if self.vy > 0:
                self.rect.bottom = platform.rect.top
                self.vy = 0
                self.on_ground = True
            elif self.vy < 0:
                self.rect.top = platform.rect.bottom
                self.vy = 0

    def respawn(self) -> None:
        self.rect.topleft = (int(self.spawn.x), int(self.spawn.y))
        self.vx = 0
        self.vy = 0


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Super Platformer - Jeu 2D")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)
        self.big_font = pygame.font.SysFont("Arial", 48, bold=True)

        self.camera = Camera()

        self.platforms = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.goal_group = pygame.sprite.GroupSingle()
        self.player = None

        self.world_width = 0
        self.state = "running"
        self.load_level(LEVEL_MAP)

    def load_level(self, level_data: list[str]) -> None:
        for y, row in enumerate(level_data):
            for x, cell in enumerate(row):
                world_x = x * TILE_SIZE
                world_y = y * TILE_SIZE

                if cell == "#":
                    self.platforms.add(Platform(world_x, world_y))
                elif cell == "P":
                    self.player = Player(world_x, world_y)
                elif cell == "C":
                    self.coins.add(Coin(world_x, world_y))
                elif cell == "E":
                    self.enemies.add(Enemy(world_x, world_y))
                elif cell == "F":
                    self.goal_group.add(GoalFlag(world_x, world_y))

        self.world_width = max(len(row) for row in level_data) * TILE_SIZE

    def update(self, dt: float) -> None:
        if self.state != "running":
            return

        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        self.player.physics_step(self.platforms)

        self.coins.update(dt)
        for enemy in self.enemies:
            enemy.update(self.platforms)

        collected = pygame.sprite.spritecollide(self.player, self.coins, True)
        self.player.score += len(collected) * 100

        hit_enemies = pygame.sprite.spritecollide(self.player, self.enemies, False)
        for enemy in hit_enemies:
            if self.player.vy > 0 and self.player.rect.bottom - enemy.rect.top < 20:
                self.enemies.remove(enemy)
                self.player.vy = -10
                self.player.score += 250
            else:
                self.player.health -= 1
                self.player.respawn()
                if self.player.health <= 0:
                    self.state = "lose"
                break

        if self.player.rect.top > SCREEN_HEIGHT + 400:
            self.player.health -= 1
            self.player.respawn()
            if self.player.health <= 0:
                self.state = "lose"

        if self.goal_group.sprite and self.player.rect.colliderect(self.goal_group.sprite.rect):
            self.state = "win"

        self.camera.update(self.player.rect)
        self.camera.offset_x = min(self.camera.offset_x, max(0, self.world_width - SCREEN_WIDTH))

    def draw_background(self) -> None:
        self.screen.fill(BG_COLOR)
        for i in range(5):
            cloud_x = (i * 260 - (self.camera.offset_x * 0.3) % 1300) - 120
            pygame.draw.ellipse(self.screen, (240, 248, 255), (cloud_x, 60 + i * 20 % 80, 130, 45))

        pygame.draw.rect(self.screen, (73, 183, 61), (0, SCREEN_HEIGHT - 70, SCREEN_WIDTH, 70))

    def draw(self) -> None:
        self.draw_background()

        def blit_with_camera(surface: pygame.Surface, rect: pygame.Rect) -> None:
            draw_rect = rect.move(-self.camera.offset_x, 0)
            self.screen.blit(surface, draw_rect)

        for platform in self.platforms:
            blit_with_camera(platform.image, platform.rect)
        for coin in self.coins:
            blit_with_camera(coin.image, coin.rect)
        for enemy in self.enemies:
            blit_with_camera(enemy.image, enemy.rect)
        if self.goal_group.sprite:
            blit_with_camera(self.goal_group.sprite.image, self.goal_group.sprite.rect)
        blit_with_camera(self.player.image, self.player.rect)

        hud = self.font.render(
            f"Score: {self.player.score}   Vies: {self.player.health}   Pieces: {len(self.coins)}",
            True,
            (20, 20, 20),
        )
        self.screen.blit(hud, (16, 12))

        if self.state == "win":
            txt = self.big_font.render("Victoire !", True, (16, 110, 30))
            self.screen.blit(txt, txt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20)))
            tip = self.font.render("Appuie sur R pour rejouer", True, (30, 30, 30))
            self.screen.blit(tip, tip.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30)))
        elif self.state == "lose":
            txt = self.big_font.render("Game Over", True, (150, 20, 20))
            self.screen.blit(txt, txt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20)))
            tip = self.font.render("Appuie sur R pour recommencer", True, (30, 30, 30))
            self.screen.blit(tip, tip.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30)))

        pygame.display.flip()

    def reset(self) -> None:
        self.platforms.empty()
        self.coins.empty()
        self.enemies.empty()
        self.goal_group.empty()
        self.player = None
        self.state = "running"
        self.camera = Camera()
        self.load_level(LEVEL_MAP)

    def run(self) -> None:
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r and self.state in {"win", "lose"}:
                    self.reset()

            self.update(dt)
            self.draw()

        pygame.quit()


if __name__ == "__main__":
    Game().run()
