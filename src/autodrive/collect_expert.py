"""Record synchronized RGB frames and BasicAgent control labels."""
import argparse
import csv
import json
import queue
import random
from datetime import datetime, timezone

from autodrive.carla_support import connect, import_basic_agent
from autodrive.config import SETTINGS

def collect(episodes: int, max_steps: int, seed: int):
    random.seed(seed)
    carla, client, world = connect()
    BasicAgent = import_basic_agent()
    original = world.get_settings()
    saved_actors = []
    SETTINGS.data_dir.mkdir(parents=True, exist_ok=True)
    metadata = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "carla_server_map": world.get_map().name,
        "seed": seed, "requested_episodes": episodes, "max_steps": max_steps,
        "fixed_delta_seconds": SETTINGS.fixed_delta_seconds,
        "camera": {"width": SETTINGS.camera_width, "height": SETTINGS.camera_height,
                   "fov_degrees": SETTINGS.camera_fov, "encoding": "RGB"},
        "expert": "CARLA BasicAgent",
    }
    try:
        settings = world.get_settings()
        settings.synchronous_mode = True
        settings.fixed_delta_seconds = SETTINGS.fixed_delta_seconds
        world.apply_settings(settings)
        blueprints = world.get_blueprint_library()
        vehicle_bp = blueprints.filter("vehicle.*")[0]
        camera_bp = blueprints.find("sensor.camera.rgb")
        camera_bp.set_attribute("image_size_x", str(SETTINGS.camera_width))
        camera_bp.set_attribute("image_size_y", str(SETTINGS.camera_height))
        camera_bp.set_attribute("fov", str(SETTINGS.camera_fov))
        camera_bp.set_attribute("sensor_tick", str(SETTINGS.fixed_delta_seconds))
        metadata["routes"] = []
        with (SETTINGS.data_dir / "labels.csv").open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=[
                "episode", "step", "image_path", "steering", "throttle", "brake",
                "speed_mps", "x", "y", "yaw"
            ])
            writer.writeheader()
            for episode in range(episodes):
                points = world.get_map().get_spawn_points()
                if len(points) < 2:
                    raise RuntimeError("CARLA map needs at least two vehicle spawn points.")
                start, destination = random.sample(points, 2)
                metadata["routes"].append({
                    "episode": episode,
                    "start": [start.location.x, start.location.y, start.location.z],
                    "destination": [destination.location.x, destination.location.y, destination.location.z],
                })
                vehicle = world.try_spawn_actor(vehicle_bp, start)
                if vehicle is None:
                    print(f"Episode {episode}: vehicle spawn failed; logged in metadata.")
                    continue
                saved_actors.append(vehicle)
                agent = BasicAgent(vehicle, target_speed=SETTINGS.target_speed_kmh)
                agent.set_destination(destination.location)
                image_queue = queue.Queue(maxsize=8)
                camera = world.spawn_actor(camera_bp, carla.Transform(
                    carla.Location(x=1.5, z=2.4)), attach_to=vehicle)
                saved_actors.append(camera)
                camera.listen(lambda image: image_queue.put(image) if not image_queue.full() else None)
                episode_dir = SETTINGS.data_dir / f"episode_{episode:03d}"
                episode_dir.mkdir(parents=True, exist_ok=True)
                for step in range(max_steps):
                    control = agent.run_step()
                    vehicle.apply_control(control)
                    frame = world.tick()
                    try:
                        image = image_queue.get(timeout=3)
                        while image.frame < frame:
                            image = image_queue.get(timeout=3)
                    except queue.Empty as exc:
                        raise RuntimeError(f"Camera timeout at episode {episode}, step {step}") from exc
                    image_path = episode_dir / f"{step:06d}.png"
                    image.save_to_disk(str(image_path), carla.ColorConverter.Raw)
                    transform = vehicle.get_transform()
                    velocity = vehicle.get_velocity()
                    speed = (velocity.x**2 + velocity.y**2 + velocity.z**2) ** 0.5
                    writer.writerow({
                        "episode": episode, "step": step,
                        "image_path": str(image_path.relative_to(SETTINGS.data_dir)).replace("\\", "/"),
                        "steering": control.steer, "throttle": control.throttle,
                        "brake": control.brake, "speed_mps": speed,
                        "x": transform.location.x, "y": transform.location.y,
                        "yaw": transform.rotation.yaw
                    })
                    if vehicle.get_location().distance(destination.location) < 4.0:
                        break
                camera.stop()
                camera.destroy()
                saved_actors.remove(camera)
                vehicle.destroy()
                saved_actors.remove(vehicle)
                print(f"Episode {episode}: recorded {step + 1} frames.")
    finally:
        for actor in reversed(saved_actors):
            if actor.is_alive:
                actor.destroy()
        world.apply_settings(original)
    (SETTINGS.data_dir / "run_metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Demonstrations saved to {SETTINGS.data_dir}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=5)
    parser.add_argument("--max-steps", type=int, default=2500)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if args.episodes < 2 or args.max_steps < 1:
        parser.error("Use at least 2 episodes and a positive --max-steps value.")
    collect(args.episodes, args.max_steps, args.seed)

if __name__ == "__main__":
    main()
