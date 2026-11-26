"""Static 2D road environment for the autonomous driving project."""

import pygame


class Environment:
    WIDTH = 1000
    HEIGHT = 700

    GRASS = (54, 125, 75)
    ROAD = ( sixty := 60, 60, 64)
    ROAD_EDGE = (225, 225, 225)
    LANE = (245, 205, 65)
    OBSTACLE = (220, 75, 65)
    GOAL = (55, 205, 115)

    def __init__(self) -> None:
        self.start_position = (330, 545)
        self.goal_rect = pygame.Rect(650, 105, 48, 48)
        self.obstacles = [
            pygame.Rect(455, 310, 38, 38),
            pygame.Rect(555, 455, 38, 38),
        ]
        self.road_rects = [
            pygame.Rect(250, 0, 500, self.HEIGHT),
            pygame.Rect(0, 250, self.WIDTH, 200),
        ]

    def is_drivable(self, rect: pygame.Rect) -> bool:
        return any(road.contains(rect) for road in self.road_rects)

    def hits_obstacle(self, rect: pygame.Rect) -> bool:
        return any(rect.colliderect(obstacle) for obstacle in self.obstacles)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(self.GRASS)

        for road in self.road_rects:
            pygame.draw.rect(surface, self.ROAD_EDGE, road.inflate(8, 8))
            pygame.draw.rect(surface, self.ROAD, road)

        # Dashed lane markings on the vertical road.
        for y in range(12, self.HEIGHT, 72):
            pygame.draw.rect(surface, self.LANE, (495, y, 10, 38))

        # Dashed lane markings on the horizontal road.
        for x in range(12, self.WIDTH, 72):
            pygame.draw.rect(surface, self.LANE, (x, 345, 38, 10))

        # Starting marker.
        pygame.draw.circle(surface, (90, 190, 255), self.start_position, 12, 3)

        # Destination marker.
        pygame.draw.rect(surface, self.GOAL, self.goal_rect, border_radius=7)
        font = pygame.font.SysFont("consolas", 13, bold=True)
        label = font.render("GOAL", True, (15, 55, 35))
        surface.blit(label, (self.goal_rect.x + 3, self.goal_rect.y + 15))

        # Construction-style obstacles.
        for obstacle in self.obstacles:
            pygame.draw.rect(surface, self.OBSTACLE, obstacle, border_radius=5)
            pygame.draw.line(surface, (255, 220, 180), obstacle.topleft, obstacle.bottomright, 4)
            pygame.draw.line(surface, (255, 220, 180), obstacle.topright, obstacle.bottomleft, 4)
