"""
Modelo da Regra das Misturas (ROM - Rule of Mixtures)
Hipótese: isodeformação na direção longitudinal
"""

import numpy as np

def E1(Vf, E1_f, E_m):
    """
    Módulo de elasticidade longitudinal E1
    
    Parâmetros:
    Vf : fração volumétrica de fibra (0 a 1)
    E1_f : módulo longitudinal da fibra (GPa)
    E_m : módulo da matriz (GPa)
    
    Retorna:
    E1 : módulo longitudinal do compósito (GPa)
    """
    return Vf * E1_f + (1 - Vf) * E_m


def nu12(Vf, nu12_f, nu_m):
    """
    Coeficiente de Poisson principal nu12
    
    Parâmetros:
    Vf : fração volumétrica de fibra (0 a 1)
    nu12_f : coeficiente de Poisson principal da fibra
    nu_m : coeficiente de Poisson da matriz
    
    Retorna:
    nu12 : coeficiente de Poisson principal do compósito
    """
    return Vf * nu12_f + (1 - Vf) * nu_m


# Nota: ROM não é adequado para E2 e G12
# Estes serão implementados nos outros modelos
