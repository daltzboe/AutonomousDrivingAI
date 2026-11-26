"""Simulated 2D LiDAR sensor for detecting obstacles and road boundaries."""

from dataclasses import dataclass
import math

import pygame


@dataclass(frozen=True)
class SensorReading:
    """One LiDAR ray and the first thing it detects."""

    angle: float
    distance: float
    hit_type: str
    end_point: tuple[float, float]


class LidarSensor:
    """Cast evenly spaced rays around a vehicle and measure nearby objects."""

    RANGE = 240.0
    ANGLE_STEP = 15
    STEP_SIZE = 4.0

    OBSTACLE_COLOR = (255, 90, 65)
    ROAD_EDGE_COLOR = (255, 210, 70)
    CLEAR_COLOR = (90, 220, 150)

    def scan(self, vehicle, environment) -> list[SensorReading]:
        readings = []
        origin_x = vehicle.x
        origin_y = vehicle.y

        for relative_angle in range(0, 360, self.ANGLE_STEP):
            angle = vehicle.angle + relative_angle
            radians = math.radians(angle)
            direction_x = math.sin(radians)
            direction_y = -math.cos(radians)
            distance = self.RANGE
            hit_type = "clear"

            for step in range(
                int(self.STEP_SIZE),
                int(self.RANGE) + 1,
                int(self.STEP_SIZE),
            ):
                x = origin_x + direction_x * step
                y = origin_y + direction_y * step
                point = (round(x), round(y))

                if any(obstacle.collidepoint(point) for obstacle in environment.obstacles):
                    distance = float(step)
                    hit_type = "obstacle"
                    break

                if not any(road.collidepoint(point) for road in environment.road_rects):
                    distance = float(step)
                    hit_type = "road_edge"
                    break

            end_point = (
                origin_x + direction_x * distance,
                origin_y + direction_y * distance,
            )
            readings.append(
                SensorReading(relative_angle, distance, hit_type, end_point)
            )

        return readings

    def draw(
        self,
        surface: pygame.Surface,
        vehicle,
        readings: list[SensorReading],
    ) -> None:
        """Draw sensor rays; obstacle and road-edge hits use different colors."""
        origin = (round(vehicle.x), round(vehicle.y))

        for reading in readings:
            if reading.hit_type == "obstacle":
                color = self.OBSTACLE_COLOR
            elif reading.hit_type == "road_edge":
                color = self.ROAD_EDGE_COLOR
            else:
                color = self.CLEAR_COLOR

            endpoint = (round(reading.end_point[0]), round(reading.end_point[1]))
            pygame.draw.line(surface, color, origin, endpoint, 1)

            if reading.hit_type != "clear":
                pygame.draw.circle(surface, color, endpoint, 3)
