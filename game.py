"""Gravity Flip: Escape Dimension - Python/Pygame edition.

Run with: python game.py
Install the only dependency with: pip install pygame
"""

import random
import sys
from dataclasses import dataclass

import pygame


WIDTH, HEIGHT = 1100, 650
FPS = 60
CYAN = (96, 232, 255)
VIOLET = (167, 139, 250)
PINK = (255, 95, 141)
INK = (233, 247, 255)
MUTED = (128, 145, 173)
BG = (8, 13, 38)


@dataclass
class FallingObject:
    kind: str
    x: float
    y: float
    speed: float
    size: int = 22
    rotation: float = 0

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.size, self.size)


class GravityFlip:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Gravity Flip: Escape Dimension")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font_big = pygame.font.Font(None, 96)
        self.font_title = pygame.font.Font(None, 62)
        self.font = pygame.font.Font(None, 26)
        self.font_small = pygame.font.Font(None, 18)
        self.stars = [(random.randrange(WIDTH), random.randrange(HEIGHT), random.randrange(1, 3)) for _ in range(90)]
        self.state = "start"
        self.reset()

    def reset(self) -> None:
        self.player = pygame.Rect(WIDTH // 2 - 18, HEIGHT - 92, 36, 42)
        self.player_velocity = pygame.Vector2(0, 0)
        self.gravity = 1
        self.flip_timer = 20.0
        self.elapsed = 0.0
        self.score = 0
        self.crystals = 0
        self.combo = 0
        self.lives = 3
        self.invulnerable = 0.0
        self.objects: list[FallingObject] = []
        self.particles: list[list[float | tuple[int, int, int]]] = []
        for i in range(4):
            self.spawn("crystal", 80 + i * 245, 150 + (i % 2) * 100)
        for i in range(3):
            self.spawn("hazard", 150 + i * 330, 270 + (i % 2) * 150)

    def spawn(self, kind: str, x: float | None = None, y: float | None = None) -> None:
        size = 20 if kind == "crystal" else 32
        self.objects.append(FallingObject(kind, x if x is not None else random.randint(30, WIDTH - 62), y if y is not None else -45, 70 + random.random() * 45 + self.elapsed * 1.8, size))

    def flip_gravity(self) -> None:
        if self.state != "playing":
            return
        self.gravity *= -1
        self.flip_timer = 20.0
        self.player_velocity.y = self.gravity * 120
        self.burst(self.player.center, CYAN, 15)

    def burst(self, position: tuple[int, int], color: tuple[int, int, int], amount: int) -> None:
        for _ in range(amount):
            self.particles.append([float(position[0]), float(position[1]), (random.uniform(-2.5, 2.5), random.uniform(-2.5, 2.5)), 0.5 + random.random() * 0.5, color])

    def update(self, dt: float) -> None:
        if self.state != "playing":
            return
        self.elapsed += dt
        self.flip_timer -= dt
        self.invulnerable = max(0, self.invulnerable - dt)
        if self.flip_timer <= 0:
            self.flip_gravity()

        keys = pygame.key.get_pressed()
        direction = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        self.player_velocity.x += (direction * 360 - self.player_velocity.x) * min(1, dt * 9)
        self.player.x = max(28, min(WIDTH - 64, int(self.player.x + self.player_velocity.x * dt)))
        self.player_velocity.y += self.gravity * 920 * dt
        self.player.y += int(self.player_velocity.y * dt)
        boundary = HEIGHT - 50 if self.gravity == 1 else 50
        if self.gravity == 1 and self.player.bottom >= boundary:
            self.player.bottom = boundary
            self.player_velocity.y = 0
        elif self.gravity == -1 and self.player.top <= boundary:
            self.player.top = boundary
            self.player_velocity.y = 0

        spawn_rate = 0.8 + min(self.elapsed / 80, 1) * 0.5
        if random.random() < dt * spawn_rate:
            self.spawn("crystal" if random.random() < 0.64 else "hazard")
        for item in self.objects[:]:
            item.y += item.speed * self.gravity * dt
            item.rotation += dt * 2
            if self.player.colliderect(item.rect):
                self.collect(item)
                self.objects.remove(item)
            elif item.y > HEIGHT + 80 or item.y < -100:
                self.objects.remove(item)
        for particle in self.particles[:]:
            particle[0] += particle[2][0] * 60 * dt
            particle[1] += particle[2][1] * 60 * dt
            particle[3] -= dt
            if particle[3] <= 0:
                self.particles.remove(particle)

    def collect(self, item: FallingObject) -> None:
        if item.kind == "crystal":
            self.crystals += 1
            self.combo += 1
            self.score += 10 + min(self.combo, 10) * 3
            self.burst(item.rect.center, VIOLET, 16)
        elif self.invulnerable <= 0:
            self.lives -= 1
            self.combo = 0
            self.invulnerable = 1.3
            self.burst(self.player.center, PINK, 24)
            if self.lives <= 0:
                self.state = "game_over"

    def draw_text(self, text: str, position: tuple[int, int], font: pygame.font.Font, color: tuple[int, int, int] = INK, center: bool = False) -> None:
        image = font.render(text, True, color)
        rect = image.get_rect(center=position) if center else image.get_rect(topleft=position)
        self.screen.blit(image, rect)

    def draw_world(self) -> None:
        self.screen.fill(BG)
        for x, y, size in self.stars:
            pygame.draw.rect(self.screen, (110, 145, 205), (x, y, size, size))
        for x in range(0, WIDTH, 55):
            pygame.draw.line(self.screen, (17, 27, 58), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, 55):
            pygame.draw.line(self.screen, (17, 27, 58), (0, y), (WIDTH, y))
        pygame.draw.rect(self.screen, (21, 30, 67), (0, 0, WIDTH, 50))
        pygame.draw.rect(self.screen, (21, 30, 67), (0, HEIGHT - 50, WIDTH, 50))
        boundary = HEIGHT - 50 if self.gravity == 1 else 50
        pygame.draw.line(self.screen, CYAN, (0, boundary), (WIDTH, boundary), 4)
        for x in range(20, WIDTH, 80):
            pygame.draw.rect(self.screen, (37, 55, 93), (x, boundary + (8 if self.gravity == 1 else -10), 42, 2))
        for x, offset in [(220, 0), (430, 75), (640, 0), (850, 75)]:
            y = HEIGHT - 180 - offset if self.gravity == 1 else 180 + offset
            pygame.draw.rect(self.screen, (24, 38, 75), (x, y, 120, 8))
            pygame.draw.rect(self.screen, (81, 101, 142), (x, y, 120, 2))

    def draw_player(self) -> None:
        if self.invulnerable > 0 and int(self.invulnerable * 12) % 2 == 0:
            return
        cx, cy = self.player.center
        pygame.draw.polygon(self.screen, CYAN, [(cx - 16, cy + 18), (cx - 12, cy - 10), (cx, cy - 20), (cx + 12, cy - 10), (cx + 16, cy + 18)])
        pygame.draw.rect(self.screen, (7, 17, 43), (cx - 8, cy - 5, 16, 13))
        pygame.draw.rect(self.screen, (191, 250, 255), (cx - 5, cy - 2, 4, 5))
        pygame.draw.rect(self.screen, (191, 250, 255), (cx + 2, cy - 2, 4, 5))
        pygame.draw.rect(self.screen, VIOLET, (cx - 12, cy + 18, 8, 5))
        pygame.draw.rect(self.screen, VIOLET, (cx + 4, cy + 18, 8, 5))

    def draw_objects(self) -> None:
        for item in self.objects:
            rect = item.rect
            if item.kind == "crystal":
                pygame.draw.polygon(self.screen, VIOLET, [(rect.centerx, rect.top - 3), (rect.right, rect.centery), (rect.centerx, rect.bottom + 3), (rect.left, rect.centery)])
            else:
                pygame.draw.line(self.screen, PINK, rect.topleft, rect.bottomright, 5)
                pygame.draw.line(self.screen, PINK, rect.topright, rect.bottomleft, 5)

    def draw_hud(self) -> None:
        self.draw_text(f"SCORE  {self.score:05d}", (24, 15), self.font, INK)
        self.draw_text(f"CRYSTALS  {self.crystals}  x{self.combo}" if self.combo > 1 else f"CRYSTALS  {self.crystals}", (190, 15), self.font, INK)
        gravity_text = "FLOOR ↓" if self.gravity == 1 else "CEILING ↑"
        self.draw_text(f"GRAVITY  {gravity_text}", (WIDTH - 300, 15), self.font, CYAN)
        self.draw_text("♥ " * self.lives, (WIDTH - 115, 15), self.font, PINK)

    def draw_overlay(self, title: str, subtitle: str, button: str) -> None:
        shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        shade.fill((5, 8, 25, 225))
        self.screen.blit(shade, (0, 0))
        self.draw_text("LABORATORY // SECTOR 15", (WIDTH // 2, 170), self.font_small, CYAN, True)
        self.draw_text(title, (WIDTH // 2, 255), self.font_big, INK, True)
        self.draw_text(subtitle, (WIDTH // 2, 325), self.font, MUTED, True)
        pygame.draw.rect(self.screen, CYAN, (WIDTH // 2 - 125, 370, 250, 52))
        self.draw_text(button, (WIDTH // 2, 396), self.font, (5, 15, 28), True)
        self.draw_text("← → / A D  MOVE     SPACE  FLIP GRAVITY     P  PAUSE", (WIDTH // 2, 470), self.font_small, MUTED, True)

    def draw(self) -> None:
        self.draw_world()
        if self.state in ("playing", "paused", "game_over"):
            self.draw_objects()
            self.draw_player()
            for x, y, _, life, color in self.particles:
                pygame.draw.rect(self.screen, color, (int(x), int(y), 3, 3))
            self.draw_hud()
        if self.state == "start":
            self.draw_overlay("ESCAPE DIMENSION", "Gravity is malfunctioning. Collect crystals. Survive the flip.", "INITIALIZE ESCAPE")
        elif self.state == "paused":
            self.draw_overlay("STABILIZE YOURSELF", "Press P to resume the experiment.", "RESUME")
        elif self.state == "game_over":
            self.draw_overlay("THE DIMENSION COLLAPSED", f"Final score: {self.score}   Crystals: {self.crystals}", "RESTART RUN")

    def run(self) -> None:
        while True:
            dt = self.clock.tick(FPS) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE) and self.state in ("start", "game_over"):
                        self.reset()
                        self.state = "playing"
                    elif event.key == pygame.K_SPACE and self.state == "playing":
                        self.flip_gravity()
                    elif event.key == pygame.K_p and self.state in ("playing", "paused"):
                        self.state = "paused" if self.state == "playing" else "playing"
            self.update(dt)
            self.draw()
            pygame.display.flip()


if __name__ == "__main__":
    GravityFlip().run()
