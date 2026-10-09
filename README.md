# Simulation of a game Mr Jack
An engineering thesis project implementing a simulation of the board game **Mr. Jack**, where both players are controlled by computer algorithms. The project evaluates and compares the computational complexity, memory usage, and performance between heuristic-based decision-making and random gameplay.

## Project Overview & Architecture
The project consists of two core components designed for different purposes:
- **Simulation Module**: Runs automated games without graphical rendering to measure computational complexity. It records execution metrics, memory consumption, and operation counts, exporting the results to Excel files for performance analysis.
- **Visual Module**: Provides a graphical interface allowing users to step through the gameplay interactively by pressing the spacebar, making it easy to observe map states, character positions, and turn-by-turn changes.

## Gameplay Modes
- **Heuristic Gameplay**: Players utilize logical heuristic rules to make optimal or near-optimal moves.
- **Random Gameplay**: Players execute completely random actions. 
- **Comparative Analysis**: Designed to contrast the computational overhead, resource usage, and complexity differences between intelligent heuristic choices and random actions.

## Technologies Used
- **Language**: Python
- **Data Export**: Excel spreadsheets for metrics tracking (memory and operation counts)
- **Visualization**: PyGame
  
Example look of the board:
<img width="1625" height="916" alt="image" src="https://github.com/user-attachments/assets/d49457d1-2e59-4eca-bb47-e1d67762436c" />


