# Super Platformer 2D (inspiré des mécaniques classiques)

Ce projet contient un jeu de plateforme 2D jouable en Python avec **Pygame**.

> ⚠️ Je n'ai pas repris du code propriétaire de Mario. Le jeu est une création originale inspirée des mécaniques de plateformes classiques.

## Fonctionnalités

- Déplacement gauche/droite + saut
- Gravité et collisions (sol, murs, plafond)
- Pièces à collecter (score)
- Ennemis avec patrouille
- Drapeau de fin de niveau
- Système de vies + game over
- Écran de victoire / défaite avec redémarrage

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Lancer le jeu

```bash
python3 game.py
```

## Contrôles

- `←` / `→` ou `Q` / `D` : se déplacer
- `Espace` / `↑` / `Z` : sauter
- `R` : rejouer après victoire ou game over

Amuse-toi bien 👾
