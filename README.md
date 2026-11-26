# Autonomous Driving AI Simulation

A 2D top-down driving simulator for experimenting with autonomous vehicle navigation and decision-making in a controlled environment.

## Project goal

Build a simulated vehicle that can perceive its surroundings, plan a route, respond to obstacles, and reach a destination. The project is developed in phases, starting with a working Pygame environment and progressing toward more advanced autonomous-driving behavior.

## Technology

- Python 3.13
- Pygame for the visual simulation
- NumPy for numerical operations and future AI components
- A* search for grid-based route planning
- Simulated LiDAR ray casting for environmental perception
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
- **L**: show or hide LiDAR sensor rays.
- **WASD / Arrow keys**: drive manually when autopilot is off.
- **R**: reset the vehicle to the starting position.
- **ESC**: quit.

## LiDAR visualization

The simulated LiDAR casts 24 rays around the vehicle, spaced 15 degrees apart, with a maximum range of 240 pixels.

- **Red rays**: an obstacle was detected.
- **Yellow rays**: a road boundary was detected.
- **Green rays**: no object or road boundary was detected within sensor range.

The HUD reports the nearest detected obstacle and road edge. The sensor readings are refreshed as the vehicle moves.

## Development phases

1. **Simulation environment:** road layout, vehicle, destination, obstacles, and manual controls.
2. **A* autonomous navigation:** grid-based route planning, obstacle-aware waypoints, and vehicle steering.
3. **Environmental perception:** simulated LiDAR, obstacle-distance readings, and road-boundary detection. The next milestone is using perception data to influence driving decisions.
4. **Learning extension:** optional reinforcement learning and model training.
5. **Evaluation:** success rate, route length, travel time, and collision count.

## Current status

Phases 1 and 2 are implemented. The first Phase 3 perception milestone adds a 24-ray LiDAR sensor. Press **L** to show or hide its rays and **P** to run the A* autopilot. Manual driving remains available when autopilot is off.
