import pulp


class Optimizer:
    """
    Classe para encapsular a lógica de otimização linear usando a biblioteca PuLP.
    """

    def __init__(self, num_variables, sense=pulp.LpMaximize):
        """
        Inicializa o otimizador.
        Args:
            num_variables (int): O número de variáveis de decisão.
            sense (pulp.LpMaximize ou pulp.LpMinimize): O sentido da otimização.
        """
        self.num_variables = num_variables
        self.model = pulp.LpProblem("Problema_Otimizacao", sense)
        self.variables = [pulp.LpVariable(f'x{i + 1}', lowBound=0, cat='Continuous')
                          for i in range(num_variables)]
        self.coef_fo = None
        # Armazena os dados das restrições para uso posterior
        self.constraints_data = []

    def set_objective_function(self, coefficients):
        """
        Define a função objetivo do modelo.
        Args:
            coefficients (list): Lista de coeficientes para cada variável na F.O.
        """
        self.coef_fo = coefficients
        expression = pulp.lpSum([coefficients[i] * self.variables[i] for i in range(self.num_variables)])
        self.model += expression, "Objective_Function"

    def add_constraint(self, coefficients, rhs, name, sense):
        """
        Adiciona uma restrição ao modelo.
        Args:
            coefficients (list): Coeficientes das variáveis no lado esquerdo (LHS).
            rhs (float): Valor do lado direito (RHS).
            name (str): Nome da restrição.
            sense (str): Operador da restrição ('<=', '>=').
        """
        self.constraints_data.append((coefficients, rhs, sense, name))

        lhs = pulp.lpSum([coefficients[i] * self.variables[i] for i in range(self.num_variables)])

        if sense == '<=':
            self.model += lhs <= rhs, name
        elif sense == '>=':
            self.model += lhs >= rhs, name

    def solve(self):
        """
        Resolve o problema de otimização.
        Retorna:
            dict: Um dicionário contendo os resultados da otimização.
        """
        self.model.solve()

        is_optimal = self.model.status == pulp.LpStatusOptimal

        valores_otimos = [v.varValue if v.varValue is not None else 0 for v in self.variables]
        valor_objetivo = pulp.value(self.model.objective) if is_optimal else 0

        precos_sombra = []
        if is_optimal:
            precos_sombra = [c.pi if c.pi is not None else 0 for c in self.model.constraints.values()]
        else:
            precos_sombra = [0] * len(self.model.constraints)

        return {
            "valores_otimos": valores_otimos,
            "valor_objetivo": valor_objetivo,
            "precos_sombra": precos_sombra,
            "viavel": self.model.status
        }

    def analyze_delta(self, constr_index, delta_b):
        """
        Analisa o impacto de um aumento (delta) no lado direito de uma restrição.
        Usa o método `copy()` para clonar o modelo original e aplicar a mudança,
        que é uma abordagem mais robusta e eficiente.

        Args:
            constr_index (int): O índice da restrição a ser modificada.
            delta_b (float): O valor a ser adicionado ao RHS da restrição.

        Retorna:
            dict: Um dicionário com os resultados da simulação.
        """
        # Só realiza a análise se o modelo original tiver uma solução ótima
        if self.model.status != pulp.LpStatusOptimal:
            return {
                "novo_valor_objetivo": 0,
                "melhora": 0,
                "pode_aumentar": False
            }

        valor_original = pulp.value(self.model.objective)

        new_model = self.model.copy()

        # Pega o nome da restrição que queremos alterar
        # O quarto elemento da tupla é o nome que demos em `add_constraint`
        constr_name = self.constraints_data[constr_index][3]

        # Pega a restrição correspondente no NOVO modelo clonado
        constraint_to_modify = new_model.constraints[constr_name]

        # PuLP move o RHS para o lado esquerdo da equação (ex: x <= 10 se torna x - 10 <= 0).
        # Para aumentar o RHS em `delta_b`, precisamos subtrair `delta_b` da constante.
        constraint_to_modify.constant += -delta_b

        # Resolve o modelo clonado e modificado
        new_model.solve()

        novo_valor_objetivo = valor_original
        is_viable_and_better = False

        # Verifica se a simulação resultou em uma solução ótima
        if new_model.status == pulp.LpStatusOptimal:
            novo_valor_objetivo = pulp.value(new_model.objective)

            # Lógica de melhora depende do sentido da otimização
            if self.model.sense == pulp.LpMaximize:
                # Para MAX, melhora é um valor maior ou igual
                is_viable_and_better = novo_valor_objetivo >= valor_original
            else:  # pulp.LpMinimize
                # Para MIN, melhora é um valor menor ou igual
                is_viable_and_better = novo_valor_objetivo <= valor_original

        return {
            "novo_valor_objetivo": novo_valor_objetivo,
            "melhora": novo_valor_objetivo - valor_original,
            "pode_aumentar": is_viable_and_better
        }
