from functools import partial

import gurobipy as gp
from gurobipy import GRB


class CallbackData:
    def __init__(self):
        self.last_gap_change_time = -GRB.INFINITY
        self.last_gap = GRB.INFINITY


def callback(model, where, *, cbdata):
    if where == GRB.Callback.MIP:
        # Nombre de solutions trouvées
        sol_count = model.cbGet(GRB.Callback.MIP_SOLCNT)
        if sol_count == 0:
            return

        # Temps écoulé
        current_time = model.cbGet(GRB.Callback.RUNTIME)

        # Obtenir la meilleure solution (objective bound) et la meilleure borne
        obj_best = model.cbGet(GRB.Callback.MIP_OBJBST)
        obj_bound = model.cbGet(GRB.Callback.MIP_OBJBND)

        # Calculer l'écart relatif actuel si possible
        if obj_best != GRB.INFINITY and abs(obj_bound) > 1e-10:
            current_gap = abs(obj_bound - obj_best) / (abs(obj_best) + 1e-10)
        else:
            current_gap = GRB.INFINITY

        # Si aucune amélioration du gap n'a eu lieu depuis un certain temps
        if abs(current_gap - cbdata.last_gap) > epsilon_to_compare_gap:
            cbdata.last_gap = current_gap
            cbdata.last_gap_change_time = current_time
        elif current_time - cbdata.last_gap_change_time > time_from_best:
            print("Terminating due to lack of improvement in gap.")
            model.terminate()



with gp.read("data/mkp.mps/mkp.mps") as model:
    # Paramètres globaux utilisés dans le callback
    time_from_best = 15  # Temps maximal sans amélioration (en secondes)
    epsilon_to_compare_gap = 1e-4  # Tolérance pour comparer l'écart relatif

    # Initialiser les données passées à la fonction de callback
    callback_data = CallbackData()
    callback_func = partial(callback, cbdata=callback_data)

    model.optimize(callback_func)
