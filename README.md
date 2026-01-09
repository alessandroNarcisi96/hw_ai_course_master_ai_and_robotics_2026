# Sokoban Solver - AI Homework Project

Short description
-----------------
This project implements and evaluates two approaches for solving Sokoban puzzles:

- An A* search solver with multiple heuristics (Manhattan, box-count, matching).
- A CSP-based solver encoded for OR-Tools CP-SAT that models player/box positions
  across timesteps and minimizes the number of player moves.

The repository includes level parsing, solver implementations, an experiment runner,
and scripts to reproduce results and generate plots.

In the folder /levels there are the experiments to submit.
If you want to perform more experiments,it is enough to add new .txt files according to the expected format: '#' for the walls,'@' for the player,'$' for the box,'.' for the goal

How to run
----------
Prerequisites: Python 3.8 or later.

1. Create a virtual environment (recommended):

```powershell
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run the full experiment suite:

```powershell
python run_experiment.py
```
4. The script will create the folder ./result with the output for each level submitted

Dependencies
------------
Install packages via `requirements.txt`:

```
numpy>=1.21.0
matplotlib>=3.5.0
pandas>=1.3.0
ortools>=9.0.0
colorama>=0.4.4
pytest>=7.0.0
```

Notes
-----
- If `ortools` is not installed, the CSP experiments will be skipped or will
  report that the solver is not available.
- Use the `levels/` folder to add or edit test levels (.txt). The runner will
  detect and use existing `.txt` files.

Contact
-------
For questions about the implementation, see the source files in the repository.



