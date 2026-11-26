from statistics import mean

def steering_mae(predictions, targets) -> float:
    if len(predictions) != len(targets) or not targets:
        raise ValueError("Predictions and targets must be non-empty and equal length.")
    return sum(abs(float(p) - float(t)) for p, t in zip(predictions, targets)) / len(targets)

def summarize_episodes(episodes: list[dict]) -> dict:
    if not episodes:
        raise ValueError("Cannot summarize an empty episode list.")
    return {
        "episodes": len(episodes),
        "collision_rate_percent": 100.0 * sum(bool(e["collision"]) for e in episodes) / len(episodes),
        "mean_lane_deviation_m": mean(float(e["lane_deviation_m"]) for e in episodes),
        "route_completion_percent": 100.0 * sum(bool(e["route_completed"]) for e in episodes) / len(episodes),
        "mean_steps": mean(float(e["steps"]) for e in episodes),
    }
