# Data Center Tycoon: GreenOps Simulator

Projet réalisé dans le cadre d’un hackathon sur le thème de l’énergie.

## Concept

Data Center Tycoon est un simulateur interactif qui montre comment les choix d’infrastructure d’un data center influencent la consommation énergétique, le coût, la température, les émissions carbone et la disponibilité du service.

L’utilisateur peut ajuster plusieurs paramètres : nombre de serveurs, charge utilisateur, refroidissement, optimisation logicielle, part d’énergie renouvelable et prix de l’électricité.

## Fonctionnalités

- Simulation énergétique d’un data center
- Sliders interactifs
- Calcul de la consommation électrique
- Estimation du coût journalier
- Estimation des émissions CO₂
- Green Score
- Événements aléatoires
- Graphiques interactifs avec Plotly

## Stack technique

- Python
- Streamlit
- Plotly
- Pandas
- NumPy

## Lancer le projet

```bash
pip install -r requirements.txt
streamlit run app.py