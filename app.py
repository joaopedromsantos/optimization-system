import streamlit as st
from pulp import LpStatusOptimal, LpStatusInfeasible, LpStatusUnbounded, LpStatusUndefined, LpMaximize, LpMinimize
from linear_optimization import Optimizer

# --- Configuração da Página ---
st.set_page_config(
    page_title="Sistema de Otimização Linear",
    page_icon="📊",
    layout="wide"
)

# --- CSS Customizado ---
st.markdown("""
<style>
    .section-header {
        padding: 0.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
        text-align: center;
        font-weight: bold;
    }
    .blue-header { background-image: linear-gradient(to right, #4e54c8, #8f94fb); }
    .green-header { background-image: linear-gradient(to right, #1d976c, #93f9b9); }
    .purple-header { background-image: linear-gradient(to right, #8e2de2, #4a00e0); }
    .red-header { background-image: linear-gradient(to right, #ff416c, #ff4b2b); }
</style>
""", unsafe_allow_html=True)

st.title("Sistema de Programação Linear")
st.markdown("Esta ferramenta de otimização ajudará você a tomar as melhores decisões. Forneça o número de variáveis e restrições, a função objetivo e as restrições para encontrar a solução ideal e analisar os preços sombra.")
st.write("---")

st.markdown('<div class="section-header blue-header"><h4>Configuração do Problema</h4></div>', unsafe_allow_html=True)

if 'num_vars' not in st.session_state:
    st.session_state.num_vars = 2
if 'num_restrs' not in st.session_state:
    st.session_state.num_restrs = 2

col1, col2, col3 = st.columns(3)
with col1:
    num_vars = st.number_input("Número de Variáveis", min_value=2, key="num_vars")
with col2:
    num_restrs = st.number_input("Número de Restrições", min_value=1, key="num_restrs")
with col3:
    st.radio(
        "Tipo de Otimização",
        ["Maximizar", "Minimizar"],
        key="objective_sense",
        horizontal=True, # Deixa os botões lado a lado
    )

# Função Objetivo
st.markdown(f'<div class="section-header green-header"><h4>Função Objetivo ({st.session_state.objective_sense})</h4></div>', unsafe_allow_html=True)
with st.container(border=True):
    cols_fo = st.columns(st.session_state.num_vars)
    variable_names = []
    for i in range(st.session_state.num_vars):
        with cols_fo[i]:
            var_name = st.text_input(f"Nome da Variável", value=f"x{i + 1}", key=f"var_name_{i}")
            variable_names.append(var_name)
            st.number_input(f"Coeficiente F.O.", key=f"c_{i}", value=0)

# Restrições
st.markdown('<div class="section-header purple-header"><h4>Restrições</h4></div>', unsafe_allow_html=True)
for i in range(st.session_state.num_restrs):
    with st.expander(f"**Configurar Restrição: R{i + 1}**"):
        st.write("**Coeficientes das Variáveis:**")
        cols_vars = st.columns(st.session_state.num_vars)
        for j, name in enumerate(variable_names):
            with cols_vars[j]:
                st.number_input(label=name, key=f"a_{i}_{j}", format="%.2f", value=0.0)
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Operador", ["<=", ">=", "=="], key=f"op_{i}")
        with col2:
            st.number_input("Lado Direito (LD)", key=f"b_{i}", format="%.2f", value=0.0)

# Botão Calcular
if st.button("Calcular Otimização", type="primary", use_container_width=True):
    sense_map = {
        "Maximizar": LpMaximize,
        "Minimizar": LpMinimize
    }
    selected_sense = sense_map[st.session_state.objective_sense]

    optimizer = Optimizer(num_vars, sense=selected_sense)

    coef_fo = [st.session_state[f"c_{i}"] for i in range(num_vars)]
    optimizer.set_objective_function(coef_fo)

    for i in range(num_restrs):
        coef_rest = [st.session_state[f"a_{i}_{j}"] for j in range(num_vars)]
        rhs = st.session_state[f"b_{i}"]
        sense = st.session_state[f"op_{i}"]
        optimizer.add_constraint(coef_rest, rhs, f"R{i+1}", sense)

    resultados = optimizer.solve()
    st.session_state.resultados = resultados
    st.session_state.optimizer = optimizer  # <-- ESSENCIAL
    st.session_state.show_results = True

# Resultados
if st.session_state.get('show_results', False):
    st.write("---")
    st.markdown('<div class="section-header green-header"><h2>Resultados da Otimização</h2></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.subheader("Valores Ótimos")
            for i in range(num_vars):
                var_name = variable_names[i]
                val = st.session_state.resultados["valores_otimos"][i]
                st.metric(label=f"{var_name}*", value=f"{val:.2f}")

    with col2:
        resultados = st.session_state.get("resultados", None)

        if resultados:
            status = resultados["viavel"]

            # Exibe o Valor Ótimo (Z*) apenas se a solução for ótima
            if status == LpStatusOptimal:
                with st.container(border=True):
                    st.subheader("Valor Ótimo (Z*)")
                    z = resultados["valor_objetivo"]
                    st.metric(label="Z*", value=f"{z:.2f}")

            # Exibe a mensagem de STATUS correspondente
            with st.container(border=True):
                st.subheader("Status da Solução")

                if status == LpStatusOptimal:
                    st.success("Solução Viável")

                elif status == LpStatusInfeasible:
                    st.error("Solução Inviável")

                elif status == LpStatusUnbounded:
                    st.warning("Solução Ilimitada")

                elif status == LpStatusUndefined:
                    st.error("Solução Indefinida")

    with col3:
        with st.container(border=True):
            st.subheader("Preços Sombra")
            for i in range(num_restrs):
                ps = st.session_state.resultados["precos_sombra"][i]
                st.metric(label=f"PS (R{i+1})", value=f"{ps:.2f}")
    st.markdown("---")
    st.markdown('<div class="section-header red-header"><h4>Análise de Aumento de Recurso (Delta)</h4></div>',
                unsafe_allow_html=True)

    constr_to_increase = st.selectbox("Selecione a restrição para aumentar",
                                      options=[f"R{i + 1}" for i in range(num_restrs)])
    delta_val = st.number_input("Quanto deseja aumentar o recurso?", min_value=0.0, format="%.2f")

    if st.button("Simular aumento de recurso"):
        constr_index = int(constr_to_increase[1:]) - 1
        optimizer = st.session_state.optimizer
        delta_result = optimizer.analyze_delta(constr_index, delta_val)
        st.metric("Novo Valor Objetivo Estimado", f"{delta_result['novo_valor_objetivo']:.2f}")
        st.metric("Melhora no Lucro", f"{delta_result['melhora']:.2f}")
        if delta_result["pode_aumentar"]:
            st.success("Aumento viável e traz melhora.")
        else:
            st.warning("Aumento pode não ser viável ou não traz melhora.")