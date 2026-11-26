"""CARLA 0.9.16 connection helpers; simulator installation stays external."""
import os
import sys
from pathlib import Path

def add_carla_agent_path() -> Path:
    root_value = os.getenv("CARLA_ROOT")
    if not root_value:
        raise RuntimeError(
            "Set CARLA_ROOT to the extracted CARLA 0.9.16 folder "
            "(the directory containing CarlaUE4.exe)."
        )
    root = Path(root_value).expanduser().resolve()
    if not (root / "CarlaUE4.exe").exists():
        raise FileNotFoundError(f"CarlaUE4.exe was not found under CARLA_ROOT: {root}")
    python_api = root / "PythonAPI" / "carla"
    if python_api.exists():
        sys.path.insert(0, str(python_api))
    agents_dir = root / "PythonAPI" / "carla"
    if agents_dir.exists():
        sys.path.insert(0, str(agents_dir))
    return root

def connect():
    add_carla_agent_path()
    try:
        import carla
    except ImportError as exc:
        raise RuntimeError(
            "CARLA Python client is missing. Install the matching 0.9.16 client "
            "inside this Python 3.12 virtual environment."
        ) from exc
    from autodrive.config import SETTINGS
    client = carla.Client(SETTINGS.host, SETTINGS.port)
    client.set_timeout(SETTINGS.timeout)
    world = client.get_world()
    return carla, client, world

def import_basic_agent():
    add_carla_agent_path()
    try:
        from agents.navigation.basic_agent import BasicAgent
    except ImportError as exc:
        raise RuntimeError(
            "Could not import CARLA BasicAgent. Confirm CARLA_ROOT points to "
            "the full 0.9.16 Windows package with PythonAPI/carla/agents."
        ) from exc
    return BasicAgent
