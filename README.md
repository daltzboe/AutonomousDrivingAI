# Autonomous Driving AI Simulation

A group AI project exploring autonomous vehicle navigation and decision-making in a controlled 2D environment.

## Project goal

Build a 2D top-down driving simulator in which an autonomous vehicle can plan a route, respond to obstacles and traffic conditions, and reach a destination. The project starts with a working simulation environment, then adds AI pathfinding and decision-making.

## Technology

- Python
- Pygame for the visual simulation
- NumPy for numerical operations
- A* search for route planning (planned)
- Q-learning as an optional extension (planned)

## Setup on Windows

1. Clone this repository and open the folder in IntelliJ IDEA.
2. Create and activate a virtual environment:

   python -m venv .venv
   .venv\\Scripts\\Activate.ps1

3. Install dependencies:

   python -m pip install -r requirements.txt

4. Run the simulation:

   python main.py

## Phase 1 controls

- WASD or arrow keys: move the test vehicle.
- R: reset the vehicle to its starting position.
- ESC: quit.

Manual movement is temporary and exists only to test the environment. Autonomous navigation will be implemented in a later phase.

## Planned development phases

1. Environment: road layout, vehicle, destination, and obstacles.
2. AI navigation: grid representation and A* pathfinding.
3. Autonomous decisions: obstacle response, traffic signals, and route updates.
4. Learning extension: optional reinforcement learning.
5. Evaluation: success rate, route length, travel time, and collision count.

## Project status

Phase 1 foundation: Pygame application structure, road environment, destination, obstacles, and temporary test-vehicle controls. AI navigation is not implemented yet.
