import numpy as np
import gurobipy as gp
from gurobipy import GRB

def generate_knapsack(num_items):
    # Fix seed value
    rng = np.random.default_rng(seed=0)
    # Item values, weights
    values = rng.uniform(low=1, high=25, size=num_items)
    weights = rng.uniform(low=5, high=100, size=num_items)
    # Knapsack capacity
    capacity = 0.7 * weights.sum()

    return values, weights, capacity


def solve_knapsack_model(values, weights, capacity):
    num_items = len(values)

    # Convert numpy arrays to dictionaries for Gurobi
    items = range(num_items)
    values_dict = {i: values[i] for i in items}
    weights_dict = {i: weights[i] for i in items}

    with gp.Env() as env:
        with gp.Model(name="knapsack", env=env) as model:
            # Define decision variables: x[i] is binary (0 or 1)
            x = model.addVars(items, vtype=GRB.BINARY, name="x")

            # Set objective: maximize the total value
            model.setObjective(x.prod(values_dict), GRB.MAXIMIZE)

            # Add capacity constraint
            model.addConstr(x.prod(weights_dict) <= capacity, "capacity")

            # Optimize the model
            model.optimize()

            # Print the solution
            if model.status == GRB.OPTIMAL:
                print("Optimal solution found!")
                for i in items:
                    if x[i].x > 0.5:  # Include item if x[i] is 1
                        print(f"Item {i}: value={values[i]:.2f}, weight={weights[i]:.2f}")
                print(f"Total value: {model.objVal:.2f}")
            else:
                print("No optimal solution found.")

# Generate data and solve the knapsack problem
data = generate_knapsack(100)  # Réduire à 100 objets
solve_knapsack_model(*data)
