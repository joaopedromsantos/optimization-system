import streamlit as st

# --- Configuração da Página ---
st.set_page_config(
    page_title="Sistema de Otimização Linear",
    page_icon="📊",
    layout="wide"
)

# --- CSS Customizado para Deixar Mais Bonito ---
st.markdown("""
<style>
    /* Estilo dos headers das seções */
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

# --- Título e Descrição ---
st.title("Sistema de Programação Linear")
st.markdown("Esta ferramenta de otimização ajudará você a tomar as melhores decisões. Forneça o número de variáveis e número de restrições, a função objetivo e as restrições para encontrar a solução ideal e analisar os preços sombra.")
st.write("---")

# --- Interface do Usuário ---

# 1. Configuração do Problema
st.markdown('<div class="section-header blue-header"><h4>Configuração do Problema</h4></div>', unsafe_allow_html=True)

if 'num_vars' not in st.session_state:
    st.session_state.num_vars = 2
if 'num_restrs' not in st.session_state:
    st.session_state.num_restrs = 2

col1, col2 = st.columns(2)
with col1:
    num_vars = st.number_input("Número de Variáveis", min_value=2, key="num_vars")
with col2:
    num_restrs = st.number_input("Número de Restrições", min_value=1, key="num_restrs")

# 2. Função Objetivo
st.markdown('<div class="section-header green-header"><h4>Função Objetivo (Maximização)</h4></div>',
            unsafe_allow_html=True)

with st.container(border=True):
    cols_fo = st.columns(st.session_state.num_vars)
    variable_names = []
    for i in range(st.session_state.num_vars):
        with cols_fo[i]:
            var_name = st.text_input(f"Nome da Variável", value=f"x{i + 1}", key=f"var_name_{i}")
            variable_names.append(var_name)
            st.number_input(f"Coeficiente F.O.", key=f"c_{i}", value=0)

# 3. Restrições (LAYOUT ALTERNATIVO COM EXPANDERS)
st.markdown('<div class="section-header purple-header"><h4>Restrições</h4></div>', unsafe_allow_html=True)

for i in range(st.session_state.num_restrs):
    with st.expander(f"**Configurar Restrição: R{i + 1}**"):

        st.write("**Coeficientes das Variáveis:**")
        cols_vars = st.columns(st.session_state.num_vars)
        for j, name in enumerate(variable_names):
            with cols_vars[j]:
                st.number_input(label=name, key=f"a_{i}_{j}", format="%.2f", value=0.0)

        st.divider()

        st.write("**Condição da Restrição:**")
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Operador", ["<=", ">=", "="], key=f"op_{i}")
        with col2:
            st.number_input("Lado Direito (LD)", key=f"b_{i}", format="%.2f", value=0.0)

# --- Botão para "Calcular" ---
if st.button("Calcular Otimização", type="primary", use_container_width=True):
    #
    #
    # CHAMADA PARA A FUNÇÃO DE OTIMIZAÇÃO AQUI
    #
    #
    st.session_state.show_results = True

# --- Seção de Resultados ---
if st.session_state.get('show_results', False):
    st.write("---")
    st.markdown('<div class="section-header green-header"><h2>Resultados da Otimização</h2></div>',
                unsafe_allow_html=True)

    st.info("Os valores abaixo são exemplos dinâmicos para fins de prototipagem.")

    col1, col2, col3 = st.columns(3)

    # Card 1: Valores Ótimos
    with col1:
        with st.container(border=True):
            st.subheader("Valores Ótimos")
            # Loop baseado no número de variáveis
            for i in range(st.session_state.num_vars):
                # Pega o nome da variável que o usuário digitou
                var_name = st.session_state.get(f'var_name_{i}', f'x{i+1}')
                # Cria um st.metric para cada variável com um valor de exemplo
                st.metric(label=f"{var_name}*", value=f"TROCAR")

    # Card 2: Lucro Máximo
    with col2:
        with st.container(border=True):
            st.subheader("Valor Ótimo (Z*)")
            st.metric(label="Z*", value=f"TROCAR")
            st.success("Solução Viável")

    # Card 3: Preços Sombra
    with col3:
        with st.container(border=True):
            st.subheader("Preços Sombra")
            for i in range(st.session_state.num_restrs):
                restr_name = st.session_state.get(f'restr_name_{i}', f'R{i+1}')
                st.metric(label=f"PS ({restr_name})", value=f"TROCAR")
