"""
Funções para plotagem comparativa dos modelos micromecânicos
Gera gráficos de E1, E2, G12 e nu12 em função de Vf
"""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from models import rom, reuss, halpin_tsai

def plot_all_properties(Vf_range, fibra, matriz, xi=2.0):
    """
    Gera gráficos comparativos para todas as propriedades
    
    Parâmetros:
    Vf_range : array de valores de Vf (ex: np.linspace(0, 1, 100))
    fibra : dicionário com propriedades da fibra
    matriz : dicionário com propriedades da matriz
    xi : fator de forma para Halpin-Tsai (padrão 2.0)
    
    Retorna:
    fig : objeto Figure do Plotly
    """
    
    # Calcular Gm a partir de Em e nu_m
    Gm = matriz['E_m (GPa)'] / (2 * (1 + matriz['nu_m']))
    
    # Inicializar listas para armazenar resultados
    E1_vals = []
    E2_reuss_vals = []
    E2_ht_vals = []
    G12_reuss_vals = []
    G12_ht_vals = []
    nu12_vals = []
    
    # Calcular para cada Vf
    for vf in Vf_range:
        # ROM
        E1_vals.append(rom.E1(vf, fibra['E1_f (GPa)'], matriz['E_m (GPa)']))
        nu12_vals.append(rom.nu12(vf, fibra['nu12_f'], matriz['nu_m']))
        
        # Reuss
        E2_reuss_vals.append(reuss.E2(vf, fibra['E2_f (GPa)'], matriz['E_m (GPa)']))
        G12_reuss_vals.append(reuss.G12(vf, fibra['G12_f (GPa)'], Gm))
        
        # Halpin-Tsai
        E2_ht_vals.append(halpin_tsai.E2(vf, fibra['E2_f (GPa)'], matriz['E_m (GPa)'], xi))
        G12_ht_vals.append(halpin_tsai.G12(vf, fibra['G12_f (GPa)'], Gm, xi))
    
    # Criar subplots (2 linhas, 2 colunas)
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Módulo Longitudinal E₁ (GPa)', 
                       'Módulo Transversal E₂ (GPa)',
                       'Módulo de Cisalhamento G₁₂ (GPa)', 
                       'Coeficiente de Poisson ν₁₂'),
        vertical_spacing=0.12,
        horizontal_spacing=0.15
    )
    
    # Gráfico E1 (linha 1, coluna 1)
    fig.add_trace(
        go.Scatter(x=Vf_range, y=E1_vals, 
                  mode='lines', name='ROM (E₁)',
                  line=dict(color='blue', width=3)),
        row=1, col=1
    )
    
    # Gráfico E2 (linha 1, coluna 2)
    fig.add_trace(
        go.Scatter(x=Vf_range, y=E2_reuss_vals, 
                  mode='lines', name='Reuss (E₂)',
                  line=dict(color='red', width=2, dash='dash')),
        row=1, col=2
    )
    fig.add_trace(
        go.Scatter(x=Vf_range, y=E2_ht_vals, 
                  mode='lines', name='Halpin-Tsai (E₂)',
                  line=dict(color='green', width=3)),
        row=1, col=2
    )
    
    # Gráfico G12 (linha 2, coluna 1)
    fig.add_trace(
        go.Scatter(x=Vf_range, y=G12_reuss_vals, 
                  mode='lines', name='Reuss (G₁₂)',
                  line=dict(color='red', width=2, dash='dash')),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=Vf_range, y=G12_ht_vals, 
                  mode='lines', name='Halpin-Tsai (G₁₂)',
                  line=dict(color='green', width=3)),
        row=2, col=1
    )
    
    # Gráfico nu12 (linha 2, coluna 2)
    fig.add_trace(
        go.Scatter(x=Vf_range, y=nu12_vals, 
                  mode='lines', name='ROM (ν₁₂)',
                  line=dict(color='blue', width=3)),
        row=2, col=2
    )
    
    # Adicionar faixas sombreadas para regiões não-físicas
    # Região de Vf < 0.45 (muito baixo para compósitos reais)
    fig.add_vrect(
        x0=0, x1=0.45,
        fillcolor="gray", opacity=0.2,
        layer="below", line_width=0,
        annotation_text="Vf baixo<br>(não prático)",
        annotation_position="top left",
        row='all', col='all'
    )
    
    # Região de Vf > 0.65 (muito alto - empacotamento máximo)
    fig.add_vrect(
        x0=0.65, x1=1,
        fillcolor="gray", opacity=0.2,
        layer="below", line_width=0,
        annotation_text="Vf alto<br>(empacotamento máximo)",
        annotation_position="top right",
        row='all', col='all'
    )
    
    # Configurar layout
    fig.update_layout(
        height=800,
        showlegend=True,
        title_text="Comparação de Modelos Micromecânicos",
        title_x=0.5,
        font=dict(size=12)
    )
    
    # Configurar eixos
    fig.update_xaxes(title_text="Fração Volumétrica de Fibra (Vf)", range=[0, 1], row=1, col=1)
    fig.update_xaxes(title_text="Vf", range=[0, 1], row=1, col=2)
    fig.update_xaxes(title_text="Vf", range=[0, 1], row=2, col=1)
    fig.update_xaxes(title_text="Vf", range=[0, 1], row=2, col=2)
    
    fig.update_yaxes(title_text="E₁ (GPa)", row=1, col=1)
    fig.update_yaxes(title_text="E₂ (GPa)", row=1, col=2)
    fig.update_yaxes(title_text="G₁₂ (GPa)", row=2, col=1)
    fig.update_yaxes(title_text="ν₁₂", row=2, col=2)
    
    return fig


def test_plot():
    """Função para testar a plotagem com dados de exemplo"""
    import pandas as pd
    
    # Carregar dados de exemplo
    fibras = pd.read_csv('data/fibras.csv')
    matrizes = pd.read_csv('data/matrizes.csv')
    
    # Selecionar primeira fibra e primeira matriz
    fibra = fibras.iloc[0].to_dict()
    matriz = matrizes.iloc[0].to_dict()
    
    # Criar range de Vf
    Vf_range = np.linspace(0, 1, 100)
    
    # Gerar figura
    fig = plot_all_properties(Vf_range, fibra, matriz, xi=2.0)
    
    # Mostrar figura
    fig.show()
    print("✅ Teste de plotagem concluído. Feche a janela do gráfico para continuar.")


if __name__ == "__main__":
    test_plot()
