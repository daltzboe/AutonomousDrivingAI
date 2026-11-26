"""Pygame application loop for the autonomous driving simulation."""

import sys

import pygame

from environment import Environment
from pathfinding import AStarPlanner
from sensors import LidarSensor
from vehicle import Vehicle


class Simulation:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Autonomous Driving AI | Phase 3: LiDAR Perception")
        self.screen = pygame.display.set_mode((Environment.WIDTH, Environment.HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 18)
        self.environment = Environment()
        self.vehicle = Vehicle(*self.environment.start_position)
        self.planner = AStarPlanner(self.environment)
        self.lidar = LidarSensor()
        self.sensor_readings = self.lidar.scan(self.vehicle, self.environment)
        self.lidar_enabled = True
        self.route: list[tuple[float, float]] = []
        self.autopilot = False
        self.goal_reached = False
        self.status = "MANUAL MODE"
        self.running = True

    def start_autopilot(self) -> None:
        goal = self.environment.goal_rect.center
        route = self.planner.find_path((self.vehicle.x, self.vehicle.y), goal)

        if not route:
            self.status = "NO SAFE ROUTE FOUND"
            self.autopilot = False
            return

        self.route = route
        self.vehicle.set_path(route)
        self.autopilot = True
        self.goal_reached = False
        self.status = "AUTOPILOT: A* ROUTE ACTIVE"

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.vehicle.reset(*self.environment.start_position)
                    self.route = []
                    self.autopilot = False
                    self.goal_reached = False
                    self.status = "MANUAL MODE"
                elif event.key == pygame.K_p:
                    if self.autopilot:
                        self.autopilot = False
                        self.status = "AUTOPILOT PAUSED"
                    elif not self.goal_reached:
                        self.start_autopilot()
                elif event.key == pygame.K_l:
                    self.lidar_enabled = not self.lidar_enabled

    def update(self, dt: float) -> None:
        if self.autopilot:
            if self.vehicle.follow_path(dt, self.environment):
                self.autopilot = False
                self.goal_reached = True
                self.status = "DESTINATION REACHED!"
        else:
            keys = pygame.key.get_pressed()
            self.vehicle.update(keys, dt, self.environment)

        self.sensor_readings = self.lidar.scan(self.vehicle, self.environment)

    def draw_route(self) -> None:
        if len(self.route) >= 2:
            points = [(round(x), round(y)) for x, y in self.route]
            pygame.draw.lines(self.screen, (70, 220, 255), False, points, 5)
            for point in points[1:-1]:
                pygame.draw.circle(self.screen, (245, 245, 245), point, 5)

    def draw_hud(self) -> None:
        obstacles = [
            reading.distance
            for reading in self.sensor_readings
            if reading.hit_type == "obstacle"
        ]
        road_edges = [
            reading.distance
            for reading in self.sensor_readings
            if reading.hit_type == "road_edge"
        ]
        nearest_obstacle = f"{min(obstacles):.0f}px" if obstacles else "none"
        nearest_edge = f"{min(road_edges):.0f}px" if road_edges else "none"

        lines = [
            "PHASE 3: LIDAR ENVIRONMENTAL PERCEPTION",
            "P: autopilot | L: LiDAR rays | WASD / Arrows: manual | R: reset | ESC: quit",
            self.status,
            f"LiDAR: nearest obstacle {nearest_obstacle} | nearest road edge {nearest_edge}",
        ]
        for index, line in enumerate(lines):
            surface = self.font.render(line, True, (245, 245, 245))
            background = pygame.Surface(
                (surface.get_width() + 12, surface.get_height() + 6),
                pygame.SRCALPHA,
            )
            background.fill((20, 25, 30, 185))
            self.screen.blit(background, (12, 12 + index * 29))
            self.screen.blit(surface, (18, 15 + index * 29))

    def run(self) -> None:
        while self.running:
            dt = min(self.clock.tick(60) / 1000.0, 0.05)
            self.handle_events()
            if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                self.running = False

            self.update(dt)
            self.environment.draw(self.screen)
            self.draw_route()
            if self.lidar_enabled:
                self.lidar.draw(self.screen, self.vehicle, self.sensor_readings)
            self.vehicle.draw(self.screen)
            self.draw_hud()
            pygame.display.flip()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Simulation().run()
