"""
Heuristic functions for Sokoban A* search.
"""

def manhattan_distance(pos1, pos2):
    """Calculate Manhattan distance between two positions."""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def manhattan_heuristic(state, goals):
    """
    Sum of Manhattan distances from each box to nearest goal.
    Admissible but not very informed.
    """
    boxes = state.boxes
    total = 0
    
    for box in boxes:
        min_dist = float('inf')
        for goal in goals:
            dist = manhattan_distance(box, goal)
            if dist < min_dist:
                min_dist = dist
        total += min_dist
    
    return total

def simple_count_heuristic(state, goals):
    """
    Count boxes not on goals.
    Very fast but not very informed.
    """
    return len([b for b in state.boxes if b not in goals])

def minimum_matching_heuristic(state, goals):
    """
    Minimum matching distance between boxes and goals.
    More informed than simple Manhattan.
    """
    boxes = list(state.boxes)
    goals_list = list(goals)
    
    if not boxes:
        return 0
    
    # Simple greedy matching (admissible but not optimal)
    total = 0
    used_goals = set()
    
    for box in boxes:
        best_dist = float('inf')
        best_goal = None
        
        for goal in goals_list:
            if goal in used_goals:
                continue
            dist = manhattan_distance(box, goal)
            if dist < best_dist:
                best_dist = dist
                best_goal = goal
        
        if best_goal:
            used_goals.add(best_goal)
            total += best_dist
    
    return total

def create_heuristic(heuristic_name, goals):
    """Create heuristic function by name."""
    def heuristic(state):
        if heuristic_name == "manhattan":
            return manhattan_heuristic(state, goals)
        elif heuristic_name == "count":
            return simple_count_heuristic(state, goals)
        elif heuristic_name == "matching":
            return minimum_matching_heuristic(state, goals)
        else:
            raise ValueError(f"Unknown heuristic: {heuristic_name}")
    
    return heuristic