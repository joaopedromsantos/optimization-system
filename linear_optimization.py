import pulp

class Optimizer:

    def __init__(self, num_variables, sense=pulp.LpMaximize):
        self.num_variables = num_variables
        self.model = pulp.LpProblem("Maximizar_Z", sense)
        self.variables = [pulp.LpVariable(f'x{i + 1}', lowBound=0, cat='Continuous')
                          for i in range(num_variables)]
        self.coef_fo = None
        self.constraints_data = []  # lista de (coef_rest, rhs, sense, name)

    def set_objective_function(self, coefficients):
        self.coef_fo = coefficients
        expression = pulp.lpSum([coefficients[i] * self.variables[i] for i in range(self.num_variables)])
        self.model += expression, "Objective_Function"

    def add_constraint(self, coefficients, rhs, name, sense):
        self.constraints_data.append((coefficients, rhs, sense, name))
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
        viavel = self.model.status
        return {
            "valores_otimos": valores_otimos,
            "valor_objetivo": valor_objetivo,
            "precos_sombra": precos_sombra,
            "viavel": viavel
        }

    def analyze_delta(self, constr_index, delta_b):
        # cria novo modelo com aumento da restrição
        new_model = pulp.LpProblem("Maximizar_Z_Delta", pulp.LpMaximize)
        new_vars = [pulp.LpVariable(f'x{i + 1}', lowBound=0, cat='Continuous') for i in range(self.num_variables)]

        # Função objetivo
        expression = pulp.lpSum([self.coef_fo[i] * new_vars[i] for i in range(self.num_variables)])
        new_model += expression

        # Adiciona restrições, aumentando RHS da restrição especificada
        for i, (coef_rest, rhs, sense, name) in enumerate(self.constraints_data):
            lhs = pulp.lpSum([coef_rest[j] * new_vars[j] for j in range(self.num_variables)])
            if i == constr_index:
                rhs += delta_b
            if sense == '<':
                new_model += lhs <= rhs, name
            elif sense == '>':
                new_model += lhs >= rhs, name
            else:
                new_model += lhs == rhs, name

        new_model.solve()
        novo_valor_objetivo = pulp.value(new_model.objective)
        valor_original = pulp.value(self.model.objective)

        return {
            "novo_valor_objetivo": novo_valor_objetivo,
            "melhora": novo_valor_objetivo - valor_original,
            "pode_aumentar": novo_valor_objetivo >= valor_original
        }
