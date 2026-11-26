import os
import sys

def main():
    print(f"Python: {sys.version.split()[0]}")
    print(f"CARLA_ROOT: {os.getenv('CARLA_ROOT', '(not set)')}")
    try:
        import torch
        print(f"PyTorch: {torch.__version__}; CUDA available: {torch.cuda.is_available()}")
    except ImportError:
        print("PyTorch: NOT INSTALLED")
    try:
        from autodrive.carla_support import connect, import_basic_agent
        carla, client, world = connect()
        BasicAgent = import_basic_agent()
        print(f"CARLA client: {getattr(carla, '__version__', 'version not exposed')}")
        print(f"Server map: {world.get_map().name}")
        print(f"BasicAgent: import OK ({BasicAgent.__name__})")
    except Exception as exc:
        print(f"CARLA check failed: {exc}")
        raise SystemExit(1)

if __name__ == "__main__":
    main()
