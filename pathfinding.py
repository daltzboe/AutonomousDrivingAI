"""A* grid planner for the 2D driving environment."""

from heapq import heappop, heappush
from itertools import count

import pygame


class AStarPlanner:
    """Finds a collision-free route through the road grid using A*."""

    CELL_SIZE = 20
    # A square footprint is deliberately conservative for a rotating vehicle.
    VEHICLE_CLEARANCE = 54

    def __init__(self, environment) -> None:
        self.environment = environment
        self.columns = (environment.WIDTH + self.CELL_SIZE - 1) // self.CELL_SIZE
        self.rows = (environment.HEIGHT + self.CELL_SIZE - 1) // self.CELL_SIZE

    def _cell_from_position(self, position: tuple[float, float]) -> tuple[int, int]:
        x, y = position
        column = round((x - self.CELL_SIZE / 2) / self.CELL_SIZE)
        row = round((y - self.CELL_SIZE / 2) / self.CELL_SIZE)
        return column, row

    def _position_from_cell(self, cell: tuple[int, int]) -> tuple[int, int]:
        column, row = cell
        return (
            column * self.CELL_SIZE + self.CELL_SIZE // 2,
            row * self.CELL_SIZE + self.CELL_SIZE // 2,
        )

    def _is_valid(self, cell: tuple[int, int]) -> bool:
        column, row = cell
        if not (0 <= column < self.columns and 0 <= row < self.rows):
            return False

        candidate = pygame.Rect(
            0, 0, self.VEHICLE_CLEARANCE, self.VEHICLE_CLEARANCE
        )
        candidate.center = self._position_from_cell(cell)
        return (
            self.environment.is_drivable(candidate)
            and not self.environment.hits_obstacle(candidate)
        )

    @staticmethod
    def _heuristic(first: tuple[int, int], second: tuple[int, int]) -> int:
        return abs(first[0] - second[0]) + abs(first[1] - second[1])

    def find_path(
        self,
        start: tuple[float, float],
        goal: tuple[float, float],
    ) -> list[tuple[float, float]]:
        """Return turn-by-turn world-coordinate waypoints, or [] if blocked."""
        start_cell = self._cell_from_position(start)
        goal_cell = self._cell_from_position(goal)

        if not self._is_valid(start_cell) or not self._is_valid(goal_cell):
            return []

        sequence = count()
        frontier = [(0, next(sequence), start_cell)]
        came_from = {start_cell: None}
        cost_so_far = {start_cell: 0}

        while frontier:
            _, _, current = heappop(frontier)
            if current == goal_cell:
                break

            neighbors = (
                (current[0] + 1, current[1]),
                (current[0] - 1, current[1]),
                (current[0], current[1] + 1),
                (current[0], current[1] - 1),
            )

            for neighbor in neighbors:
                if not self._is_valid(neighbor):
                    continue

                new_cost = cost_so_far[current] + 1
                if new_cost >= cost_so_far.get(neighbor, float("inf")):
                    continue

                cost_so_far[neighbor] = new_cost
                came_from[neighbor] = current
                priority = new_cost + self._heuristic(neighbor, goal_cell)
                heappush(frontier, (priority, next(sequence), neighbor))

        if goal_cell not in came_from:
            return []

        cells = []
        current = goal_cell
        while current is not None:
            cells.append(current)
            current = came_from[current]
        cells.reverse()

        # Keep only corners so the vehicle follows clean straight segments.
        waypoints: list[tuple[float, float]] = [start]
        for index in range(1, len(cells) - 1):
            previous = cells[index - 1]
            current = cells[index]
            following = cells[index + 1]
            incoming = (current[0] - previous[0], current[1] - previous[1])
            outgoing = (following[0] - current[0], following[1] - current[1])
            if incoming != outgoing:
                waypoints.append(self._position_from_cell(current))

        waypoints.append(goal)
        return waypoints
