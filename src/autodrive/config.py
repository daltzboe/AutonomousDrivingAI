from dataclasses import dataclass
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[2]

@dataclass(frozen=True)
class Settings:
    host: str = os.getenv("CARLA_HOST", "127.0.0.1")
    port: int = int(os.getenv("CARLA_PORT", "2000"))
    timeout: float = float(os.getenv("CARLA_TIMEOUT", "20"))
    image_width: int = 200
    image_height: int = 66
    camera_width: int = 640
    camera_height: int = 360
    camera_fov: float = 90.0
    fixed_delta_seconds: float = 0.05
    target_speed_kmh: float = 25.0
    data_dir: Path = ROOT / "data" / "demonstrations"
    artifacts_dir: Path = ROOT / "artifacts"
    results_dir: Path = ROOT / "results"

SETTINGS = Settings()
