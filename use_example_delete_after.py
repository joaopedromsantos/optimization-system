from linear_optimization import Optimizer
# --- Dados do Problema ---
# Variáveis: x1=T, x2=M, x3=C. Portanto, são 3 variáveis.
NUM_VARS = 3

# Função Objetivo: 3*x1 + 2*x2 + 5*x3
COEFS_OBJETIVO = [3, 2, 5]

# Restrições:
# 1*x1 + 3*x2 + 1*x3 <= 430
# 2*x1 + 0*x2 + 4*x3 <= 460
# 1*x1 + 2*x2 + 0*x3 <= 420
RESTRICOES = [
    {"coefs": [1, 3, 1], "rhs": 430, "nome": "Recurso_A", "sense": "<="},
    {"coefs": [2, 0, 4], "rhs": 460, "nome": "Recurso_B", "sense": "<="},
    {"coefs": [1, 2, 0], "rhs": 420, "nome": "Recurso_C", "sense": "<="}
]

# 1. Inicializar o otimizador com 3 variáveis para maximização
optimizer = Optimizer(num_variables=NUM_VARS)

# 2. Definir a função objetivo
optimizer.set_objective_function(COEFS_OBJETIVO)

# 3. Adicionar as restrições a partir da lista
for r in RESTRICOES:
    optimizer.add_constraint(coefficients=r["coefs"], rhs=r["rhs"], name=r["nome"], sense=r["sense"])

# 4. Resolver o problema
optimizer.solve()
