# -*- coding: utf-8 -*-
"""
Nom du fichier : data_generation/utils/random_utils.py
Description     : Outils de génération de nombres aléatoires avec distributions adaptées.
"""

import random
from typing import List, Any
from data_generation.config.config import SEED

# Assure la reproductibilité globale des appels random
random.seed(SEED)

def get_random_choice(choices: List[Any], probabilities: List[float] = None) -> Any:
    """
    Retourne un élément au hasard parmi la liste en respectant les probabilités de distribution.
    """
    if probabilities:
        return random.choices(choices, weights=probabilities, k=1)[0]
    return random.choice(choices)

def generate_lognormal_amount(mean: float, std_dev: float, min_val: float, max_val: float) -> float:
    """
    Génère un montant financier suivant une loi log-normale, tronquée entre min_val et max_val.
    Idéal pour simuler des chiffres d'affaires ou des transactions bancaires réalistes.
    """
    while True:
        # random.lognormvariate prend les paramètres de la distribution normale sous-jacente
        # Approximation simple pour cibler une moyenne réelle
        amount = random.lognormvariate(mean, std_dev)
        if min_val <= amount <= max_val:
            return round(amount, 2)

def generate_normal_integer(mean: float, std_dev: float, min_val: int, max_val: int) -> int:
    """
    Génère un entier suivant une loi normale tronquée.
    Idéal pour les effectifs de salariés par exemple.
    """
    while True:
        val = int(random.gauss(mean, std_dev))
        if min_val <= val <= max_val:
            return val
