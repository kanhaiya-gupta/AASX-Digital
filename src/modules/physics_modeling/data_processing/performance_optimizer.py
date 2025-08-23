"""
Performance Optimizer for Physics Modeling
Handles performance optimization and resource management
"""

import asyncio
import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union, Callable
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class OptimizationStrategy(Enum):
    """Types of optimization strategies"""
    GRADIENT_DESCENT = "gradient_descent"
    GENETIC_ALGORITHM = "genetic_algorithm"
    PARTICLE_SWARM = "particle_swarm"
    SIMULATED_ANNEALING = "simulated_annealing"
    BAYESIAN_OPTIMIZATION = "bayesian_optimization"

class ResourceType(Enum):
    """Types of computational resources"""
    CPU = "cpu"
    MEMORY = "memory"
    GPU = "gpu"
    NETWORK = "network"
    STORAGE = "storage"

@dataclass
class OptimizationConfig:
    """Configuration for performance optimization"""
    strategy: OptimizationStrategy = OptimizationStrategy.GRADIENT_DESCENT
    max_iterations: int = 1000
    convergence_tolerance: float = 1e-6
    learning_rate: float = 0.01
    population_size: int = 50
    mutation_rate: float = 0.1
    crossover_rate: float = 0.8
    temperature: float = 1000.0
    cooling_rate: float = 0.95
    use_parallel: bool = True
    max_workers: int = 4

@dataclass
class ResourceConfig:
    """Configuration for resource management"""
    max_cpu_usage: float = 0.8
    max_memory_usage: float = 0.8
    max_gpu_usage: float = 0.9
    max_network_bandwidth: float = 0.7
    max_storage_usage: float = 0.8
    enable_resource_monitoring: bool = True
    resource_check_interval: float = 1.0

class PerformanceOptimizer:
    """Performance optimization and resource management for physics modeling"""
    
    def __init__(self, opt_config: Optional[OptimizationConfig] = None, 
                 resource_config: Optional[ResourceConfig] = None):
        self.opt_config = opt_config or OptimizationConfig()
        self.resource_config = resource_config or ResourceConfig()
        self.optimization_history = []
        self.resource_usage_history = []
        self.performance_metrics = {}
        self.optimization_stats = {
            'total_optimizations': 0,
            'successful_optimizations': 0,
            'failed_optimizations': 0,
            'total_improvement': 0.0
        }
        logger.info("✅ Performance Optimizer initialized")
    
    async def optimize_performance(self, objective_function: Callable, 
                                 initial_parameters: Dict[str, Any],
                                 constraints: Optional[List[Dict[str, Any]]] = None,
                                 optimization_type: str = "general") -> Dict[str, Any]:
        """Optimize performance using specified strategy"""
        await asyncio.sleep(0)
        
        start_time = datetime.now()
        logger.info(f"🔄 Starting performance optimization using {self.opt_config.strategy.value}")
        
        try:
            # Check resource availability
            resource_check = await self._check_resource_availability()
            if not resource_check['available']:
                raise ValueError(f"Insufficient resources: {resource_check['constraints']}")
            
            # Run optimization based on strategy
            if self.opt_config.strategy == OptimizationStrategy.GRADIENT_DESCENT:
                result = await self._gradient_descent_optimization(
                    objective_function, initial_parameters, constraints
                )
            elif self.opt_config.strategy == OptimizationStrategy.GENETIC_ALGORITHM:
                result = await self._genetic_algorithm_optimization(
                    objective_function, initial_parameters, constraints
                )
            elif self.opt_config.strategy == OptimizationStrategy.PARTICLE_SWARM:
                result = await self._particle_swarm_optimization(
                    objective_function, initial_parameters, constraints
                )
            elif self.opt_config.strategy == OptimizationStrategy.SIMULATED_ANNEALING:
                result = await self._simulated_annealing_optimization(
                    objective_function, initial_parameters, constraints
                )
            elif self.opt_config.strategy == OptimizationStrategy.BAYESIAN_OPTIMIZATION:
                result = await self._bayesian_optimization(
                    objective_function, initial_parameters, constraints
                )
            else:
                raise ValueError(f"Unsupported optimization strategy: {self.opt_config.strategy}")
            
            # Record optimization history
            optimization_time = (datetime.now() - start_time).total_seconds()
            optimization_record = {
                'timestamp': datetime.now(),
                'optimization_type': optimization_type,
                'strategy': self.opt_config.strategy.value,
                'optimization_time': optimization_time,
                'initial_parameters': initial_parameters,
                'final_parameters': result.get('optimal_parameters', {}),
                'initial_objective': result.get('initial_objective', 0.0),
                'final_objective': result.get('optimal_objective', 0.0),
                'improvement': result.get('improvement', 0.0),
                'iterations': result.get('iterations', 0),
                'converged': result.get('converged', False),
                'success': result.get('success', False)
            }
            
            self.optimization_history.append(optimization_record)
            
            # Update statistics
            self.optimization_stats['total_optimizations'] += 1
            if result.get('success', False):
                self.optimization_stats['successful_optimizations'] += 1
                self.optimization_stats['total_improvement'] += result.get('improvement', 0.0)
            else:
                self.optimization_stats['failed_optimizations'] += 1
            
            logger.info(f"✅ Performance optimization completed in {optimization_time:.3f}s")
            return result
            
        except Exception as e:
            optimization_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ Performance optimization failed: {str(e)}")
            
            self.optimization_history.append({
                'timestamp': datetime.now(),
                'optimization_type': optimization_type,
                'strategy': self.opt_config.strategy.value,
                'optimization_time': optimization_time,
                'success': False,
                'error': str(e)
            })
            
            self.optimization_stats['total_optimizations'] += 1
            self.optimization_stats['failed_optimizations'] += 1
            
            return {
                'success': False,
                'error': str(e),
                'optimization_time': optimization_time
            }
    
    async def _check_resource_availability(self) -> Dict[str, Any]:
        """Check if sufficient resources are available"""
        await asyncio.sleep(0)
        
        if not self.resource_config.enable_resource_monitoring:
            return {'available': True, 'constraints': []}
        
        constraints = []
        
        # Check CPU usage
        cpu_usage = await self._get_cpu_usage()
        if cpu_usage > self.resource_config.max_cpu_usage:
            constraints.append(f"CPU usage {cpu_usage:.2%} exceeds limit {self.resource_config.max_cpu_usage:.2%}")
        
        # Check memory usage
        memory_usage = await self._get_memory_usage()
        if memory_usage > self.resource_config.max_memory_usage:
            constraints.append(f"Memory usage {memory_usage:.2%} exceeds limit {self.resource_config.max_memory_usage:.2%}")
        
        # Check GPU usage
        gpu_usage = await self._get_gpu_usage()
        if gpu_usage > self.resource_config.max_gpu_usage:
            constraints.append(f"GPU usage {gpu_usage:.2%} exceeds limit {self.resource_config.max_gpu_usage:.2%}")
        
        available = len(constraints) == 0
        
        # Record resource usage
        self.resource_usage_history.append({
            'timestamp': datetime.now(),
            'cpu_usage': cpu_usage,
            'memory_usage': memory_usage,
            'gpu_usage': gpu_usage,
            'available': available
        })
        
        return {
            'available': available,
            'constraints': constraints,
            'current_usage': {
                'cpu': cpu_usage,
                'memory': memory_usage,
                'gpu': gpu_usage
            }
        }
    
    async def _gradient_descent_optimization(self, objective_function: Callable,
                                           initial_parameters: Dict[str, Any],
                                           constraints: Optional[List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Gradient descent optimization"""
        await asyncio.sleep(0)
        
        parameters = initial_parameters.copy()
        learning_rate = self.opt_config.learning_rate
        
        # Evaluate initial objective
        initial_objective = await self._evaluate_objective(objective_function, parameters)
        best_objective = initial_objective
        best_parameters = parameters.copy()
        
        for iteration in range(self.opt_config.max_iterations):
            # Calculate gradients (finite difference approximation)
            gradients = await self._calculate_gradients(objective_function, parameters)
            
            # Update parameters
            for key in parameters:
                if key in gradients:
                    parameters[key] -= learning_rate * gradients[key]
            
            # Apply constraints
            if constraints:
                parameters = await self._apply_parameter_constraints(parameters, constraints)
            
            # Evaluate new objective
            current_objective = await self._evaluate_objective(objective_function, parameters)
            
            # Check convergence
            if abs(current_objective - best_objective) < self.opt_config.convergence_tolerance:
                break
            
            # Update best solution
            if current_objective < best_objective:
                best_objective = current_objective
                best_parameters = parameters.copy()
            
            # Adaptive learning rate
            if iteration > 0 and current_objective > best_objective:
                learning_rate *= 0.9
        
        improvement = initial_objective - best_objective
        
        return {
            'success': True,
            'optimal_parameters': best_parameters,
            'optimal_objective': best_objective,
            'initial_objective': initial_objective,
            'improvement': improvement,
            'iterations': iteration + 1,
            'converged': iteration < self.opt_config.max_iterations - 1,
            'strategy': 'gradient_descent'
        }
    
    async def _genetic_algorithm_optimization(self, objective_function: Callable,
                                            initial_parameters: Dict[str, Any],
                                            constraints: Optional[List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Genetic algorithm optimization"""
        await asyncio.sleep(0)
        
        # Initialize population
        population = await self._initialize_population(initial_parameters, self.opt_config.population_size)
        
        # Evaluate initial population
        fitness_scores = []
        for individual in population:
            fitness = await self._evaluate_objective(objective_function, individual)
            fitness_scores.append(fitness)
        
        best_objective = min(fitness_scores)
        best_parameters = population[np.argmin(fitness_scores)].copy()
        initial_objective = best_objective
        
        for generation in range(self.opt_config.max_iterations):
            # Selection
            parents = await self._selection(population, fitness_scores)
            
            # Crossover
            offspring = await self._crossover(parents)
            
            # Mutation
            offspring = await self._mutation(offspring)
            
            # Apply constraints
            if constraints:
                for individual in offspring:
                    individual = await self._apply_parameter_constraints(individual, constraints)
            
            # Evaluate offspring
            offspring_fitness = []
            for individual in offspring:
                fitness = await self._evaluate_objective(objective_function, individual)
                offspring_fitness.append(fitness)
            
            # Replace population
            population = offspring
            fitness_scores = offspring_fitness
            
            # Update best solution
            min_fitness = min(fitness_scores)
            if min_fitness < best_objective:
                best_objective = min_fitness
                best_parameters = population[np.argmin(fitness_scores)].copy()
            
            # Check convergence
            if abs(best_objective - initial_objective) < self.opt_config.convergence_tolerance:
                break
        
        improvement = initial_objective - best_objective
        
        return {
            'success': True,
            'optimal_parameters': best_parameters,
            'optimal_objective': best_objective,
            'initial_objective': initial_objective,
            'improvement': improvement,
            'iterations': generation + 1,
            'converged': generation < self.opt_config.max_iterations - 1,
            'strategy': 'genetic_algorithm'
        }
    
    async def _particle_swarm_optimization(self, objective_function: Callable,
                                         initial_parameters: Dict[str, Any],
                                         constraints: Optional[List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Particle swarm optimization"""
        await asyncio.sleep(0)
        
        # Initialize particles
        particles = await self._initialize_particles(initial_parameters, self.opt_config.population_size)
        velocities = await self._initialize_velocities(initial_parameters, self.opt_config.population_size)
        
        # Evaluate initial particles
        particle_fitness = []
        for particle in particles:
            fitness = await self._evaluate_objective(objective_function, particle)
            particle_fitness.append(fitness)
        
        best_objective = min(particle_fitness)
        best_parameters = particles[np.argmin(particle_fitness)].copy()
        initial_objective = best_objective
        
        # Personal best positions
        personal_best = particles.copy()
        personal_best_fitness = particle_fitness.copy()
        
        for iteration in range(self.opt_config.max_iterations):
            # Update velocities and positions
            for i in range(len(particles)):
                # Update velocity
                for key in particles[i]:
                    if key in velocities[i] and key in personal_best[i]:
                        # Cognitive component
                        cognitive = 0.5 * (personal_best[i][key] - particles[i][key])
                        # Social component
                        social = 0.5 * (best_parameters[key] - particles[i][key])
                        
                        velocities[i][key] = 0.7 * velocities[i][key] + cognitive + social
                
                # Update position
                for key in particles[i]:
                    if key in velocities[i]:
                        particles[i][key] += velocities[i][key]
            
            # Apply constraints
            if constraints:
                for particle in particles:
                    particle = await self._apply_parameter_constraints(particle, constraints)
            
            # Evaluate new positions
            for i, particle in enumerate(particles):
                fitness = await self._evaluate_objective(objective_function, particle)
                particle_fitness[i] = fitness
                
                # Update personal best
                if fitness < personal_best_fitness[i]:
                    personal_best[i] = particle.copy()
                    personal_best_fitness[i] = fitness
                
                # Update global best
                if fitness < best_objective:
                    best_objective = fitness
                    best_parameters = particle.copy()
            
            # Check convergence
            if abs(best_objective - initial_objective) < self.opt_config.convergence_tolerance:
                break
        
        improvement = initial_objective - best_objective
        
        return {
            'success': True,
            'optimal_parameters': best_parameters,
            'optimal_objective': best_objective,
            'initial_objective': initial_objective,
            'improvement': improvement,
            'iterations': iteration + 1,
            'converged': iteration < self.opt_config.max_iterations - 1,
            'strategy': 'particle_swarm'
        }
    
    async def _simulated_annealing_optimization(self, objective_function: Callable,
                                              initial_parameters: Dict[str, Any],
                                              constraints: Optional[List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Simulated annealing optimization"""
        await asyncio.sleep(0)
        
        current_parameters = initial_parameters.copy()
        current_objective = await self._evaluate_objective(objective_function, current_parameters)
        
        best_parameters = current_parameters.copy()
        best_objective = current_objective
        initial_objective = current_objective
        
        temperature = self.opt_config.temperature
        
        for iteration in range(self.opt_config.max_iterations):
            # Generate neighbor solution
            neighbor_parameters = await self._generate_neighbor(current_parameters)
            
            # Apply constraints
            if constraints:
                neighbor_parameters = await self._apply_parameter_constraints(neighbor_parameters, constraints)
            
            # Evaluate neighbor
            neighbor_objective = await self._evaluate_objective(objective_function, neighbor_parameters)
            
            # Accept or reject based on temperature
            delta_e = neighbor_objective - current_objective
            
            if delta_e < 0 or np.random.random() < np.exp(-delta_e / temperature):
                current_parameters = neighbor_parameters
                current_objective = neighbor_objective
                
                # Update best solution
                if current_objective < best_objective:
                    best_parameters = current_parameters.copy()
                    best_objective = current_objective
            
            # Cool down
            temperature *= self.opt_config.cooling_rate
            
            # Check convergence
            if abs(best_objective - initial_objective) < self.opt_config.convergence_tolerance:
                break
        
        improvement = initial_objective - best_objective
        
        return {
            'success': True,
            'optimal_parameters': best_parameters,
            'optimal_objective': best_objective,
            'initial_objective': initial_objective,
            'improvement': improvement,
            'iterations': iteration + 1,
            'converged': iteration < self.opt_config.max_iterations - 1,
            'strategy': 'simulated_annealing'
        }
    
    async def _bayesian_optimization(self, objective_function: Callable,
                                   initial_parameters: Dict[str, Any],
                                   constraints: Optional[List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Bayesian optimization"""
        await asyncio.sleep(0)
        
        # For simplicity, implement a basic version
        # In practice, this would use a proper Bayesian optimization library
        
        best_parameters = initial_parameters.copy()
        best_objective = await self._evaluate_objective(objective_function, best_parameters)
        initial_objective = best_objective
        
        for iteration in range(self.opt_config.max_iterations):
            # Generate candidate points (random sampling for simplicity)
            candidate_parameters = await self._generate_candidate_parameters(initial_parameters)
            
            # Apply constraints
            if constraints:
                candidate_parameters = await self._apply_parameter_constraints(candidate_parameters, constraints)
            
            # Evaluate candidate
            candidate_objective = await self._evaluate_objective(objective_function, candidate_parameters)
            
            # Update best solution
            if candidate_objective < best_objective:
                best_parameters = candidate_parameters.copy()
                best_objective = candidate_objective
            
            # Check convergence
            if abs(best_objective - initial_objective) < self.opt_config.convergence_tolerance:
                break
        
        improvement = initial_objective - best_objective
        
        return {
            'success': True,
            'optimal_parameters': best_parameters,
            'optimal_objective': best_objective,
            'initial_objective': initial_objective,
            'improvement': improvement,
            'iterations': iteration + 1,
            'converged': iteration < self.opt_config.max_iterations - 1,
            'strategy': 'bayesian_optimization'
        }
    
    # Helper methods
    async def _evaluate_objective(self, objective_function: Callable, 
                                 parameters: Dict[str, Any]) -> float:
        """Evaluate objective function"""
        await asyncio.sleep(0)
        
        try:
            if asyncio.iscoroutinefunction(objective_function):
                return await objective_function(parameters)
            else:
                return objective_function(parameters)
        except Exception as e:
            logger.warning(f"⚠️ Objective function evaluation failed: {str(e)}")
            return float('inf')
    
    async def _calculate_gradients(self, objective_function: Callable, 
                                  parameters: Dict[str, Any]) -> Dict[str, float]:
        """Calculate gradients using finite differences"""
        await asyncio.sleep(0)
        
        gradients = {}
        epsilon = 1e-6
        
        for key, value in parameters.items():
            if isinstance(value, (int, float)):
                # Forward difference
                params_plus = parameters.copy()
                params_plus[key] = value + epsilon
                
                params_minus = parameters.copy()
                params_minus[key] = value - epsilon
                
                f_plus = await self._evaluate_objective(objective_function, params_plus)
                f_minus = await self._evaluate_objective(objective_function, params_minus)
                
                gradients[key] = (f_plus - f_minus) / (2 * epsilon)
        
        return gradients
    
    async def _apply_parameter_constraints(self, parameters: Dict[str, Any], 
                                         constraints: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply parameter constraints"""
        await asyncio.sleep(0)
        
        constrained_parameters = parameters.copy()
        
        for constraint in constraints:
            param_name = constraint.get('parameter')
            min_val = constraint.get('min')
            max_val = constraint.get('max')
            
            if param_name in constrained_parameters:
                value = constrained_parameters[param_name]
                if min_val is not None:
                    constrained_parameters[param_name] = max(value, min_val)
                if max_val is not None:
                    constrained_parameters[param_name] = min(constrained_parameters[param_name], max_val)
        
        return constrained_parameters
    
    async def _initialize_population(self, initial_parameters: Dict[str, Any], 
                                   population_size: int) -> List[Dict[str, Any]]:
        """Initialize genetic algorithm population"""
        await asyncio.sleep(0)
        
        population = []
        
        for _ in range(population_size):
            individual = {}
            for key, value in initial_parameters.items():
                if isinstance(value, (int, float)):
                    # Add random perturbation
                    perturbation = np.random.normal(0, 0.1 * abs(value))
                    individual[key] = value + perturbation
                else:
                    individual[key] = value
            
            population.append(individual)
        
        return population
    
    async def _initialize_velocities(self, initial_parameters: Dict[str, Any], 
                                   population_size: int) -> List[Dict[str, Any]]:
        """Initialize particle swarm velocities"""
        await asyncio.sleep(0)
        
        velocities = []
        
        for _ in range(population_size):
            velocity = {}
            for key, value in initial_parameters.items():
                if isinstance(value, (int, float)):
                    # Random initial velocity
                    velocity[key] = np.random.normal(0, 0.1 * abs(value))
                else:
                    velocity[key] = 0
            
            velocities.append(velocity)
        
        return velocities
    
    async def _selection(self, population: List[Dict[str, Any]], 
                        fitness_scores: List[float]) -> List[Dict[str, Any]]:
        """Tournament selection for genetic algorithm"""
        await asyncio.sleep(0)
        
        selected = []
        tournament_size = 3
        
        for _ in range(len(population)):
            # Random tournament
            tournament_indices = np.random.choice(len(population), tournament_size, replace=False)
            tournament_fitness = [fitness_scores[i] for i in tournament_indices]
            
            # Select best from tournament
            winner_index = tournament_indices[np.argmin(tournament_fitness)]
            selected.append(population[winner_index])
        
        return selected
    
    async def _crossover(self, parents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Crossover operation for genetic algorithm"""
        await asyncio.sleep(0)
        
        offspring = []
        
        for i in range(0, len(parents), 2):
            if i + 1 < len(parents):
                parent1 = parents[i]
                parent2 = parents[i + 1]
                
                # Uniform crossover
                child1 = {}
                child2 = {}
                
                for key in parent1:
                    if np.random.random() < self.opt_config.crossover_rate:
                        child1[key] = parent1[key]
                        child2[key] = parent2[key]
                    else:
                        child1[key] = parent2[key]
                        child2[key] = parent1[key]
                
                offspring.extend([child1, child2])
            else:
                offspring.append(parents[i])
        
        return offspring
    
    async def _mutation(self, offspring: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Mutation operation for genetic algorithm"""
        await asyncio.sleep(0)
        
        mutated = []
        
        for individual in offspring:
            mutated_individual = individual.copy()
            
            for key, value in individual.items():
                if isinstance(value, (int, float)) and np.random.random() < self.opt_config.mutation_rate:
                    # Add random perturbation
                    perturbation = np.random.normal(0, 0.1 * abs(value))
                    mutated_individual[key] = value + perturbation
            
            mutated.append(mutated_individual)
        
        return mutated
    
    async def _generate_neighbor(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate neighbor solution for simulated annealing"""
        await asyncio.sleep(0)
        
        neighbor = parameters.copy()
        
        for key, value in parameters.items():
            if isinstance(value, (int, float)):
                # Add random perturbation
                perturbation = np.random.normal(0, 0.1 * abs(value))
                neighbor[key] = value + perturbation
        
        return neighbor
    
    async def _generate_candidate_parameters(self, initial_parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate candidate parameters for Bayesian optimization"""
        await asyncio.sleep(0)
        
        candidate = {}
        
        for key, value in initial_parameters.items():
            if isinstance(value, (int, float)):
                # Random sampling around current value
                candidate[key] = np.random.normal(value, 0.1 * abs(value))
            else:
                candidate[key] = value
        
        return candidate
    
    # Resource monitoring methods
    async def _get_cpu_usage(self) -> float:
        """Get current CPU usage"""
        await asyncio.sleep(0)
        
        # Mock CPU usage (in practice, use psutil or similar)
        return np.random.uniform(0.1, 0.8)
    
    async def _get_memory_usage(self) -> float:
        """Get current memory usage"""
        await asyncio.sleep(0)
        
        # Mock memory usage (in practice, use psutil or similar)
        return np.random.uniform(0.2, 0.7)
    
    async def _get_gpu_usage(self) -> float:
        """Get current GPU usage"""
        await asyncio.sleep(0)
        
        # Mock GPU usage (in practice, use nvidia-ml-py or similar)
        return np.random.uniform(0.0, 0.6)
    
    async def get_optimization_summary(self) -> Dict[str, Any]:
        """Get summary of optimization operations"""
        await asyncio.sleep(0)
        
        total_optimizations = len(self.optimization_history)
        successful_optimizations = sum(1 for op in self.optimization_history if op.get('success', False))
        failed_optimizations = total_optimizations - successful_optimizations
        
        avg_optimization_time = 0
        avg_improvement = 0
        
        if total_optimizations > 0:
            optimization_times = [op['optimization_time'] for op in self.optimization_history if op.get('success', False)]
            improvements = [op.get('improvement', 0.0) for op in self.optimization_history if op.get('success', False)]
            
            if optimization_times:
                avg_optimization_time = sum(optimization_times) / len(optimization_times)
            if improvements:
                avg_improvement = sum(improvements) / len(improvements)
        
        return {
            'total_optimizations': total_optimizations,
            'successful_optimizations': successful_optimizations,
            'failed_optimizations': failed_optimizations,
            'success_rate': successful_optimizations / total_optimizations if total_optimizations > 0 else 0,
            'average_optimization_time': avg_optimization_time,
            'average_improvement': avg_improvement,
            'optimization_stats': self.optimization_stats,
            'recent_optimizations': self.optimization_history[-5:] if self.optimization_history else []
        }
    
    async def get_resource_usage_summary(self) -> Dict[str, Any]:
        """Get summary of resource usage"""
        await asyncio.sleep(0)
        
        if not self.resource_usage_history:
            return {'message': 'No resource usage data available'}
        
        recent_usage = self.resource_usage_history[-10:]  # Last 10 measurements
        
        avg_cpu = np.mean([u['cpu_usage'] for u in recent_usage])
        avg_memory = np.mean([u['memory_usage'] for u in recent_usage])
        avg_gpu = np.mean([u['gpu_usage'] for u in recent_usage])
        
        return {
            'average_usage': {
                'cpu': avg_cpu,
                'memory': avg_memory,
                'gpu': avg_gpu
            },
            'resource_limits': {
                'max_cpu': self.resource_config.max_cpu_usage,
                'max_memory': self.resource_config.max_memory_usage,
                'max_gpu': self.resource_config.max_gpu_usage
            },
            'recent_usage': recent_usage
        }
    
    async def reset_statistics(self) -> None:
        """Reset all statistics and history"""
        await asyncio.sleep(0)
        
        self.optimization_history.clear()
        self.resource_usage_history.clear()
        self.performance_metrics.clear()
        self.optimization_stats = {
            'total_optimizations': 0,
            'successful_optimizations': 0,
            'failed_optimizations': 0,
            'total_improvement': 0.0
        }
        logger.info("🔄 Performance Optimizer statistics reset")
