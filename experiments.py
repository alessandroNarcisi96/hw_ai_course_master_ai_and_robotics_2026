"""
Experiment runner for Sokoban solver comparison.
"""
import time
import json
from typing import List, Dict, Any
import matplotlib.pyplot as plt
import numpy as np

from a_star import AStarSolver, AStarMetrics
from sokoban import SokobanProblem, load_level
from heuristics import create_heuristic
from csp_solver import CSPSolver, CSPMetrics

class ExperimentRunner:
    """Run experiments comparing A* and CSP."""
    
    def __init__(self, output_dir="results"):
        self.output_dir = output_dir
        self.a_star_results = []
        self.csp_results = []
    
    def run_a_star_on_levels(self, level_files: List[str], timeout=30):
        """Run A* on multiple levels with different heuristics."""
        print("\n" + "="*60)
        print("Running A* Experiments")
        print("="*60)
        
        for level_file in level_files:
            print(f"\nLevel: {level_file}")
            
            # Load level
            level_str = load_level(level_file)
            problem = SokobanProblem(level_str)
            
            # Get goals for heuristic
            goals = problem.initial_state.goals
            
            # Test different heuristics
            for heuristic_name in ["manhattan", "count", "matching"]:
                print(f"  Heuristic: {heuristic_name}")
                
                heuristic_func = create_heuristic(heuristic_name, goals)
                solver = AStarSolver(heuristic_func)
                
                start_time = time.time()
                path, actions, metrics = solver.solve(problem, timeout=timeout)
                elapsed = time.time() - start_time
                
                # Add level info
                metrics.level = level_file
                metrics.heuristic = heuristic_name
                metrics.scaling_param = len(problem.initial_state.boxes)
                
                # Convert actions to short format: U, D, L, R
                if actions:
                    move_map = {'UP': 'U', 'DOWN': 'D', 'LEFT': 'L', 'RIGHT': 'R'}
                    metrics.moves = ','.join([move_map.get(a, a[0]) for a in actions])
                else:
                    metrics.moves = ''
                
                self.a_star_results.append(metrics.__dict__)
                
                status = "✅" if metrics.success else "❌"
                if metrics.timeout:
                    status = "⏰"
                
                print(f"    {status} Time: {elapsed:.3f}s, "
                      f"Nodes: {metrics.nodes_expanded:,}, "
                      f"Solution: {metrics.solution_length if metrics.success else 'N/A'}")
    
    def run_csp_on_levels(self, level_files: List[str], timeout=30):
        """Run CSP solver on multiple levels."""
        print("\n" + "="*60)
        print("Running CSP Experiments")
        print("="*60)
        
        for level_file in level_files:
            print(f"\nLevel: {level_file}")
            
            level_str = load_level(level_file)
            problem = SokobanProblem(level_str)
            
            solver = CSPSolver()
            
            try:
                solution, metrics = solver.solve_sokoban(problem, max_steps=20, timeout=timeout)
                
                # Add level info
                metrics.level = level_file
                metrics.scaling_param = len(problem.initial_state.boxes)
                
                # Convert solution to short format: U, D, L, R
                if solution:
                    move_map = {'UP': 'U', 'DOWN': 'D', 'LEFT': 'L', 'RIGHT': 'R'}
                    metrics.moves = ','.join([move_map.get(a, a[0]) for a in solution])
                else:
                    metrics.moves = ''
                
                self.csp_results.append(metrics.__dict__)
                
                status = "✅" if metrics.success else "❌"
                if metrics.timeout:
                    status = "⏰"
                elif hasattr(metrics, 'solver_not_found') and metrics.solver_not_found:
                    status = "⚠️"
                
                message = f"    {status} Time: {metrics.total_time:.3f}s, "
                if hasattr(metrics, 'solver_not_found') and metrics.solver_not_found:
                    message += "OR-Tools not installed"
                else:
                    message += f"Vars: {metrics.num_variables}, Solution: {metrics.solution_length if metrics.success else 'N/A'}"
                print(message)
                
            except FileNotFoundError as e:
                print(f"    ⚠️  CSP solver (OR-Tools) not installed - skipping")
                # Add a placeholder result
                self.csp_results.append({
                    'level': level_file,
                    'scaling_param': len(problem.initial_state.boxes),
                    'success': False,
                    'total_time': 0,
                    'note': 'CSP solver not installed'
                })
            except Exception as e:
                print(f"    ❌ CSP solver error: {e}")
    
    def save_results(self):
        """Save results to JSON files."""
        import os
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Save A* results
        with open(f"{self.output_dir}/a_star_results.json", 'w', encoding='utf-8') as f:
            json.dump(self.a_star_results, f, indent=2)
        
        # Save CSP results
        with open(f"{self.output_dir}/csp_results.json", 'w', encoding='utf-8') as f:
            json.dump(self.csp_results, f, indent=2)
        
        print(f"\nResults saved to {self.output_dir}/")
    
    def generate_plots(self):
        """Generate plots from experiment results."""
        if not self.a_star_results:
            print("No results to plot")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Plot 1: Time vs Number of Boxes (A*)
        self._plot_time_vs_boxes(axes[0, 0])
        
        # Plot 2: Nodes Expanded vs Boxes (A*)
        self._plot_nodes_vs_boxes(axes[0, 1])
        
        # Plot 3: Heuristic Comparison (A*)
        self._plot_heuristic_comparison(axes[1, 0])
        
        # Plot 4: A* vs CSP Time Comparison
        self._plot_algorithm_comparison(axes[1, 1])
        
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/experiment_plots.png", dpi=300)
        plt.show()
    
    def _plot_time_vs_boxes(self, ax):
        """Plot search time vs number of boxes."""
        boxes = []
        times = []
        heuristics = []
        
        for result in self.a_star_results:
            if result.get('success'):
                boxes.append(result.get('scaling_param', 0))
                times.append(result.get('total_time', 0))
                heuristics.append(result.get('heuristic', 'unknown'))
        
        # Group by heuristic
        heuristic_data = {}
        for b, t, h in zip(boxes, times, heuristics):
            if h not in heuristic_data:
                heuristic_data[h] = {'boxes': [], 'times': []}
            heuristic_data[h]['boxes'].append(b)
            heuristic_data[h]['times'].append(t)
        
        colors = ['blue', 'orange', 'green']
        for (h, data), color in zip(heuristic_data.items(), colors):
            ax.scatter(data['boxes'], data['times'], label=h, alpha=0.7, color=color)
        
        ax.set_xlabel("Number of Boxes (Scaling Parameter)")
        ax.set_ylabel("Search Time (seconds)")
        ax.set_title("A*: Time vs Problem Size")
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_nodes_vs_boxes(self, ax):
        """Plot nodes expanded vs number of boxes."""
        boxes = []
        nodes = []
        
        for result in self.a_star_results:
            if result.get('success'):
                boxes.append(result.get('scaling_param', 0))
                nodes.append(result.get('nodes_expanded', 0))
        
        ax.scatter(boxes, nodes, alpha=0.7)
        ax.set_xlabel("Number of Boxes")
        ax.set_ylabel("Nodes Expanded")
        ax.set_title("A*: Nodes Expanded vs Problem Size")
        ax.set_yscale('log')
        ax.grid(True, alpha=0.3)
    
    def _plot_heuristic_comparison(self, ax):
        """Compare different heuristics."""
        heuristic_times = {}
        
        for result in self.a_star_results:
            if result.get('success'):
                h = result.get('heuristic', 'unknown')
                if h not in heuristic_times:
                    heuristic_times[h] = []
                heuristic_times[h].append(result.get('total_time', 0))
        
        # Create box plot
        data = [heuristic_times[h] for h in heuristic_times]
        ax.boxplot(data, labels=list(heuristic_times.keys()))
        ax.set_ylabel("Time (seconds)")
        ax.set_title("Heuristic Performance Comparison")
        ax.grid(True, alpha=0.3)
    
    def _plot_algorithm_comparison(self, ax):
        """Compare A* and CSP times."""
        if not self.csp_results:
            return
        
        # Get average times for successful runs
        a_star_times = [r['total_time'] for r in self.a_star_results 
                       if r.get('success') and 'total_time' in r]
        csp_times = [r['total_time'] for r in self.csp_results 
                    if r.get('success') and 'total_time' in r]
        
        if a_star_times and csp_times:
            avg_a_star = np.mean(a_star_times)
            avg_csp = np.mean(csp_times)
            
            bars = ax.bar(['A*', 'CSP'], [avg_a_star, avg_csp], alpha=0.7)
            ax.set_ylabel("Average Time (seconds)")
            ax.set_title("Algorithm Comparison")
            ax.grid(True, alpha=0.3)
            
            # Add value labels
            for bar, time_val in zip(bars, [avg_a_star, avg_csp]):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                       f'{time_val:.3f}s', ha='center', va='bottom')