"""Pygame application loop for the driving simulation."""

import sys
import pygame

from environment import Environment
from vehicle import Vehicle


class Simulation:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Autonomous Driving AI | Phase 1")
        self.screen = pygame.display.set_mode((Environment.WIDTH, Environment.HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 18)
        self.environment = Environment()
        self.vehicle = Vehicle(*self.environment.start_position)
        self.running = True

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.vehicle.reset(*self.environment.start_position)

    def update(self, dt: float) -> None:
        # Temporary manual controls let us test the environment before AI navigation.
        keys = pygame.key.get_pressed()
        self.vehicle.update(keys, dt, self.environment)

    def draw_hud(self) -> None:
        lines = [
            "PHASE 1: SIMULATION ENVIRONMENT",
            "WASD / Arrow keys: move test vehicle | R: reset | ESC: quit",
            "AI navigation will be added in Phase 2.",
        ]
        for index, line in enumerate(lines):
            surface = self.font.render(line, True, (245, 245, 245))
            self.screen.blit(surface, (18, 16 + index * 25))

    def run(self) -> None:
        while self.running:
            dt = min(self.clock.tick(60) / 1000.0, 0.05)
            self.handle_events()
            if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                self.running = False
            self.update(dt)
            self.environment.draw(self.screen)
            self.vehicle.draw(self.screen)
            self.draw_hud()
            pygame.display.flip()

        pygame.quit()
        sys.exit()
