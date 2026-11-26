import pytest
from autodrive.metrics import steering_mae, summarize_episodes

def test_steering_mae():
    assert steering_mae([0.0, 0.5, -0.5], [0.1, 0.4, -0.25]) == pytest.approx(0.15)

def test_episode_metrics():
    rows = [
        {"collision": False, "lane_deviation_m": 0.2, "route_completed": True, "steps": 100},
        {"collision": True, "lane_deviation_m": 0.4, "route_completed": False, "steps": 200},
    ]
    summary = summarize_episodes(rows)
    assert summary["collision_rate_percent"] == 50
    assert summary["mean_lane_deviation_m"] == pytest.approx(0.3)
    assert summary["route_completion_percent"] == 50

def test_empty_mae_rejected():
    with pytest.raises(ValueError):
        steering_mae([], [])
