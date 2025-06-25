
import pulp

class Optimizer:

    def __init__(self, num_variables):
        self.num_variables = num_variables
        self.model = pulp.LpProblem("Maximizar_Z", pulp.LpMaximize)
        self.variables = [pulp.LpVariable(f'x{i + 1}', lowBound=0, cat='Continuous')
                          for i in range(num_variables)]

    def set_objective_function(self, coefficients):
        expression = pulp.lpSum([coefficients[i] * self.variables[i] for i in range(self.num_variables)])
        self.model += expression, "Objective_Function"

    def add_constraint(self, coefficients, rhs, name, sense):
        lhs = pulp.lpSum([coefficients[i] * self.variables[i] for i in range(self.num_variables)])
        if sense == '<=':
            self.model += lhs <= rhs, name
        elif sense == '>=':
            self.model += lhs >= rhs, name
        elif sense == '==':
            self.model += lhs == rhs, name

    def solve(self):
        self.model.solve()
        valores_otimos = [v.varValue for v in self.variables]
        valor_objetivo = pulp.value(self.model.objective)
        precos_sombra = [c.pi for c in self.model.constraints.values()]
        return {
            "valores_otimos": valores_otimos,
            "valor_objetivo": valor_objetivo,
            "precos_sombra": precos_sombra
        }
