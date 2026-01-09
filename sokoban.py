"""
Sokoban Problem Implementation
"""
from typing import Set, Tuple, List, Dict, FrozenSet
import os

class SokobanState:
    """State representation for Sokoban."""
    
    def __init__(self, boxes: FrozenSet[Tuple[int, int]], 
                 player: Tuple[int, int],
                 walls: FrozenSet[Tuple[int, int]],
                 goals: FrozenSet[Tuple[int, int]]):
        self.boxes = boxes
        self.player = player
        self.walls = walls
        self.goals = goals
    
    def __hash__(self):
        return hash((self.boxes, self.player))
    
    def __eq__(self, other):
        return (self.boxes == other.boxes and 
                self.player == other.player)
    
    def is_goal(self):
        """Check if all boxes are on goals."""
        return self.boxes == self.goals

class SokobanProblem:
    """Sokoban problem for A* solver."""
    
    def __init__(self, level_str: str):
        self.walls, self.boxes, self.player, self.goals = self._parse_level(level_str)
        self.initial_state = SokobanState(
            frozenset(self.boxes),
            self.player,
            frozenset(self.walls),
            frozenset(self.goals)
        )
    
    def _parse_level(self, level_str: str):
        """Parse Sokoban level from string."""
        walls = set()
        boxes = set()
        player = None
        goals = set()
        
        lines = [line.rstrip() for line in level_str.strip().split('\n')]
        
        for r, line in enumerate(lines):
            for c, char in enumerate(line):
                pos = (r, c)
                if char == '#' or char == '🧱' or char == '⬛':  # Wall
                    walls.add(pos)
                elif char == 'B' or char == '$' or char == '📦':  # Box
                    boxes.add(pos)
                elif char == 'G' or char == '.' or char == '⭐' or char == '🎯':  # Goal
                    goals.add(pos)
                elif char == 'P' or char == '@' or char == '🧑' or char == '👷':  # Player
                    player = pos
                elif char == '*':  # Box on goal
                    boxes.add(pos)
                    goals.add(pos)
                elif char == '+':  # Player on goal
                    player = pos
                    goals.add(pos)
        
        return walls, boxes, player, goals
    
    def get_initial_state(self):
        return self.initial_state
    
    def goal_test(self, state):
        return state.is_goal()
    
    def actions(self, state):
        """Return possible actions from current state."""
        possible_actions = []
        directions = [(-1, 0, 'UP'), (1, 0, 'DOWN'), 
                     (0, -1, 'LEFT'), (0, 1, 'RIGHT')]
        
        for dr, dc, action in directions:
            new_player = (state.player[0] + dr, state.player[1] + dc)
            
            # Check wall collision
            if new_player in state.walls:
                continue
            
            # Check box push
            if new_player in state.boxes:
                new_box = (new_player[0] + dr, new_player[1] + dc)
                
                # Can't push into wall or another box
                if new_box in state.walls or new_box in state.boxes:
                    continue
            
            possible_actions.append(action)
        
        return possible_actions
    
    def result(self, state, action):
        """Apply action to state and return new state."""
        dir_map = {
            'UP': (-1, 0),
            'DOWN': (1, 0),
            'LEFT': (0, -1),
            'RIGHT': (0, 1)
        }
        dr, dc = dir_map[action]
        
        new_player = (state.player[0] + dr, state.player[1] + dc)
        new_boxes = set(state.boxes)
        
        # Check if pushing a box
        if new_player in state.boxes:
            new_box = (new_player[0] + dr, new_player[1] + dc)
            new_boxes.remove(new_player)
            new_boxes.add(new_box)
        
        new_state = SokobanState(
            frozenset(new_boxes),
            new_player,
            state.walls,
            state.goals
        )
        
        return new_state, 1.0  # Uniform cost
    
    def display(self, state):
        """Display state in console."""
        # Find bounds
        all_positions = list(state.walls) + list(state.boxes) + list(state.goals) + [state.player]
        rows = [p[0] for p in all_positions]
        cols = [p[1] for p in all_positions]
        
        min_row, max_row = min(rows), max(rows)
        min_col, max_col = min(cols), max(cols)
        
        grid = []
        for r in range(min_row, max_row + 1):
            row = []
            for c in range(min_col, max_col + 1):
                pos = (r, c)
                if pos in state.walls:
                    row.append('#')
                elif pos in state.boxes and pos in state.goals:
                    row.append('*')
                elif pos in state.boxes:
                    row.append('$')
                elif pos in state.goals:
                    row.append('.')
                elif pos == state.player:
                    row.append('@')
                else:
                    row.append(' ')
            grid.append(''.join(row))
        
        return '\n'.join(grid)

def load_level(filename: str) -> str:
    """Load Sokoban level from file."""
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

# Example levels
LEVEL_1 = """
#####
#@$.#
#####
"""

LEVEL_2 = """
#######
#.@   #
# $   #
#     #
#   $.#
#######
"""