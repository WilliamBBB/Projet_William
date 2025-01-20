import json
import pandas as pd
import numpy as np
import gurobipy as gp
from gurobipy import GRB

# Charger les données
with open("data/portfolio-example.json", "r") as f:
    data = json.load(f)

n = data["num_assets"]
sigma = np.array(data["covariance"])
mu = np.array(data["expected_return"])
mu_0 = data["target_return"]
k = data["portfolio_max_size"]

# Créer le modèle
with gp.Model("portfolio") as model:
    # Variables de décision : proportion investie dans chaque actif
    x = model.addVars(n, vtype=GRB.CONTINUOUS, name="x")
    
    # Variable binaire pour limiter le nombre d'actifs dans le portefeuille
    z = model.addVars(n, vtype=GRB.BINARY, name="z")

    # Fonction objectif : minimiser le risque (variance du portefeuille)
    portfolio_variance = gp.quicksum(sigma[i][j] * x[i] * x[j] for i in range(n) for j in range(n))
    model.setObjective(portfolio_variance, GRB.MINIMIZE)

    # Contrainte 1 : Retour attendu au moins égal à mu_0
    model.addConstr(gp.quicksum(mu[i] * x[i] for i in range(n)) >= mu_0, name="return")

    # Contrainte 2 : La somme des proportions doit être égale à 1
    model.addConstr(gp.quicksum(x[i] for i in range(n)) == 1, name="budget")

    # Contrainte 3 : Limiter le nombre d'actifs dans le portefeuille
    model.addConstr(gp.quicksum(z[i] for i in range(n)) <= k, name="max_assets")

    # Contrainte 4 : Lier les variables x et z
    for i in range(n):
        model.addConstr(x[i] <= z[i], name=f"link_{i}")

    # Résolution du modèle
    model.optimize()

    # Extraction des résultats
    if model.status == GRB.OPTIMAL:
        portfolio = [var.X for var in model.getVars() if "x" in var.VarName]
        risk = model.ObjVal
        expected_return = model.getRow(model.getConstrByName("return")).getValue()
        df = pd.DataFrame(
            data=portfolio + [risk, expected_return],
            index=[f"asset_{i}" for i in range(n)] + ["risk", "return"],
            columns=["Portfolio"],
        )
        print(df)
        selected_assets = [var.VarName for var in model.getVars() if var.X > 1e-6 and "x" in var.VarName]
        print("Selected assets:", selected_assets.index)
    else:
        print("No optimal solution found.")
