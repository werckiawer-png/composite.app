"""
Aplicativo Streamlit para Micromecânica de Compósitos UD
Versão com modo manual e chatbot Gemini - COM HISTÓRICO DE CONVERSA
"""

import streamlit as st
import pandas as pd
import numpy as np
from models import rom, reuss, halpin_tsai
from utils.plotting import plot_all_properties
import google.generativeai as genai

# ============================================
# CONFIGURAÇÃO DA API GEMINI
# ============================================
# A chave será lida do arquivo .streamlit/secrets.toml
# NÃO COLOQUE A CHAVE AQUI!
API_KEY = st.secrets["gemini"]["api_key"]

# Inicializar o cliente Gemini
if 'chat_model' not in st.session_state:
    try:
        genai.configure(api_key=API_KEY)
        st.session_state.chat_model = genai.GenerativeModel('gemini-2.5-flash')
        st.session_state.chat_initialized = True
        st.session_state.chat_error = None
    except Exception as e:
        st.session_state.chat_initialized = False
        st.session_state.chat_error = str(e)

# Inicializar histórico de chat se não existir
if 'mensagens_chat' not in st.session_state:
    st.session_state.mensagens_chat = []

# Configurar a página
st.set_page_config(
    page_title="Micromecânica de Compósitos - Monografia",
    page_icon="📚",
    layout="wide"
)

# Título principal
st.title("📚 Ferramenta Computacional para Micromecânica de Compósitos Unidirecionais")
st.markdown("*Desenvolvido para pesquisa de mestrado*")
st.markdown("---")

# Carregar dados
@st.cache_data
def carregar_dados():
    fibras = pd.read_csv('data/fibras.csv')
    matrizes = pd.read_csv('data/matrizes.csv')
    return fibras, matrizes

fibras, matrizes = carregar_dados()

# Sidebar com controles
st.sidebar.header("⚙️ Parâmetros de Entrada")

modo_entrada = st.sidebar.radio(
    "Modo de entrada",
    ["📚 Usar biblioteca", "✏️ Digitar manualmente"],
    help="Escolha entre selecionar materiais da biblioteca ou digitar propriedades manualmente"
)

st.sidebar.markdown("---")

if modo_entrada == "📚 Usar biblioteca":
    fibra_nome = st.sidebar.selectbox(
        "Fibra",
        fibras['nome'].tolist(),
        help="Selecione o tipo de fibra"
    )
    
    matriz_nome = st.sidebar.selectbox(
        "Matriz",
        matrizes['nome'].tolist(),
        help="Selecione o tipo de matriz"
    )
    
    fibra = fibras[fibras['nome'] == fibra_nome].iloc[0].to_dict()
    matriz = matrizes[matrizes['nome'] == matriz_nome].iloc[0].to_dict()
    
else:  # Modo manual
    st.sidebar.subheader("Propriedades da Fibra")
    E1_f_manual = st.sidebar.number_input("E₁ᶠ (GPa)", min_value=0.1, max_value=1000.0, value=225.0, step=1.0)
    E2_f_manual = st.sidebar.number_input("E₂ᶠ (GPa)", min_value=0.1, max_value=1000.0, value=15.0, step=1.0)
    G12_f_manual = st.sidebar.number_input("G₁₂ᶠ (GPa)", min_value=0.1, max_value=500.0, value=15.0, step=1.0)
    nu_f_manual = st.sidebar.number_input("ν₁₂ᶠ", min_value=0.01, max_value=0.5, value=0.2, step=0.01, format="%.2f")
    
    st.sidebar.subheader("Propriedades da Matriz")
    E_m_manual = st.sidebar.number_input("Eᵐ (GPa)", min_value=0.1, max_value=500.0, value=4.8, step=0.1)
    nu_m_manual = st.sidebar.number_input("νᵐ", min_value=0.01, max_value=0.5, value=0.34, step=0.01, format="%.2f")
    
    fibra = {
        'E1_f (GPa)': E1_f_manual,
        'E2_f (GPa)': E2_f_manual,
        'G12_f (GPa)': G12_f_manual,
        'nu12_f': nu_f_manual
    }
    
    matriz = {
        'E_m (GPa)': E_m_manual,
        'nu_m': nu_m_manual
    }
    
    fibra_nome = "Manual"
    matriz_nome = "Manual"

Vf = st.sidebar.slider(
    "Fração Volumétrica de Fibra (Vf)",
    min_value=0.0, max_value=1.0, value=0.6, step=0.01
)

xi = st.sidebar.slider(
    "Fator de forma ξ (Halpin-Tsai)",
    min_value=0.1, max_value=10.0, value=2.0, step=0.1
)

Gm = matriz['E_m (GPa)'] / (2 * (1 + matriz['nu_m']))

# Alertas
st.sidebar.markdown("---")
st.sidebar.subheader("⚠️ Validação Física")

if Vf < 0.45:
    st.sidebar.warning("Vf abaixo da faixa prática (0.45-0.65)")
elif Vf > 0.65:
    st.sidebar.warning("Vf acima da faixa prática (0.45-0.65)")
else:
    st.sidebar.success("✅ Vf dentro da faixa prática (0.45-0.65)")

# Área principal
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📋 Resultados para Vf atual")
    
    resultados = {
        'Propriedade': ['E₁ (GPa)', 'E₂ (GPa)', 'G₁₂ (GPa)', 'ν₁₂'],
        'ROM': [
            f"{rom.E1(Vf, fibra['E1_f (GPa)'], matriz['E_m (GPa)']):.2f}",
            "—",
            "—",
            f"{rom.nu12(Vf, fibra['nu12_f'], matriz['nu_m']):.2f}"
        ],
        'Reuss': [
            "—",
            f"{reuss.E2(Vf, fibra['E2_f (GPa)'], matriz['E_m (GPa)']):.2f}",
            f"{reuss.G12(Vf, fibra['G12_f (GPa)'], Gm):.2f}",
            "—"
        ],
        'Halpin-Tsai': [
            "—",
            f"{halpin_tsai.E2(Vf, fibra['E2_f (GPa)'], matriz['E_m (GPa)'], xi):.2f}",
            f"{halpin_tsai.G12(Vf, fibra['G12_f (GPa)'], Gm, xi):.2f}",
            "—"
        ]
    }
    
    df_resultados = pd.DataFrame(resultados)
    st.dataframe(df_resultados, use_container_width=True)
    
    st.subheader("📌 Propriedades dos Constituintes")
    
    col1a, col1b = st.columns(2)
    with col1a:
        st.markdown(f"""
        **Fibra:** {fibra_nome}
        - E₁ᶠ = {fibra['E1_f (GPa)']} GPa
        - E₂ᶠ = {fibra['E2_f (GPa)']} GPa
        - G₁₂ᶠ = {fibra['G12_f (GPa)']} GPa
        - ν₁₂ᶠ = {fibra['nu12_f']}
        """)
    
    with col1b:
        st.markdown(f"""
        **Matriz:** {matriz_nome}
        - Eᵐ = {matriz['E_m (GPa)']} GPa
        - νᵐ = {matriz['nu_m']}
        - Gᵐ = {Gm:.2f} GPa
        """)

with col2:
    st.subheader("📈 Comparação dos Modelos")
    
    Vf_range = np.linspace(0, 1, 100)
    fig = plot_all_properties(Vf_range, fibra, matriz, xi)
    st.plotly_chart(fig, use_container_width=True)

# ============================================
# SEÇÃO DE FUNDAMENTAÇÃO TEÓRICA
# ============================================
st.markdown("---")
st.header("📖 Fundamentação Teórica")

tab1, tab2, tab3, tab4 = st.tabs([
    "Modelos Implementados", 
    "Interpretação dos Gráficos", 
    "Validação Física",
    "Referências"
])

with tab1:
    st.subheader("1. Regra das Misturas (ROM)")
    st.latex(r"E_1 = V_f E_{1f} + (1 - V_f) E_m")
    st.latex(r"\nu_{12} = V_f \nu_{12f} + (1 - V_f) \nu_m")
    st.markdown("**Hipótese:** Isodeformação longitudinal (Voigt). Excelente para E₁.")

    st.subheader("2. Modelo de Reuss")
    st.latex(r"\frac{1}{E_2} = \frac{V_f}{E_{2f}} + \frac{1 - V_f}{E_m}")
    st.latex(r"\frac{1}{G_{12}} = \frac{V_f}{G_{12f}} + \frac{1 - V_f}{G_m}")
    st.markdown("**Hipótese:** Isotensão transversal. Limite inferior para E₂ e G₁₂.")

    st.subheader("3. Modelo de Halpin-Tsai")
    st.latex(r"\eta = \frac{P_f/P_m - 1}{P_f/P_m + \xi}")
    st.latex(r"P = P_m \frac{1 + \xi \eta V_f}{1 - \eta V_f}")
    st.markdown("**Parâmetro ξ:** ξ=2 para fibras circulares. Valores intermediários realistas.")

with tab2:
    st.subheader("Regiões dos Gráficos")
    st.markdown("""
    - **Vf < 0.45:** Fração muito baixa para compósitos estruturais.
    - **Vf > 0.65:** Próximo ao limite de empacotamento de fibras (~0.74).
    """)

with tab3:
    st.subheader("Intervalos Físicos Válidos")
    st.markdown("""
    | Faixa Vf | Interpretação |
    |----------|----------------|
    | 0.00 - 0.30 | Fibras isoladas - não forma compósito estrutural |
    | 0.30 - 0.45 | Compósitos de baixo desempenho |
    | **0.45 - 0.65** | **Faixa prática para compósitos estruturais** |
    | 0.65 - 0.74 | Limite teórico de empacotamento |
    | > 0.74 | Fisicamente impossível |
    """)

with tab4:
    st.subheader("Referências")
    st.markdown("""
    1. JONES, R. M. *Mechanics of Composite Materials*. 1999.
    2. HALPIN, J. C.; KARDOS, J. L. *Polymer Engineering & Science*, 1976.
    3. HULL, D.; CLYNE, T. W. *An Introduction to Composite Materials*. 1996.
    """)

# ============================================
# SEÇÃO CHATBOT COM GEMINI (COM HISTÓRICO)
# ============================================
st.markdown("---")
st.header("🤖 Chat IA - Tire suas dúvidas sobre compósitos")

# Botão para novo chat
col_btn1, col_btn2 = st.columns([3, 1])
with col_btn2:
    if st.button("🗑️ Novo Chat", use_container_width=True):
        st.session_state.mensagens_chat = []
        st.rerun()

# Verificar conexão
if st.session_state.get('chat_initialized', False):
    
    # Contexto do app (atualizado a cada interação)
    contexto_base = f"""
    ### CONTEXTO ATUAL DO APLICATIVO:
    
    **Materiais:** {fibra_nome} + {matriz_nome}
    - Fibra: E₁ᶠ={fibra['E1_f (GPa)']} GPa, E₂ᶠ={fibra['E2_f (GPa)']} GPa, G₁₂ᶠ={fibra['G12_f (GPa)']} GPa, ν₁₂ᶠ={fibra['nu12_f']}
    - Matriz: Eᵐ={matriz['E_m (GPa)']} GPa, νᵐ={matriz['nu_m']}, Gᵐ={Gm:.2f} GPa
    
    **Parâmetros:** Vf={Vf:.2f}, ξ={xi:.2f}
    
    **Resultados atuais:**
    - E₁ = {rom.E1(Vf, fibra['E1_f (GPa)'], matriz['E_m (GPa)']):.2f} GPa
    - E₂ (Reuss) = {reuss.E2(Vf, fibra['E2_f (GPa)'], matriz['E_m (GPa)']):.2f} GPa
    - E₂ (HT) = {halpin_tsai.E2(Vf, fibra['E2_f (GPa)'], matriz['E_m (GPa)'], xi):.2f} GPa
    - G₁₂ (Reuss) = {reuss.G12(Vf, fibra['G12_f (GPa)'], Gm):.2f} GPa
    - G₁₂ (HT) = {halpin_tsai.G12(Vf, fibra['G12_f (GPa)'], Gm, xi):.2f} GPa
    - ν₁₂ = {rom.nu12(Vf, fibra['nu12_f'], matriz['nu_m']):.2f}
    """
    
    # Mostrar histórico de mensagens
    st.markdown("### 💬 Conversa")
    
    for msg in st.session_state.mensagens_chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # Input do usuário
    pergunta = st.chat_input("Digite sua pergunta sobre os materiais ou gráficos...")
    
    if pergunta:
        # Adicionar mensagem do usuário ao histórico
        st.session_state.mensagens_chat.append({"role": "user", "content": pergunta})
        
        with st.chat_message("user"):
            st.markdown(pergunta)
        
        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                try:
                    # Construir histórico para o Gemini
                    historico = []
                    for msg in st.session_state.mensagens_chat[-10:]:
                        historico.append(f"{msg['role']}: {msg['content']}")
                    
                    historico_texto = "\n".join(historico)
                    
                    prompt = f"""
                    Você é um especialista em materiais compósitos.
                    
                    {contexto_base}
                    
                    HISTÓRICO DA CONVERSA:
                    {historico_texto}
                    
                    Responda à última pergunta do usuário de forma natural, como um especialista conversando.
                    Use o contexto atual e o histórico para manter a continuidade da conversa.
                    Seja conciso mas informativo.
                    """
                    
                    resposta = st.session_state.chat_model.generate_content(prompt)
                    
                    # Adicionar resposta ao histórico
                    st.session_state.mensagens_chat.append({"role": "assistant", "content": resposta.text})
                    st.markdown(resposta.text)
                    
                except Exception as e:
                    st.error(f"Erro: {e}")
else:
    st.error(f"❌ Erro de conexão com Gemini. Verifique o arquivo .streamlit/secrets.toml")

st.markdown("---")
st.markdown("*Ferramenta desenvolvida para projeto de mestrado*")