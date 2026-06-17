# Data Center Tycoon: GreenOps Simulator

Application Streamlit réalisée dans le cadre d'un hackathon sur le thème de l'énergie.

## Démo

L'application est disponible en ligne :

https://dce4svhc2nofeqpnpqgawc5j.streamlit.app/

## Concept

**Data Center Tycoon: GreenOps Simulator** est un simulateur pédagogique qui permet d'explorer les compromis entre performance numérique, coût énergétique, impact carbone et disponibilité d'un data center.

L'utilisateur ajuste différents paramètres d'exploitation, comme le nombre de serveurs, la charge utilisateur, le niveau de refroidissement, l'optimisation logicielle, la part d'énergie renouvelable et le prix de l'électricité. La simulation calcule ensuite les conséquences de ces choix sur la consommation, la température, les émissions de CO2 et la qualité de service.

L'objectif est de rendre visibles, en quelques minutes, les décisions GreenOps auxquelles une équipe technique peut être confrontée : réduire la consommation, maîtriser les coûts, conserver une bonne disponibilité et limiter l'empreinte carbone.

## Fonctionnalités MVP

- Sliders interactifs pour ajuster les paramètres du data center.
- Calcul de la consommation énergétique en kWh/jour.
- Estimation du coût d'exploitation en €/jour.
- Suivi de la température.
- Estimation de la disponibilité du service.
- Calcul des émissions CO2.
- Green Score synthétique pour évaluer la performance globale.
- Événements aléatoires influençant la simulation.
- Graphiques interactifs avec Plotly.
- Simulation sur 24h.
- Verdict final pour interpréter les résultats.

## Stack technique

- Python
- Streamlit
- Plotly
- Pandas
- NumPy

## Installation locale

1. Cloner le repository :

```bash
git clone https://github.com/wilfriedndr/Data-Center-Tycoon.git
cd Data-Center-Tycoon
```

2. Créer un environnement virtuel :

```bash
python -m venv .venv
```

3. Activer l'environnement virtuel :

```bash
# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

4. Installer les dépendances :

```bash
pip install -r requirements.txt
```

5. Lancer l'application :

```bash
streamlit run app.py
```

## Déploiement

- Plateforme : Streamlit Community Cloud
- Repository : `wilfriedndr/Data-Center-Tycoon`
- Branch : `main`
- Main file path : `app.py`

## Utilisation de Codex

Codex a été utilisé comme assistant de développement afin d'accélérer plusieurs étapes du projet :

- Génération de la base Streamlit.
- Mise en place de la logique de calcul.
- Construction de l'interface utilisateur.
- Création des événements aléatoires.
- Production des graphiques.
- Rédaction et amélioration de la documentation.

L'utilisation de Codex a permis de gagner du temps pendant le hackathon tout en gardant une logique de projet lisible, modifiable et adaptée à une démonstration rapide.

## Limites

Les calculs utilisés dans cette application sont volontairement simplifiés et pédagogiques. Ils servent à illustrer les ordres de grandeur et les compromis entre énergie, coût, température, disponibilité et émissions carbone.

Cette simulation ne remplace pas un audit énergétique réel, une étude d'infrastructure complète ou une analyse technique réalisée à partir de données mesurées sur un data center existant.

## Pistes d'amélioration

- Ajouter plusieurs scénarios prédéfinis.
- Enregistrer et afficher le meilleur score.
- Ajouter un export des résultats.
- Intégrer un chronomètre pour renforcer l'aspect jeu/simulation.
- Améliorer le design visuel de l'interface.
- Refactoriser le projet en modules `src/`.
- Ajouter une capture d'écran ou un GIF de démonstration dans ce README.
