"""
A* Search Implementation
"""
import heapq
import time
from typing import Any, List, Tuple, Dict, Set, Optional, Callable
from dataclasses import dataclass, asdict
import json

@dataclass
class AStarMetrics:
    """Metrics collected during A* search."""
    nodes_expanded: int = 0
    nodes_generated: int = 0
    max_frontier_size: int = 0
    max_memory_nodes: int = 0
    total_time: float = 0.0
    solution_length: int = 0
    success: bool = False
    timeout: bool = False
    avg_branching_factor: float = 0.0

class Node:
    """Search tree node."""
    def __init__(self, state, parent=None, action=None, cost=0.0):
        self.state = state
        self.parent = parent
        self.action = action
        self.g = cost  # path cost
        if parent:
            self.g += parent.g
    
    def __lt__(self, other):
        return self.g < other.g

class AStarSolver:
    """A* solver"""
    
    def __init__(self, heuristic_func: Callable):
        self.heuristic = heuristic_func
        self.metrics = AStarMetrics()
    
    def solve(self, problem, timeout: float = 30.0) -> Tuple[Optional[List], Optional[List], AStarMetrics]:
        """
        A* search as per Slide 32 pseudocode.
        
        Args:
            problem: Problem instance with methods:
                - get_initial_state()
                - goal_test(state)
                - actions(state)
                - result(state, action) -> (new_state, cost)
            timeout: Maximum search time in seconds
        
        Returns:
            (solution_path, solution_actions, metrics)
        """
        start_time = time.time()
        
        # Initialize as per pseudocode
        initial_state = problem.get_initial_state()
        initial_node = Node(initial_state)
        
        # Frontier: priority queue ordered by f = g + h
        frontier = []
        initial_f = self._f(initial_node, problem)
        heapq.heappush(frontier, (initial_f, initial_node))
        
        # Track states in frontier for duplicate checking
        frontier_states = {initial_state: (initial_node.g, initial_f)}
        
        explored = set()  # Set of explored states (no reopening!)
        
        self.metrics.nodes_generated = 1
        self.metrics.max_frontier_size = 1
        self.metrics.max_memory_nodes = 1
        branching_factors = []
        
        while frontier:
            # Check timeout
            if time.time() - start_time > timeout:
                self.metrics.timeout = True
                self.metrics.total_time = time.time() - start_time
                return None, None, self.metrics
            
            # Update max memory
            current_memory = len(frontier) + len(explored)
            self.metrics.max_memory_nodes = max(self.metrics.max_memory_nodes, current_memory)
            
            # Pop node with minimum f
            f, node = heapq.heappop(frontier)
            del frontier_states[node.state]
            self.metrics.nodes_expanded += 1
            
            # Goal test
            if problem.goal_test(node.state):
                self.metrics.success = True
                self.metrics.total_time = time.time() - start_time
                path, actions = self._extract_solution(node)
                self.metrics.solution_length = len(actions)
                
                # Calculate branching factor
                if branching_factors:
                    self.metrics.avg_branching_factor = sum(branching_factors) / len(branching_factors)
                
                return path, actions, self.metrics
            
            # Add to explored (NO REOPENING!)
            explored.add(node.state)
            
            # Generate successors
            actions = problem.actions(node.state)
            branching_factors.append(len(actions))
            
            for action in actions:
                child_state, step_cost = problem.result(node.state, action)
                child_node = Node(child_state, node, action, step_cost)
                self.metrics.nodes_generated += 1
                
                # Skip if in explored (no reopening)
                if child_state in explored:
                    continue
                
                # Calculate f for child
                child_f = self._f(child_node, problem)
                
                # Check if in frontier
                if child_state in frontier_states:
                    frontier_g, frontier_f = frontier_states[child_state]
                    # If better g, replace in frontier
                    if child_node.g < frontier_g:
                        # Remove old from frontier
                        self._remove_from_frontier(frontier, frontier_states, child_state)
                        # Add new
                        heapq.heappush(frontier, (child_f, child_node))
                        frontier_states[child_state] = (child_node.g, child_f)
                else:
                    # New state, add to frontier
                    heapq.heappush(frontier, (child_f, child_node))
                    frontier_states[child_state] = (child_node.g, child_f)
                    self.metrics.max_frontier_size = max(self.metrics.max_frontier_size, len(frontier))
        
        # No solution found
        self.metrics.total_time = time.time() - start_time
        return None, None, self.metrics
    
    def _f(self, node: Node, problem) -> float:
        """Calculate f = g + h."""
        return node.g + self.heuristic(node.state)
    
    def _remove_from_frontier(self, frontier, frontier_states, state):
        """Remove node from frontier."""
        for i, (f, node) in enumerate(frontier):
            if node.state == state:
                frontier[i] = frontier[-1]
                frontier.pop()
                heapq.heapify(frontier)
                del frontier_states[state]
                break
    
    def _extract_solution(self, goal_node: Node):
        """Extract solution path from goal node."""
        path = []
        actions = []
        
        current = goal_node
        while current:
            path.append(current.state)
            if current.action:
                actions.append(current.action)
            current = current.parent
        
        path.reverse()
        actions.reverse()
        return path, actions

def test_a_star():
    """Test A* implementation."""
    print("Testing A* implementation...")
    
    # Simple test problem
    class TestProblem:
        def get_initial_state(self):
            return "start"
        
        def goal_test(self, state):
            return state == "goal"
        
        def actions(self, state):
            if state == "start":
                return ["move"]
            return []
        
        def result(self, state, action):
            return "goal", 1.0
    
    def simple_heuristic(state):
        return 0 if state == "goal" else 1
    
    problem = TestProblem()
    solver = AStarSolver(simple_heuristic)
    
    path, actions, metrics = solver.solve(problem)
    
    if metrics.success:
        print("✅ A* test passed!")
        print(f"Solution: {actions}")
    else:
        print("❌ A* test failed")
    

    return metrics
