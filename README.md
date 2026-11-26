# Autonomous Driving AI Simulation

A 2D top-down driving simulator for experimenting with autonomous vehicle navigation and decision-making in a controlled environment.

## Project goal

Build a simulated vehicle that can plan a route, avoid obstacles, and reach a destination. The project is developed in phases, starting with a working Pygame environment and progressing toward more advanced autonomous-driving behavior.

## Technology

- Python 3.13
- Pygame for the visual simulation
- NumPy for numerical operations and future AI components
- A* search for grid-based route planning
- Q-learning as a possible future extension

## Setup on Windows

This project has been tested with Python 3.13.17.

1. Open the repository folder in IntelliJ IDEA.
2. Create and activate a virtual environment:

   ```powershell
   py -3.13 -m venv .venv313
   .\.venv313\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

4. Run the simulation:

   ```powershell
   python main.py
   ```

## Controls

- **P**: start or pause A* autopilot.
- **WASD / Arrow keys**: drive manually when autopilot is off.
- **R**: reset the vehicle to the starting position.
- **ESC**: quit.

## Development phases

1. **Simulation environment:** road layout, vehicle, destination, obstacles, and manual controls.
2. **A* autonomous navigation:** grid-based route planning, obstacle-aware waypoints, and vehicle steering.
3. **Autonomous decisions:** sensor simulation, obstacle response, traffic signals, and route updates.
4. **Learning extension:** optional reinforcement learning and model training.
5. **Evaluation:** success rate, route length, travel time, and collision count.

## Current status

Phase 1 and the first Phase 2 milestone are implemented. Press **P** to have the vehicle calculate and follow an A* route from its current position to the destination. Manual driving remains available when autopilot is paused.
