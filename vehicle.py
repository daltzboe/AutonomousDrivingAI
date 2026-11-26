"""Vehicle model. Manual controls are temporary and used only for Phase 1 testing."""

import pygame


class Vehicle:
    WIDTH = 34
    HEIGHT = 54
    SPEED = 230.0
    COLOR = (40, 145, 245)

    def __init__(self, x: float, y: float) -> None:
        self.x = float(x)
        self.y = float(y)
        self.rect = pygame.Rect(0, 0, self.WIDTH, self.HEIGHT)
        self.rect.center = (round(self.x), round(self.y))

    def reset(self, x: float, y: float) -> None:
        self.x = float(x)
        self.y = float(y)
        self.rect.center = (round(self.x), round(self.y))

    def update(self, keys, dt: float, environment) -> None:
        dx = float(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - float(
            keys[pygame.K_a] or keys[pygame.K_LEFT]
        )
        dy = float(keys[pygame.K_s] or keys[pygame.K_DOWN]) - float(
            keys[pygame.K_w] or keys[pygame.K_UP]
        )
        if dx and dy:
            dx *= 0.7071
            dy *= 0.7071

        next_x = self.x + dx * self.SPEED * dt
        next_y = self.y + dy * self.SPEED * dt
        candidate = self.rect.copy()
        candidate.center = (round(next_x), round(next_y))

        if environment.is_drivable(candidate) and not environment.hits_obstacle(candidate):
            self.x = next_x
            self.y = next_y
            self.rect = candidate

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, self.COLOR, self.rect, border_radius=8)
        pygame.draw.rect(surface, (190, 225, 245), (self.rect.x + 6, self.rect.y + 8, 22, 12), border_radius=4)
        pygame.draw.rect(surface, (25, 75, 115), (self.rect.x + 6, self.rect.y + 34, 22, 9), border_radius=3)
        pygame.draw.circle(surface, (255, 245, 170), (self.rect.left + 6, self.rect.top + 3), 3)
        pygame.draw.circle(surface, (255, 245, 170), (self.rect.right - 6, self.rect.top + 3), 3)
