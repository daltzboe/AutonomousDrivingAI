"""Evaluate BasicAgent and the trained imitation model on CARLA episodes."""
import argparse
import csv
import queue
import random
from autodrive.carla_support import connect, import_basic_agent
from autodrive.config import SETTINGS
from autodrive.metrics import summarize_episodes
from autodrive.model import SteeringCNN
import numpy as np
import torch
from PIL import Image

def run_episode(mode, episode, max_steps, carla, world, BasicAgent, model, device):
    spawn_points = world.get_map().get_spawn_points()
    start, destination = random.sample(spawn_points, 2)
    blueprint = world.get_blueprint_library().filter("vehicle.*")[0]
    vehicle = world.try_spawn_actor(blueprint, start)
    if vehicle is None:
        raise RuntimeError(f"{mode} episode {episode}: spawn failed (count as failed run in report)")
    actors = [vehicle]
    collisions = []
    collision_bp = world.get_blueprint_library().find("sensor.other.collision")
    collision = world.spawn_actor(collision_bp, carla.Transform(), attach_to=vehicle)
    collision.listen(lambda event: collisions.append(event))
    actors.append(collision)
    camera_bp = world.get_blueprint_library().find("sensor.camera.rgb")
    camera_bp.set_attribute("image_size_x", str(SETTINGS.camera_width))
    camera_bp.set_attribute("image_size_y", str(SETTINGS.camera_height))
    camera_bp.set_attribute("fov", str(SETTINGS.camera_fov))
    camera_bp.set_attribute("sensor_tick", str(SETTINGS.fixed_delta_seconds))
    images = queue.Queue(maxsize=8)
    camera = world.spawn_actor(camera_bp, carla.Transform(carla.Location(x=1.5, z=2.4)), attach_to=vehicle)
    camera.listen(lambda image: images.put(image) if not images.full() else None)
    actors.append(camera)
    agent = BasicAgent(vehicle, target_speed=SETTINGS.target_speed_kmh) if mode == "basic_agent" else None
    if agent:
        agent.set_destination(destination.location)
    lane_errors, travelled = [], 0.0
    previous = vehicle.get_location()
    completed, steps = False, 0
    try:
        for steps in range(1, max_steps + 1):
            if agent:
                control = agent.run_step()
            else:
                image = images.get(timeout=3)
                rgb = np.frombuffer(image.raw_data, dtype=np.uint8).reshape(
                    (image.height, image.width, 4))[:, :, :3][:, :, ::-1].copy()
                pil = Image.fromarray(rgb).resize((200, 66))
                tensor = torch.from_numpy(np.asarray(pil, dtype=np.float32) / 255).permute(
                    2, 0, 1).unsqueeze(0).to(device)
                with torch.no_grad():
                    steering = float(model(tensor).item())
                control = carla.VehicleControl(
                    steer=max(-1.0, min(1.0, steering)), throttle=0.35, brake=0.0)
            vehicle.apply_control(control)
            world.tick()
            current = vehicle.get_location()
            travelled += previous.distance(current)
            previous = current
            waypoint = world.get_map().get_waypoint(
                current, project_to_road=True, lane_type=carla.LaneType.Driving)
            if waypoint:
                center = waypoint.transform.location
                lane_errors.append(((current.x-center.x)**2 + (current.y-center.y)**2)**0.5)
            if current.distance(destination.location) < 4.0:
                completed = True
                break
    finally:
        for actor in actors:
            if actor.is_alive:
                actor.destroy()
    return {"controller": mode, "episode": episode, "collision": bool(collisions),
            "lane_deviation_m": sum(lane_errors)/len(lane_errors) if lane_errors else 0.0,
            "route_completed": completed, "steps": steps, "distance_travelled_m": travelled}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=5)
    parser.add_argument("--max-steps", type=int, default=2500)
    parser.add_argument("--seed", type=int, default=1000)
    args = parser.parse_args()
    if args.episodes < 1 or args.max_steps < 1:
        parser.error("Episodes and max steps must be positive.")
    carla, client, world = connect()
    BasicAgent = import_basic_agent()
    checkpoint = torch.load(SETTINGS.artifacts_dir / "steering_cnn.pth",
                            map_location="cpu", weights_only=False)
    model = SteeringCNN()
    model.load_state_dict(checkpoint["model_state_dict"])
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device).eval()
    old = world.get_settings()
    results = []
    try:
        settings = world.get_settings()
        settings.synchronous_mode = True
        settings.fixed_delta_seconds = SETTINGS.fixed_delta_seconds
        world.apply_settings(settings)
        for episode in range(args.episodes):
            # Identical route draw for both controllers (same seed per episode).
            for mode in ("basic_agent", "imitation_cnn"):
                random.seed(args.seed + episode)
                results.append(run_episode(mode, episode, args.max_steps, carla,
                                          world, BasicAgent, model, device))
                print(results[-1])
    finally:
        world.apply_settings(old)
    SETTINGS.results_dir.mkdir(parents=True, exist_ok=True)
    raw_path = SETTINGS.results_dir / "episodes.csv"
    with raw_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    summaries = []
    for mode in ("basic_agent", "imitation_cnn"):
        summary = {"controller": mode, **summarize_episodes(
            [r for r in results if r["controller"] == mode])}
        summaries.append(summary)
        print(summary)
    with (SETTINGS.results_dir / "summary.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=summaries[0].keys())
        writer.writeheader()
        writer.writerows(summaries)
    print(f"Raw episodes: {raw_path}")
    print(f"Aggregated comparison: {SETTINGS.results_dir / 'summary.csv'}")

if __name__ == "__main__":
    main()
