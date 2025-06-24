import pulp


class Optimizer:

    def __init__(self, num_variables):
        self.num_variables = num_variables

        self.model = pulp.LpProblem("Maximizar_Z", pulp.LpMaximize)

        self.variables = []

        for i in range(self.num_variables):
            self.variables.append(pulp.LpVariable(f'x{i + 1}', lowBound=0, cat='Continuous'))


    def set_objective_function(self, coefficients):
        objective_expression = pulp.lpSum(
            [coefficients[i] * self.variables[i] for i in range(self.num_variables)]
        )

        self.model += objective_expression, "Objective_Function"

    def add_constraint(self, coefficients, rhs, name, sense):
        lhs_expression = pulp.lpSum(
            [coefficients[i] * self.variables[i] for i in range(self.num_variables)]
        )

        if sense == '<=':
            self.model += lhs_expression <= rhs, name
        elif sense == '>=':
            self.model += lhs_expression >= rhs, name
        elif sense == '==':
            self.model += lhs_expression == rhs, name

    def solve(self):
        self.model.solve()

        # Devolver pro front-end os resultados

        # print("-" * 30)
        # print("Resultados Ótimos:")
        # for var in self.variables:
        #     print(f"  - Valor de {var.name}: {var.varValue:.2f}")
        #
        # print("-" * 30)
        # objective_value = pulp.value(self.model.objective)
        # print(f"Valor Ótimo da Função Objetivo: {objective_value:.2f}")
        #
        # print("-" * 30)
        # print("Preços Sombra (Shadow Prices):")
        # if not self.model.constraints:
        #     print("  - Nenhuma restrição no modelo.")
        # else:
        #     for name, constraint in self.model.constraints.items():
        #         print(f"  - Restrição '{name}': {constraint.pi:.2f}")
        # print("-" * 30)