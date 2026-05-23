"""
Modelo de Halpin-Tsai
Equações semi-empíricas para E2 e G12
Parâmetro de forma ξ: padrão ξ=2 para fibras circulares
"""

import numpy as np

def E2(Vf, E2_f, E_m, xi=2.0):
    """
    Módulo de elasticidade transversal E2 (Halpin-Tsai)
    
    Parâmetros:
    Vf : fração volumétrica de fibra (0 a 1)
    E2_f : módulo transversal da fibra (GPa)
    E_m : módulo da matriz (GPa)
    xi : fator de forma (padrão 2.0 para fibras circulares)
    
    Retorna:
    E2 : módulo transversal do compósito (GPa)
    """
    eta = (E2_f/E_m - 1) / (E2_f/E_m + xi)
    return E_m * (1 + xi * eta * Vf) / (1 - eta * Vf)


def G12(Vf, G12_f, G_m, xi=2.0):
    """
    Módulo de cisalhamento no plano G12 (Halpin-Tsai)
    
    Parâmetros:
    Vf : fração volumétrica de fibra (0 a 1)
    G12_f : módulo de cisalhamento da fibra (GPa)
    G_m : módulo de cisalhamento da matriz (GPa)
    xi : fator de forma (padrão 2.0 para fibras circulares)
    
    Retorna:
    G12 : módulo de cisalhamento do compósito (GPa)
    """
    eta = (G12_f/G_m - 1) / (G12_f/G_m + xi)
    return G_m * (1 + xi * eta * Vf) / (1 - eta * Vf)


# Observação: Para Vf=0, retorna G_m; para Vf=1, retorna G12_f
# O parâmetro xi pode ser ajustado para diferentes geometrias de fibra