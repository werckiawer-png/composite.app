"""
Modelo de Reuss (Regra das Misturas Inversa)
Hipótese: isotensão na direção transversal
Adequado para E2 e G12
"""

import numpy as np

def E2(Vf, E2_f, E_m):
    """
    Módulo de elasticidade transversal E2
    
    Parâmetros:
    Vf : fração volumétrica de fibra (0 a 1)
    E2_f : módulo transversal da fibra (GPa)
    E_m : módulo da matriz (GPa)
    
    Retorna:
    E2 : módulo transversal do compósito (GPa)
    """
    return 1 / (Vf/E2_f + (1 - Vf)/E_m)


def G12(Vf, G12_f, G_m):
    """
    Módulo de cisalhamento no plano G12
    
    Parâmetros:
    Vf : fração volumétrica de fibra (0 a 1)
    G12_f : módulo de cisalhamento da fibra (GPa)
    G_m : módulo de cisalhamento da matriz (GPa)
    
    Retorna:
    G12 : módulo de cisalhamento do compósito (GPa)
    """
    return 1 / (Vf/G12_f + (1 - Vf)/G_m)


# Nota: A matriz é isotrópica, então G_m = E_m / (2*(1+nu_m))