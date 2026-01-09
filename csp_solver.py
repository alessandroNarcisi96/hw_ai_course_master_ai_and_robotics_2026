"""
CSP (Constraint Satisfaction Problem) Sokoban solver using OR-Tools CP-SAT.
"""

from dataclasses import dataclass
from typing import Dict
import time
from ortools.sat.python import cp_model


@dataclass
class CSPMetrics:
    total_time: float = 0.0
    encoding_time: float = 0.0
    solving_time: float = 0.0
    num_variables: int = 0
    success: bool = False
    timeout: bool = False
    solution_length: int = 0


class CSPSolver:

    def solve_sokoban(self, problem, max_steps=20, timeout=30.0):
        metrics = CSPMetrics()
        start = time.perf_counter()

        model, var = self._encode(problem, max_steps)
        metrics.encoding_time = time.perf_counter() - start
        metrics.num_variables = len(var)

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = timeout
        solver.parameters.optimize_with_core = True

        solve_start = time.perf_counter()
        status = solver.Solve(model)
        metrics.solving_time = time.perf_counter() - solve_start
        metrics.total_time = time.perf_counter() - start

        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            metrics.success = True
            plan = self._extract_actions(solver, var, max_steps)
            metrics.solution_length = len(plan)
            return plan, metrics

        if status == cp_model.UNKNOWN:
            metrics.timeout = True

        return None, metrics

    # ---------------------------------------------------------

    def _encode(self, problem, max_steps):
        model = cp_model.CpModel()
        var: Dict[str, cp_model.IntVar] = {}

        init = problem.initial_state
        walls = set(init.walls)
        goals = list(init.goals)
        boxes = list(init.boxes)
        player_start = init.player

        all_pos = walls | set(goals) | set(boxes) | {player_start}
        xs = [x for x, _ in all_pos]
        ys = [y for _, y in all_pos]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        n_boxes = len(boxes)

        # ---------------- VARIABLES ----------------

        for t in range(max_steps + 1):
            var[f'px_{t}'] = model.NewIntVar(min_x, max_x, f'px_{t}')
            var[f'py_{t}'] = model.NewIntVar(min_y, max_y, f'py_{t}')
            for i in range(n_boxes):
                var[f'bx_{i}_{t}'] = model.NewIntVar(min_x, max_x, f'bx_{i}_{t}')
                var[f'by_{i}_{t}'] = model.NewIntVar(min_y, max_y, f'by_{i}_{t}')

        for t in range(max_steps):
            var[f'action_{t}'] = model.NewIntVar(0, 4, f'action_{t}')

        # ---------------- INITIAL ----------------

        model.Add(var['px_0'] == player_start[0])
        model.Add(var['py_0'] == player_start[1])

        for i, (bx, by) in enumerate(boxes):
            model.Add(var[f'bx_{i}_0'] == bx)
            model.Add(var[f'by_{i}_0'] == by)

        # ---------------- HELPERS ----------------

        def forbid(xv, yv, x, y):
            bx = model.NewBoolVar('')
            by = model.NewBoolVar('')
            model.Add(xv == x).OnlyEnforceIf(bx)
            model.Add(xv != x).OnlyEnforceIf(bx.Not())
            model.Add(yv == y).OnlyEnforceIf(by)
            model.Add(yv != y).OnlyEnforceIf(by.Not())
            model.AddBoolOr([bx.Not(), by.Not()])

        # ---------------- STATIC ----------------

        for t in range(max_steps + 1):
            for wx, wy in walls:
                forbid(var[f'px_{t}'], var[f'py_{t}'], wx, wy)
                for i in range(n_boxes):
                    forbid(var[f'bx_{i}_{t}'], var[f'by_{i}_{t}'], wx, wy)

        # ---------------- DYNAMICS ----------------

        moves = {
            0: (-1, 0),
            1: (1, 0),
            2: (0, -1),
            3: (0, 1),
            4: (0, 0),
        }

        move_costs = []

        for t in range(max_steps):
            px, py = var[f'px_{t}'], var[f'py_{t}']
            pxn, pyn = var[f'px_{t+1}'], var[f'py_{t+1}']
            act = var[f'action_{t}']

            # Player move
            for a, (dx, dy) in moves.items():
                b = model.NewBoolVar('')
                model.Add(act == a).OnlyEnforceIf(b)
                model.Add(act != a).OnlyEnforceIf(b.Not())
                model.Add(pxn == px + dx).OnlyEnforceIf(b)
                model.Add(pyn == py + dy).OnlyEnforceIf(b)

            pushes = []

            for i in range(n_boxes):
                bx, by = var[f'bx_{i}_{t}'], var[f'by_{i}_{t}']
                bxn, byn = var[f'bx_{i}_{t+1}'], var[f'by_{i}_{t+1}']

                pushed = model.NewBoolVar('')
                pushes.append(pushed)

                # If pushed, action cannot be NONE
                model.Add(act != 4).OnlyEnforceIf(pushed)

                # By default (not pushed) the box stays in place
                model.Add(bxn == bx).OnlyEnforceIf(pushed.Not())
                model.Add(byn == by).OnlyEnforceIf(pushed.Not())

                # If pushed and a specific action is chosen, enforce that:
                # - the player was adjacent in the correct direction (player + move == box)
                # - the box moves in the same direction
                for a, (dxm, dym) in moves.items():
                    if a == 4:
                        continue
                    ba = model.NewBoolVar('')
                    model.Add(act == a).OnlyEnforceIf(ba)
                    model.Add(act != a).OnlyEnforceIf(ba.Not())
                    model.Add(bxn == bx + dxm).OnlyEnforceIf([pushed, ba])
                    model.Add(byn == by + dym).OnlyEnforceIf([pushed, ba])
                    model.Add(px + dxm == bx).OnlyEnforceIf([pushed, ba])
                    model.Add(py + dym == by).OnlyEnforceIf([pushed, ba])

                # If pushed, player next must equal the box current (redundant but safe)
                model.Add(pxn == bx).OnlyEnforceIf(pushed)
                model.Add(pyn == by).OnlyEnforceIf(pushed)

            model.Add(sum(pushes) <= 1)

            m = model.NewBoolVar('')
            model.Add(act != 4).OnlyEnforceIf(m)
            model.Add(act == 4).OnlyEnforceIf(m.Not())
            move_costs.append(m)

        # ---------------- GOAL ----------------

        for gx, gy in goals:
            goal_filled = []
            for i in range(n_boxes):
                b = model.NewBoolVar('')
                model.Add(var[f'bx_{i}_{max_steps}'] == gx).OnlyEnforceIf(b)
                model.Add(var[f'by_{i}_{max_steps}'] == gy).OnlyEnforceIf(b)
                goal_filled.append(b)
            model.Add(sum(goal_filled) == 1)

        # ---------------- OBJECTIVE ----------------

        model.Minimize(sum(move_costs))

        return model, var

    # ---------------------------------------------------------

    def _extract_actions(self, solver, var, max_steps):
        names = ['UP', 'DOWN', 'LEFT', 'RIGHT', 'NONE']
        plan = []
        for t in range(max_steps):
            a = solver.Value(var[f'action_{t}'])
            if a != 4:
                plan.append(names[a])
        return plan
