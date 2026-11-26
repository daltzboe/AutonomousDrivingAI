"""Vehicle model with manual controls and waypoint-following autopilot."""

import math

import pygame


class Vehicle:
    WIDTH = 34
    HEIGHT = 54
    SPEED = 230.0
    COLOR = (40, 145, 245)

    def __init__(self, x: float, y: float) -> None:
        self.x = float(x)
        self.y = float(y)
        self.angle = 0.0
        self.path: list[tuple[float, float]] = []
        self.waypoint_index = 0
        self.rect = self._make_rect(self.x, self.y, self.angle)

    @classmethod
    def _make_rect(cls, x: float, y: float, angle: float) -> pygame.Rect:
        radians = math.radians(angle)
        width = abs(cls.WIDTH * math.cos(radians)) + abs(
            cls.HEIGHT * math.sin(radians)
        )
        height = abs(cls.HEIGHT * math.cos(radians)) + abs(
            cls.WIDTH * math.sin(radians)
        )
        rect = pygame.Rect(0, 0, round(width), round(height))
        rect.center = (round(x), round(y))
        return rect

    @staticmethod
    def _angle_for_direction(dx: float, dy: float) -> float:
        # The unrotated car points toward the top of the screen.
        return math.degrees(math.atan2(dx, -dy))

    def reset(self, x: float, y: float) -> None:
        self.x = float(x)
        self.y = float(y)
        self.angle = 0.0
        self.path = []
        self.waypoint_index = 0
        self.rect = self._make_rect(self.x, self.y, self.angle)

    def set_path(self, path: list[tuple[float, float]]) -> None:
        self.path = list(path)
        self.waypoint_index = 0

    def update(self, keys, dt: float, environment) -> None:
        """Move the vehicle using keyboard input for manual testing."""
        dx = float(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - float(
            keys[pygame.K_a] or keys[pygame.K_LEFT]
        )
        dy = float(keys[pygame.K_s] or keys[pygame.K_DOWN]) - float(
            keys[pygame.K_w] or keys[pygame.K_UP]
        )
        if dx == 0 and dy == 0:
            return

        if dx and dy:
            dx *= 0.7071
            dy *= 0.7071

        next_x = self.x + dx * self.SPEED * dt
        next_y = self.y + dy * self.SPEED * dt
        next_angle = self._angle_for_direction(dx, dy)
        candidate = self._make_rect(next_x, next_y, next_angle)

        if environment.is_drivable(candidate) and not environment.hits_obstacle(candidate):
            self.x = next_x
            self.y = next_y
            self.angle = next_angle
            self.rect = candidate

    def follow_path(self, dt: float, environment) -> bool:
        """Move toward the next waypoint. Return True when the route is complete."""
        while self.waypoint_index < len(self.path):
            target_x, target_y = self.path[self.waypoint_index]
            dx = target_x - self.x
            dy = target_y - self.y
            distance = math.hypot(dx, dy)

            if distance <= 3.0:
                self.x = target_x
                self.y = target_y
                self.waypoint_index += 1
                continue

            travel = min(self.SPEED * dt, distance)
            direction_x = dx / distance
            direction_y = dy / distance
            next_x = self.x + direction_x * travel
            next_y = self.y + direction_y * travel
            next_angle = self._angle_for_direction(direction_x, direction_y)
            candidate = self._make_rect(next_x, next_y, next_angle)

            if not environment.is_drivable(candidate) or environment.hits_obstacle(candidate):
                return False

            self.x = next_x
            self.y = next_y
            self.angle = next_angle
            self.rect = candidate

            if travel >= distance:
                self.x = target_x
                self.y = target_y
                self.waypoint_index += 1

        return self.waypoint_index >= len(self.path)

    def draw(self, surface: pygame.Surface) -> None:
        car_surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(
            car_surface, self.COLOR,
            (0, 0, self.WIDTH, self.HEIGHT), border_radius=8
        )
        pygame.draw.rect(
            car_surface, (190, 225, 245),
            (6, 8, 22, 12), border_radius=4
        )
        pygame.draw.rect(
            car_surface, (25, 75, 115),
            (6, 34, 22, 9), border_radius=3
        )
        pygame.draw.circle(car_surface, (255, 245, 170), (6, 3), 3)
        pygame.draw.circle(car_surface, (255, 245, 170), (self.WIDTH - 6, 3), 3)

        rotated = pygame.transform.rotate(car_surface, self.angle)
        surface.blit(rotated, rotated.get_rect(center=self.rect.center))
