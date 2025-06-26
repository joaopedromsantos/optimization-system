from streamlit.testing.v1 import AppTest


def run_optimization_test(num_vars: int, num_restrs: int, objective_coeffs: list, constraints: list,
                          objective_sense: str = "Maximizar") -> AppTest:

    at = AppTest.from_file("app.py", default_timeout=30).run()

    # --- Configuração dos Inputs ---
    at.number_input(key="num_vars").set_value(num_vars).run()
    at.number_input(key="num_restrs").set_value(num_restrs).run()

    # Define o tipo de otimização (Maximizar/Minimizar)
    at.radio(key="objective_sense").set_value(objective_sense).run()

    # Preenche a Função Objetivo
    for i, coeff in enumerate(objective_coeffs):
        at.number_input(key=f"c_{i}").set_value(coeff)

    # Preenche as Restrições
    for i, constraint in enumerate(constraints):
        for j, coeff in enumerate(constraint['coeffs']):
            at.number_input(key=f"a_{i}_{j}").set_value(coeff)
        at.selectbox(key=f"op_{i}").select(constraint['op'])
        at.number_input(key=f"b_{i}").set_value(constraint['rhs'])

    # Clica no botão para calcular
    at.button[0].click().run()

    return at

def test_caso_minimizacao_classico_2_variaveis_2_restricoes():
    """
    Testa o problema: Min Z = 2x₁ + 3x₂
    Sujeito a:
    1x₁ + 3x₂ >= 6
    2x₁ + 1x₂ >= 4
    """
    at = run_optimization_test(
        num_vars=2,
        num_restrs=2,
        objective_coeffs=[2, 3],
        constraints=[
            {'coeffs': [1, 3], 'op': '>=', 'rhs': 6},
            {'coeffs': [2, 1], 'op': '>=', 'rhs': 4},
        ],
        objective_sense="Minimizar"
    )

    # --- Verificação dos Resultados ---
    assert at.metric[0].value == "1.20"
    assert at.metric[1].value == "1.60"

    assert at.metric[2].value == "7.20"
    assert at.success[0].value == "Solução Viável"

    assert at.metric[3].value == "0.80"
    assert at.metric[4].value == "0.60"

def test_caso_minimizacao_3_variaveis_5_restricoes():
    """
    Testa o problema: Min Z = 5x₁ + 4x₂ + 3x₃
    Sujeito a:
    2x₁ + 3x₂ + 1x₃ >= 80
    4x₁ + 2x₂ + 1x₃ >= 60
    1x₁ + 1x₂ + 2x₃ >= 50
    1x₁ <= 100  (Restrição não limitante)
    1x₂ <= 100  (Restrição não limitante)
    """
    at = run_optimization_test(
        num_vars=3,
        num_restrs=5,
        objective_coeffs=[5, 4, 3],
        constraints=[
            {'coeffs': [2, 3, 1], 'op': '>=', 'rhs': 80},
            {'coeffs': [4, 2, 1], 'op': '>=', 'rhs': 60},
            {'coeffs': [1, 1, 2], 'op': '>=', 'rhs': 50},
            {'coeffs': [1, 0, 0], 'op': '<=', 'rhs': 100},
            {'coeffs': [0, 1, 0], 'op': '<=', 'rhs': 100},
        ],
        objective_sense="Minimizar"
    )

    # --- Verificação dos Resultados ---
    assert at.metric[0].value == "0.77"
    assert at.metric[1].value == "21.54"
    assert at.metric[2].value == "13.85"

    assert at.metric[3].value == "131.54"
    assert at.success[0].value == "Solução Viável"

    assert at.metric[4].value == "0.54"
    assert at.metric[5].value == "0.77"
    assert at.metric[6].value == "0.85"
    assert at.metric[7].value == "0.00"
    assert at.metric[8].value == "0.00"

def test_caso_otimo_classico_2_variaveis_2_restricoes():
    """
    Testa o problema: Max Z = 40x₁ + 30x₂
    Sujeito a:
    1x₁ + 2x₂ <= 16
    3x₁ + 2x₂ <= 24
    """
    at = run_optimization_test(
        num_vars=2,
        num_restrs=2,
        objective_coeffs=[40, 30],
        constraints=[
            {'coeffs': [1, 2], 'op': '<=', 'rhs': 16},
            {'coeffs': [3, 2], 'op': '<=', 'rhs': 24},
        ]
    )

    # --- Verificação dos Resultados ---
    assert at.metric[0].value == "4.00"
    assert at.metric[1].value == "6.00"

    assert at.metric[2].value == "340.00"
    assert at.success[0].value == "Solução Viável"

    assert at.metric[3].value == "2.50"
    assert at.metric[4].value == "12.50"

def test_caso_otimo_classico_2_variaveis_3_restricoes(capfd):
    """
    Testa o problema: Max Z = 3x₁ + 5x₂
    Sujeito a:
    1x₁ + 0x₂ <= 4
    0x₁ + 2x₂ <= 12
    3x₁ + 2x₂ <= 18
    """

    at = run_optimization_test(
        num_vars=2,
        num_restrs=3,
        objective_coeffs=[3, 5],
        constraints=[
            {'coeffs': [1, 0], 'op': '<=', 'rhs': 4},
            {'coeffs': [0, 2], 'op': '<=', 'rhs': 12},
            {'coeffs': [3, 2], 'op': '<=', 'rhs': 18},
        ]
    )

    # --- Verificação dos Resultados ---
    assert at.metric[0].value == "2.00"
    assert at.metric[1].value == "6.00"

    assert at.metric[2].value == "36.00"
    assert at.success[0].value == "Solução Viável"

    assert at.metric[3].value == "-0.00"
    assert at.metric[4].value == "1.50"
    assert at.metric[5].value == "1.00"
    assert len(at.error) == 0 and len(at.warning) == 0


def test_caso_otimo_classico_3_variaveis_2_restricoes():
    """
    Testa o problema: Max Z = 3x₁ + 2x₂ + 5x₃
    Sujeito a:
    1x₁ + 2x₂ + 1x₃ <= 10
    3x₁ + 0x₂ + 2x₃ <= 12
    """
    at = run_optimization_test(
        num_vars=3,
        num_restrs=2,
        objective_coeffs=[3, 2, 5],
        constraints=[
            {'coeffs': [1, 2, 1], 'op': '<=', 'rhs': 10},
            {'coeffs': [3, 0, 2], 'op': '<=', 'rhs': 12},
        ]
    )

    # --- Verificação dos Resultados ---
    assert at.metric[0].value == "0.00"
    assert at.metric[1].value == "2.00"
    assert at.metric[2].value == "6.00"

    assert at.metric[3].value == "34.00"
    assert at.success[0].value == "Solução Viável"

    assert at.metric[4].value == "1.00"
    assert at.metric[5].value == "2.00"


def test_caso_otimo_classico_3_variaveis_3_restricoes():
    """
    Testa o problema: Max Z = 3x₁ + 2x₂ + 5x₃
    Sujeito a:
    1x₁ + 2x₂ + 1x₃ <= 430
    3x₁ + 0x₂ + 2x₃ <= 460
    1x₁ + 4x₂ + 0x₃ <= 420
    """
    at = run_optimization_test(
        num_vars=3,
        num_restrs=3,
        objective_coeffs=[3, 2, 5],
        constraints=[
            {'coeffs': [1, 2, 1], 'op': '<=', 'rhs': 430},
            {'coeffs': [3, 0, 2], 'op': '<=', 'rhs': 460},
            {'coeffs': [1, 4, 0], 'op': '<=', 'rhs': 420},
        ]
    )

    # --- Verificação dos Resultados ---
    assert at.metric[0].value == "0.00"
    assert at.metric[1].value == "100.00"
    assert at.metric[2].value == "230.00"

    assert at.metric[3].value == "1350.00"
    assert at.success[0].value == "Solução Viável"

    assert at.metric[4].value == "1.00"
    assert at.metric[5].value == "2.00"
    assert at.metric[6].value == "-0.00"


def test_caso_otimo_classico_4_variaveis_4_restricoes():
    """
    Testa o problema: Max Z = 8x₁ + 10x₂ + 7x₃ + 6x₄
    Sujeito a:
    2x₁ + 3x₂ + 2x₃ + 1x₄ <= 20
    1x₁ + 2x₂ + 3x₃ + 2x₄ <= 25
    3x₁ + 1x₂ + 2x₃ + 3x₄ <= 30
    1x₁ + 1x₂ + 1x₃ + 1x₄ <= 15
    """
    at = run_optimization_test(
        num_vars=4,
        num_restrs=4,
        objective_coeffs=[8, 10, 7, 6],
        constraints=[
            {'coeffs': [2, 3, 2, 1], 'op': '<=', 'rhs': 20},
            {'coeffs': [1, 2, 3, 2], 'op': '<=', 'rhs': 25},
            {'coeffs': [3, 1, 2, 3], 'op': '<=', 'rhs': 30},
            {'coeffs': [1, 1, 1, 1], 'op': '<=', 'rhs': 15},
        ]
    )

    # --- Verificação dos Resultados ---
    assert at.metric[0].value == "0.00"
    assert at.metric[1].value == "3.75"
    assert at.metric[2].value == "0.00"
    assert at.metric[3].value == "8.75"

    assert at.metric[4].value == "90.00"
    assert at.success[0].value == "Solução Viável"

    assert at.metric[5].value == "3.00"
    assert at.metric[6].value == "-0.00"
    assert at.metric[7].value == "1.00"
    assert at.metric[8].value == "-0.00"


def test_caso_otimo_classico_5_variaveis_8_restricoes():
    """
    Testa um problema de 5 variáveis e 8 restrições com uma solução simples.
    Max Z = x₁ + x₂ + x₃ + x₄ + x₅
    Sujeito a xᵢ <= 1 para i=1..5, e outras 3 restrições não-limitantes.
    """
    at = run_optimization_test(
        num_vars=5,
        num_restrs=8,
        objective_coeffs=[1, 1, 1, 1, 1],
        constraints=[
            {'coeffs': [1, 0, 0, 0, 0], 'op': '<=', 'rhs': 1},
            {'coeffs': [0, 1, 0, 0, 0], 'op': '<=', 'rhs': 1},
            {'coeffs': [0, 0, 1, 0, 0], 'op': '<=', 'rhs': 1},
            {'coeffs': [0, 0, 0, 1, 0], 'op': '<=', 'rhs': 1},
            {'coeffs': [0, 0, 0, 0, 1], 'op': '<=', 'rhs': 1},
            {'coeffs': [1, 1, 0, 0, 0], 'op': '<=', 'rhs': 10},
            {'coeffs': [0, 0, 1, 1, 0], 'op': '<=', 'rhs': 10},
            {'coeffs': [0, 0, 0, 0, 1], 'op': '<=', 'rhs': 10},
        ]
    )

    # --- Verificação dos Resultados ---
    assert at.metric[0].value == "1.00"
    assert at.metric[1].value == "1.00"
    assert at.metric[2].value == "1.00"
    assert at.metric[3].value == "1.00"
    assert at.metric[4].value == "1.00"

    assert at.metric[5].value == "5.00"
    assert at.success[0].value == "Solução Viável"

    assert at.metric[6].value == "1.00"
    assert at.metric[7].value == "1.00"
    assert at.metric[8].value == "1.00"
    assert at.metric[9].value == "1.00"
    assert at.metric[10].value == "1.00"
    assert at.metric[11].value == "-0.00"
    assert at.metric[12].value == "-0.00"
    assert at.metric[13].value == "-0.00"


def test_caso_inviavel():
    at = run_optimization_test(
        num_vars=2,
        num_restrs=2,
        objective_coeffs=[1, 1],
        constraints=[
            {'coeffs': [1, 1], 'op': '<=', 'rhs': 2},
            {'coeffs': [1, 1], 'op': '>=', 'rhs': 5},
        ]
    )

    # --- Verificação dos Resultados ---
    assert at.error[0].value == "Solução Inviável"


def test_caso_ilimitado():
    at = run_optimization_test(
        num_vars=2,
        num_restrs=1,
        objective_coeffs=[2, 1],
        constraints=[
            {'coeffs': [1, -1], 'op': '<=', 'rhs': 10},
        ]
    )

    # --- Verificação dos Resultados ---
    assert at.warning[0].value == "Solução Ilimitada"

