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
        # CORREÇÃO: Nome do problema mais genérico
        self.model = pulp.LpProblem("Problema_Otimizacao", sense)
        self.variables = [pulp.LpVariable(f'x{i + 1}', lowBound=0, cat='Continuous')
                          for i in range(num_variables)]
        self.coef_fo = None
        # Armazena os dados das restrições para uso posterior na análise de sensibilidade
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
            sense (str): Operador da restrição ('<=', '>=', ou '==').
        """
        # Armazena os detalhes da restrição para poder recriá-la depois
        self.constraints_data.append((coefficients, rhs, sense, name))

        lhs = pulp.lpSum([coefficients[i] * self.variables[i] for i in range(self.num_variables)])

        if sense == '<=':
            self.model += lhs <= rhs, name
        elif sense == '>=':
            self.model += lhs >= rhs, name
        elif sense == '==':
            self.model += lhs == rhs, name

    def solve(self):
        """
        Resolve o problema de otimização.
        Retorna:
            dict: Um dicionário contendo os resultados da otimização.
        """
        # Usar o solver padrão do PuLP. Pode ser trocado se necessário (ex: CBC, GLPK)
        self.model.solve()

        # Extrai os resultados
        valores_otimos = [v.varValue if v.varValue is not None else 0 for v in self.variables]
        valor_objetivo = pulp.value(self.model.objective) if self.model.status == pulp.LpStatusOptimal else 0

        # O preço sombra (dual value) só é significativo em soluções ótimas
        precos_sombra = []
        if self.model.status == pulp.LpStatusOptimal:
            precos_sombra = [c.pi if c.pi is not None else 0 for c in self.model.constraints.values()]
        else:
            # Se não for ótimo, preenche com zeros para manter a estrutura de dados
            precos_sombra = [0] * len(self.model.constraints)

        viavel = self.model.status

        return {
            "valores_otimos": valores_otimos,
            "valor_objetivo": valor_objetivo,
            "precos_sombra": precos_sombra,
            "viavel": viavel
        }

    def analyze_delta(self, constr_index, delta_b):
        """
        Analisa o impacto de um aumento (delta) no lado direito de uma restrição.
        Recria e resolve o modelo com o novo valor para encontrar o impacto.

        Args:
            constr_index (int): O índice da restrição a ser modificada.
            delta_b (float): O valor a ser adicionado ao RHS da restrição.

        Retorna:
            dict: Um dicionário com os resultados da simulação.
        """
        # Captura o valor objetivo original antes da simulação
        valor_original = pulp.value(self.model.objective)
        if valor_original is None:
            # Se o problema original não tinha solução, a análise não faz sentido
            return {
                "novo_valor_objetivo": 0,
                "melhora": 0,
                "pode_aumentar": False
            }

        new_model = pulp.LpProblem("Analise_Sensibilidade", self.model.sense)
        new_vars = [pulp.LpVariable(f'x{i + 1}', lowBound=0, cat='Continuous') for i in range(self.num_variables)]

        # Recria a Função Objetivo
        expression = pulp.lpSum([self.coef_fo[i] * new_vars[i] for i in range(self.num_variables)])
        new_model += expression, "Objective_Function_Delta"

        # Recria as restrições, aumentando o RHS da restrição especificada
        for i, (coef_rest, rhs, sense, name) in enumerate(self.constraints_data):
            lhs = pulp.lpSum([coef_rest[j] * new_vars[j] for j in range(self.num_variables)])

            # Aplica o delta na restrição selecionada
            current_rhs = rhs
            if i == constr_index:
                current_rhs += delta_b


            if sense == '<=':
                new_model += lhs <= current_rhs, name
            elif sense == '>=':
                new_model += lhs >= current_rhs, name
            elif sense == '==':
                new_model += lhs == current_rhs, name

        # Resolve o novo modelo e lida com possíveis falhas
        new_model.solve()

        # Verifica se o novo modelo tem uma solução ótima
        if new_model.status == pulp.LpStatusOptimal:
            novo_valor_objetivo = pulp.value(new_model.objective)
        else:
            # Se a simulação resultar em inviabilidade/etc, considera que não houve melhora.
            novo_valor_objetivo = valor_original

        pode_aumentar = False
        if self.model.sense == pulp.LpMaximize:
            # Para MAX, melhora é um valor maior ou igual
            pode_aumentar = novo_valor_objetivo >= valor_original
        else:  # pulp.LpMinimize
            # Para MIN, melhora é um valor menor ou igual
            pode_aumentar = novo_valor_objetivo <= valor_original

        return {
            "novo_valor_objetivo": novo_valor_objetivo,
            "melhora": novo_valor_objetivo - valor_original,
            "pode_aumentar": pode_aumentar
        }
