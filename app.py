import random
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="Data Center Tycoon",
    page_icon="⚡",
    layout="wide",
)

st.markdown(
    """
    <style>
    .hero {
        border: 1px solid rgba(128, 128, 128, 0.28);
        border-radius: 8px;
        padding: 1.25rem 1.4rem;
        background: var(--secondary-background-color);
        color: var(--text-color);
        margin-bottom: 1rem;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
    }
    .hero h1 {
        margin: 0 0 0.35rem 0;
        font-size: 2.25rem;
        line-height: 1.1;
        color: var(--text-color);
    }
    .hero p {
        margin: 0.25rem 0;
        font-size: 1.02rem;
        color: var(--text-color);
    }
    .hero strong {
        color: var(--text-color);
    }
    .status-badge {
        display: inline-block;
        border-radius: 999px;
        padding: 0.18rem 0.55rem;
        font-size: 0.82rem;
        font-weight: 700;
        border: 1px solid transparent;
        margin-top: 0.25rem;
    }
    .badge-good {
        background: #e8f6ee;
        border-color: #9fd5b1;
        color: #146c3f;
    }
    .badge-medium {
        background: #fff4d7;
        border-color: #f1cb6a;
        color: #875b00;
    }
    .badge-bad {
        background: #fde8e8;
        border-color: #f2a3a3;
        color: #9f1f1f;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

EVENTS = [
    {
        "name": "Pic de trafic",
        "emoji": "📈",
        "description": "La charge utilisateur augmente fortement.",
        "load_bonus": 20,
        "temp_bonus": 3,
        "cooling_penalty": 0,
        "price_bonus": 0,
        "renewable_bonus": 0,
        "optimization_bonus": 0,
    },
    {
        "name": "Vague de chaleur",
        "emoji": "🌡️",
        "description": "La température extérieure augmente, le refroidissement devient plus difficile.",
        "load_bonus": 0,
        "temp_bonus": 10,
        "cooling_penalty": 10,
        "price_bonus": 0,
        "renewable_bonus": 0,
        "optimization_bonus": 0,
    },
    {
        "name": "Panne partielle de refroidissement",
        "emoji": "⚠️",
        "description": "Le système de refroidissement perd temporairement en efficacité.",
        "load_bonus": 0,
        "temp_bonus": 6,
        "cooling_penalty": 25,
        "price_bonus": 0,
        "renewable_bonus": 0,
        "optimization_bonus": 0,
    },
    {
        "name": "Hausse du prix de l’électricité",
        "emoji": "💸",
        "description": "Le coût de l’électricité augmente pendant la simulation.",
        "load_bonus": 0,
        "temp_bonus": 0,
        "cooling_penalty": 0,
        "price_bonus": 0.08,
        "renewable_bonus": 0,
        "optimization_bonus": 0,
    },
    {
        "name": "Production solaire élevée",
        "emoji": "☀️",
        "description": "La part d’énergie renouvelable disponible augmente temporairement.",
        "load_bonus": 0,
        "temp_bonus": 0,
        "cooling_penalty": 0,
        "price_bonus": -0.02,
        "renewable_bonus": 20,
        "optimization_bonus": 0,
    },
    {
        "name": "Optimisation logicielle déployée",
        "emoji": "🧠",
        "description": "Une optimisation réduit la charge inutile sur les serveurs.",
        "load_bonus": -10,
        "temp_bonus": -2,
        "cooling_penalty": 0,
        "price_bonus": 0,
        "renewable_bonus": 0,
        "optimization_bonus": 15,
    },
]


SCENARIOS = {
    "Personnalisé": {
        "description": "Réglages par défaut du MVP, à ajuster librement.",
        "values": {
            "servers": 24,
            "user_load": 65,
            "cooling": 55,
            "optimization": 35,
            "renewable_energy": 40,
            "energy_price": 0.22,
        },
    },
    "🌱 Data center sobre": {
        "description": "Priorité à la sobriété, aux renouvelables et à l'optimisation logicielle.",
        "values": {
            "servers": 24,
            "user_load": 55,
            "cooling": 55,
            "optimization": 85,
            "renewable_energy": 85,
            "energy_price": 0.18,
        },
    },
    "⚡ Performance maximale": {
        "description": "Capacité élevée et refroidissement renforcé pour absorber une forte demande.",
        "values": {
            "servers": 70,
            "user_load": 90,
            "cooling": 80,
            "optimization": 45,
            "renewable_energy": 35,
            "energy_price": 0.25,
        },
    },
    "🔥 Incident critique": {
        "description": "Configuration extrême pour montrer les risques GreenOps majeurs.",
        "values": {
            "servers": 80,
            "user_load": 100,
            "cooling": 0,
            "optimization": 35,
            "renewable_energy": 0,
            "energy_price": 0.50,
        },
    },
    "💸 Énergie chère": {
        "description": "Prix de l'électricité élevé, utile pour démontrer l'impact des coûts.",
        "values": {
            "servers": 45,
            "user_load": 75,
            "cooling": 60,
            "optimization": 40,
            "renewable_energy": 25,
            "energy_price": 0.50,
        },
    },
    "🧠 Optimisation logicielle": {
        "description": "Exemple montrant l'effet d'une forte optimisation sans surdimensionner le matériel.",
        "values": {
            "servers": 32,
            "user_load": 70,
            "cooling": 50,
            "optimization": 95,
            "renewable_energy": 55,
            "energy_price": 0.22,
        },
    },
}


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


def calculate_datacenter_metrics(
    servers: int,
    user_load: int,
    cooling: int,
    optimization: int,
    renewable_energy: int,
    energy_price: float,
    event: dict | None,
) -> dict:
    event = event or {}

    effective_load = clamp(user_load + event.get("load_bonus", 0), 0, 100)
    effective_cooling = clamp(cooling - event.get("cooling_penalty", 0), 0, 100)
    effective_optimization = clamp(optimization + event.get("optimization_bonus", 0), 0, 100)
    effective_renewable = clamp(renewable_energy + event.get("renewable_bonus", 0), 0, 100)
    effective_price = max(0.01, energy_price + event.get("price_bonus", 0))

    base_power_per_server_kw = 0.55
    load_factor = 0.35 + (effective_load / 100) * 0.65
    optimization_factor = 1 - (effective_optimization / 100) * 0.35

    it_power_kw = servers * base_power_per_server_kw * load_factor * optimization_factor

    cooling_intensity = 0.15 + (effective_cooling / 100) * 0.35
    cooling_power_kw = it_power_kw * cooling_intensity

    total_power_kw = it_power_kw + cooling_power_kw
    daily_energy_kwh = total_power_kw * 24
    daily_cost = daily_energy_kwh * effective_price

    temperature = (
        24
        + effective_load * 0.42
        + servers * 0.08
        - effective_cooling * 0.34
        - effective_optimization * 0.07
        + event.get("temp_bonus", 0)
    )

    server_capacity_score = clamp((servers * 2.4 / max(effective_load, 1)) * 100, 0, 100)
    heat_penalty = max(0, temperature - 75) * 2.3
    availability = clamp(server_capacity_score - heat_penalty, 0, 100)

    fossil_share = 1 - (effective_renewable / 100)
    renewable_share = effective_renewable / 100
    carbon_factor = fossil_share * 0.38 + renewable_share * 0.04
    co2_kg = daily_energy_kwh * carbon_factor

    cost_score = 100 - clamp((daily_cost / 250) * 100, 0, 100)
    carbon_score = 100 - clamp((co2_kg / 180) * 100, 0, 100)
    temperature_score = 100 - clamp(max(0, temperature - 45) * 2.2, 0, 100)

    green_score = (
        availability * 0.35
        + cost_score * 0.20
        + carbon_score * 0.25
        + temperature_score * 0.20
    )

    return {
        "effective_load": effective_load,
        "effective_cooling": effective_cooling,
        "effective_optimization": effective_optimization,
        "effective_renewable": effective_renewable,
        "effective_price": effective_price,
        "it_power_kw": it_power_kw,
        "cooling_power_kw": cooling_power_kw,
        "total_power_kw": total_power_kw,
        "daily_energy_kwh": daily_energy_kwh,
        "daily_cost": daily_cost,
        "temperature": temperature,
        "availability": availability,
        "co2_kg": co2_kg,
        "green_score": clamp(green_score, 0, 100),
    }


def get_verdict(score: float, availability: float, temperature: float) -> tuple[str, str]:
    if temperature >= 85:
        return "Critique", "Le data center surchauffe. Il faut augmenter le refroidissement ou réduire la charge."
    if availability < 70:
        return "Instable", "La disponibilité est trop faible. Il faut plus de capacité ou une meilleure optimisation."
    if score >= 80:
        return "Excellent", "Data center performant, sobre et bien équilibré."
    if score >= 60:
        return "Correct", "Le service fonctionne, mais il reste des marges d’optimisation énergétique."
    return "À optimiser", "Le coût énergétique, la température ou les émissions carbone sont trop élevés."


def get_temperature_status(temperature: float) -> tuple[str, str]:
    if temperature >= 80:
        return "Critique", "badge-bad"
    if temperature >= 65:
        return "Élevée", "badge-medium"
    return "Normale", "badge-good"


def get_availability_status(availability: float) -> tuple[str, str]:
    if availability >= 95:
        return "Excellente", "badge-good"
    if availability >= 90:
        return "Correcte", "badge-medium"
    return "Faible", "badge-bad"


def get_green_score_status(score: float) -> tuple[str, str]:
    if score >= 80:
        return "Excellent", "badge-good"
    if score >= 60:
        return "Correct", "badge-medium"
    return "Faible", "badge-bad"


def status_badge(label: str, css_class: str) -> str:
    return f'<span class="status-badge {css_class}">{label}</span>'


def generate_greenops_tips(
    metrics: dict,
    servers: int,
    user_load: int,
    cooling: int,
    optimization: int,
    renewable_energy: int,
    energy_price: float,
) -> list[dict[str, str]]:
    tips = []

    if metrics["green_score"] < 50:
        tips.append(
            {
                "level": "error",
                "message": "Green Score faible : priorisez refroidissement, baisse de charge, optimisation et énergie renouvelable.",
            }
        )

    if metrics["temperature"] > 80:
        tips.append(
            {
                "level": "error",
                "message": "Surchauffe critique : augmentez le refroidissement ou réduisez rapidement la charge.",
            }
        )

    if cooling < 20 and user_load > 70:
        message = "Refroidissement insuffisant avec forte charge : risque de surchauffe et de disponibilité dégradée."
        if cooling == 0:
            message = "Aucun refroidissement avec forte charge : risque de surchauffe et de disponibilité dégradée."
        tips.append(
            {
                "level": "error",
                "message": message,
            }
        )

    if user_load == 100:
        tips.append(
            {
                "level": "warning",
                "message": "Charge à 100 % : réduisez la demande ou augmentez l'optimisation logicielle.",
            }
        )

    if energy_price >= 0.40:
        tips.append(
            {
                "level": "warning",
                "message": "Prix de l'électricité élevé : réduisez la consommation et les serveurs actifs non essentiels.",
            }
        )

    if renewable_energy == 0:
        tips.append(
            {
                "level": "warning",
                "message": "Aucune énergie renouvelable : augmentez la part renouvelable pour réduire les émissions CO2.",
            }
        )

    if metrics["availability"] < 90:
        message = "Disponibilité sous 90 % : ajoutez des serveurs ou améliorez l'optimisation logicielle."
        if servers >= 40:
            message = "Disponibilité sous 90 % : optimisez le logiciel avant d'ajouter encore du matériel."
        tips.append(
            {
                "level": "warning",
                "message": message,
            }
        )

    if metrics["co2_kg"] > 80 and renewable_energy > 0:
        tips.append(
            {
                "level": "warning",
                "message": "Émissions CO2 élevées : augmentez la part renouvelable ou réduisez la consommation.",
            }
        )

    if metrics["daily_cost"] > 75:
        message = "Coût journalier élevé : réduisez les serveurs inutiles ou augmentez l'optimisation logicielle."
        if servers >= 60:
            message = "Coût journalier élevé : vérifiez si tous les serveurs actifs sont nécessaires."
        tips.append(
            {
                "level": "warning",
                "message": message,
            }
        )

    if cooling >= 80 and metrics["temperature"] < 35:
        tips.append(
            {
                "level": "info",
                "message": "Refroidissement très élevé pour une température basse : réduisez-le pour économiser de l'énergie.",
            }
        )

    if optimization < 30:
        tips.append(
            {
                "level": "info",
                "message": "Optimisation faible : elle peut réduire la consommation sans ajouter de matériel.",
            }
        )

    if metrics["green_score"] > 80:
        tips.append(
            {
                "level": "success",
                "message": "Excellent équilibre global : performance, sobriété et stabilité sont bien maîtrisées.",
            }
        )

    if not tips:
        tips.append(
            {
                "level": "info",
                "message": "Aucun point critique détecté : ajustez les paramètres pour améliorer le Green Score.",
            }
        )

    return tips


def simulate_24h(
    servers: int,
    user_load: int,
    cooling: int,
    optimization: int,
    renewable_energy: int,
    energy_price: float,
) -> tuple[pd.DataFrame, list[dict[str, str]]]:
    event_hours = sorted(random.sample(range(6, 23), k=3))
    scheduled_events = {hour: random.choice(EVENTS) for hour in event_hours}
    rows = []
    event_log = []

    for hour in range(24):
        if hour < 6:
            load_factor = 0.55
        elif hour < 9:
            load_factor = 0.75
        elif hour < 13:
            load_factor = 1.00
        elif hour < 19:
            load_factor = 1.12
        elif hour < 22:
            load_factor = 0.90
        else:
            load_factor = 0.65

        hourly_load = int(round(clamp(user_load * load_factor + random.uniform(-4, 4), 0, 100)))
        event = scheduled_events.get(hour)
        hourly_metrics = calculate_datacenter_metrics(
            servers=servers,
            user_load=hourly_load,
            cooling=cooling,
            optimization=optimization,
            renewable_energy=renewable_energy,
            energy_price=energy_price,
            event=event,
        )

        event_name = "Aucun"
        if event:
            event_name = event["name"]
            event_log.append(
                {
                    "Heure": f"{hour:02d}:00",
                    "Événement": f"{event['emoji']} {event['name']}",
                    "Impact": event["description"],
                }
            )

        rows.append(
            {
                "Heure": f"{hour:02d}:00",
                "Charge simulée %": hourly_load,
                "Charge effective %": hourly_metrics["effective_load"],
                "Événement": event_name,
                "Consommation kWh": hourly_metrics["daily_energy_kwh"] / 24,
                "Coût €": hourly_metrics["daily_cost"] / 24,
                "Température °C": hourly_metrics["temperature"],
                "Disponibilité %": hourly_metrics["availability"],
                "Émissions CO2 kg": hourly_metrics["co2_kg"] / 24,
                "Green Score": hourly_metrics["green_score"],
            }
        )

    return pd.DataFrame(rows), event_log


if "active_event" not in st.session_state:
    st.session_state.active_event = None

if "event_history" not in st.session_state:
    st.session_state.event_history = []

if "simulation_24h_df" not in st.session_state:
    st.session_state.simulation_24h_df = None

if "simulation_24h_events" not in st.session_state:
    st.session_state.simulation_24h_events = []

if "selected_scenario" not in st.session_state:
    st.session_state.selected_scenario = "Personnalisé"

if "applied_scenario" not in st.session_state:
    st.session_state.applied_scenario = None

for key, value in SCENARIOS["Personnalisé"]["values"].items():
    if key not in st.session_state:
        st.session_state[key] = value


st.markdown(
    """
    <div class="hero">
        <h1>⚡ Data Center Tycoon: GreenOps Simulator</h1>
        <p><strong>Pilotez un data center sous contraintes énergie, coût, carbone et disponibilité.</strong></p>
        <p>Objectif du joueur : obtenir le meilleur Green Score sans faire tomber la stabilité de l'infrastructure.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("🎯 Objectif de simulation")

objective_cols = st.columns(5)
objective_cols[0].markdown("**🛡️ Disponibilité**<br>Maintenir le service stable.", unsafe_allow_html=True)
objective_cols[1].markdown("**🌡️ Température**<br>Limiter les risques de surchauffe.", unsafe_allow_html=True)
objective_cols[2].markdown("**💶 Coût**<br>Réduire la facture quotidienne.", unsafe_allow_html=True)
objective_cols[3].markdown("**🌍 CO2**<br>Diminuer les émissions.", unsafe_allow_html=True)
objective_cols[4].markdown("**🌱 Score**<br>Maximiser le Green Score.", unsafe_allow_html=True)

st.subheader("📚 Lecture pédagogique")
st.info(
    "Le simulateur illustre les compromis GreenOps entre capacité, charge, refroidissement, coût et énergie renouvelable. "
    "Les résultats réagissent immédiatement aux choix de configuration pour faciliter une démonstration rapide. "
    "Les calculs sont simplifiés et pédagogiques : ils montrent des tendances, pas un audit énergétique réel."
)

with st.sidebar:
    st.header("🎬 Scénarios de démonstration")

    selected_scenario = st.selectbox(
        "Choisir un scénario",
        options=list(SCENARIOS.keys()),
        key="selected_scenario",
    )

    scenario = SCENARIOS[selected_scenario]

    if st.session_state.applied_scenario != selected_scenario:
        for key, value in scenario["values"].items():
            st.session_state[key] = value
        st.session_state.applied_scenario = selected_scenario

    st.caption(scenario["description"])

    st.divider()

    st.header("🎛️ Paramètres du data center")

    servers = st.slider("Serveurs actifs", 1, 80, key="servers")
    user_load = st.slider("Charge utilisateur (%)", 0, 100, key="user_load")
    cooling = st.slider("Refroidissement (%)", 0, 100, key="cooling")
    optimization = st.slider("Optimisation logicielle (%)", 0, 100, key="optimization")
    renewable_energy = st.slider("Énergie renouvelable (%)", 0, 100, key="renewable_energy")
    energy_price = st.slider("Prix électricité (€/kWh)", 0.10, 0.50, step=0.01, key="energy_price")

    st.divider()

    if st.button("🎲 Déclencher un événement"):
        event = random.choice(EVENTS)
        st.session_state.active_event = event
        st.session_state.event_history.insert(0, event)

    if st.button("🔄 Réinitialiser l’événement"):
        st.session_state.active_event = None


active_event = st.session_state.active_event

metrics = calculate_datacenter_metrics(
    servers=servers,
    user_load=user_load,
    cooling=cooling,
    optimization=optimization,
    renewable_energy=renewable_energy,
    energy_price=energy_price,
    event=active_event,
)

if active_event:
    st.warning(
        f"{active_event['emoji']} **Événement actif : {active_event['name']}** — "
        f"{active_event['description']}"
    )
else:
    st.info("Aucun événement actif. Déclenchez un événement pour tester la résilience du data center.")

st.subheader("📊 Tableau de bord")

temperature_status, temperature_class = get_temperature_status(metrics["temperature"])
availability_status, availability_class = get_availability_status(metrics["availability"])
green_score_status, green_score_class = get_green_score_status(metrics["green_score"])

col1, col2, col3 = st.columns(3)
col4, col5, col6 = st.columns(3)

col1.metric(
    "⚡ Consommation / jour",
    f"{metrics['daily_energy_kwh']:.0f} kWh",
    delta=f"{metrics['total_power_kw']:.1f} kW moyens",
    delta_color="off",
)
col2.metric(
    "💶 Coût / jour",
    f"{metrics['daily_cost']:.2f} €",
    delta=f"{metrics['effective_price']:.2f} €/kWh",
    delta_color="off",
)
col3.metric(
    "🌡️ Température",
    f"{metrics['temperature']:.1f} °C",
    delta=temperature_status,
    delta_color="off",
)
col3.markdown(status_badge(temperature_status, temperature_class), unsafe_allow_html=True)

col4.metric(
    "🛡️ Disponibilité",
    f"{metrics['availability']:.1f} %",
    delta=availability_status,
    delta_color="off",
)
col4.markdown(status_badge(availability_status, availability_class), unsafe_allow_html=True)
col5.metric(
    "🌍 Émissions CO₂ / jour",
    f"{metrics['co2_kg']:.1f} kg",
    delta=f"{metrics['effective_renewable']:.0f} % renouvelable",
    delta_color="off",
)
col6.metric(
    "🌱 Green Score",
    f"{metrics['green_score']:.0f} / 100",
    delta=green_score_status,
    delta_color="off",
)
col6.markdown(status_badge(green_score_status, green_score_class), unsafe_allow_html=True)

st.progress(int(metrics["green_score"]) / 100)

verdict_title, verdict_text = get_verdict(
    metrics["green_score"],
    metrics["availability"],
    metrics["temperature"],
)

st.subheader(f"🏁 Verdict : {verdict_title}")
st.write(verdict_text)

st.subheader("💡 Conseils GreenOps")

greenops_tips = generate_greenops_tips(
    metrics=metrics,
    servers=servers,
    user_load=user_load,
    cooling=cooling,
    optimization=optimization,
    renewable_energy=renewable_energy,
    energy_price=energy_price,
)

for tip in greenops_tips:
    if tip["level"] == "error":
        st.error(tip["message"])
    elif tip["level"] == "success":
        st.success(tip["message"])
    elif tip["level"] == "warning":
        st.warning(tip["message"])
    else:
        st.info(tip["message"])

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("⚙️ Répartition de la puissance")
    power_df = pd.DataFrame(
        {
            "Type": ["Serveurs IT", "Refroidissement"],
            "Puissance kW": [metrics["it_power_kw"], metrics["cooling_power_kw"]],
        }
    )

    fig_power = px.pie(
        power_df,
        names="Type",
        values="Puissance kW",
        hole=0.45,
        title="Répartition de la puissance consommée",
    )
    fig_power.update_traces(textposition="inside", textinfo="percent+label")
    fig_power.update_layout(legend_title_text="Poste de consommation")
    st.plotly_chart(fig_power, width="stretch")

with right:
    st.subheader("🌱 Paramètres effectifs")
    effective_df = pd.DataFrame(
        {
            "Paramètre": [
                "Charge",
                "Refroidissement",
                "Optimisation",
                "Renouvelable",
                "Disponibilité",
            ],
            "Valeur": [
                metrics["effective_load"],
                metrics["effective_cooling"],
                metrics["effective_optimization"],
                metrics["effective_renewable"],
                metrics["availability"],
            ],
        }
    )

    fig_bar = px.bar(
        effective_df,
        x="Paramètre",
        y="Valeur",
        range_y=[0, 100],
        text="Valeur",
        title="Paramètres effectifs après scénario et événement",
        labels={"Valeur": "Valeur (%)", "Paramètre": "Paramètre"},
    )
    fig_bar.update_traces(texttemplate="%{y:.0f}%", textposition="outside")
    fig_bar.update_layout(showlegend=False)
    st.plotly_chart(fig_bar, width="stretch")

st.subheader("🕒 Simulation 24h")

st.write(
    "Lancez une journée complète pour voir l'effet des variations de charge et des événements aléatoires heure par heure."
)

if st.button("▶️ Lancer une simulation 24h"):
    simulation_df, simulation_events = simulate_24h(
        servers=servers,
        user_load=user_load,
        cooling=cooling,
        optimization=optimization,
        renewable_energy=renewable_energy,
        energy_price=energy_price,
    )
    st.session_state.simulation_24h_df = simulation_df
    st.session_state.simulation_24h_events = simulation_events

if st.session_state.simulation_24h_df is None:
    st.info("Aucune simulation 24h lancée pour le moment.")
else:
    simulation_df = st.session_state.simulation_24h_df
    simulation_events = st.session_state.simulation_24h_events

    sim_col1, sim_col2, sim_col3 = st.columns(3)
    sim_col4, sim_col5, sim_col6 = st.columns(3)

    sim_col1.metric("⚡ Consommation 24h", f"{simulation_df['Consommation kWh'].sum():.0f} kWh")
    sim_col2.metric("💶 Coût 24h", f"{simulation_df['Coût €'].sum():.2f} €")
    sim_col3.metric("🌍 CO2 24h", f"{simulation_df['Émissions CO2 kg'].sum():.1f} kg")
    sim_col4.metric("🛡️ Disponibilité moyenne", f"{simulation_df['Disponibilité %'].mean():.1f} %")
    sim_col5.metric("🌱 Green Score moyen", f"{simulation_df['Green Score'].mean():.0f} / 100")
    sim_col6.metric("🌡️ Température max", f"{simulation_df['Température °C'].max():.1f} °C")

    st.markdown("**Journal des événements de la journée**")
    if simulation_events:
        st.dataframe(pd.DataFrame(simulation_events), hide_index=True)
    else:
        st.write("Aucun événement automatique pendant cette simulation.")

    fig_line = go.Figure()
    fig_line.add_trace(
        go.Scatter(
            x=simulation_df["Heure"],
            y=simulation_df["Consommation kWh"],
            mode="lines+markers",
            name="Consommation kWh",
        )
    )
    fig_line.add_trace(
        go.Scatter(
            x=simulation_df["Heure"],
            y=simulation_df["Température °C"],
            mode="lines+markers",
            name="Température °C",
            yaxis="y2",
        )
    )
    fig_line.add_trace(
        go.Scatter(
            x=simulation_df["Heure"],
            y=simulation_df["Green Score"],
            mode="lines+markers",
            name="Green Score",
            yaxis="y2",
        )
    )
    fig_line.update_layout(
        title="Simulation horaire : consommation, température et Green Score",
        xaxis_title="Heure",
        yaxis_title="Consommation kWh",
        yaxis2=dict(
            title="Température °C / Green Score",
            overlaying="y",
            side="right",
            range=[0, 100],
        ),
        legend=dict(orientation="h"),
    )
    st.plotly_chart(fig_line, width="stretch")

    with st.expander("Voir le détail heure par heure"):
        display_df = simulation_df.copy()
        display_df["Consommation kWh"] = display_df["Consommation kWh"].round(1)
        display_df["Coût €"] = display_df["Coût €"].round(2)
        display_df["Température °C"] = display_df["Température °C"].round(1)
        display_df["Disponibilité %"] = display_df["Disponibilité %"].round(1)
        display_df["Émissions CO2 kg"] = display_df["Émissions CO2 kg"].round(1)
        display_df["Green Score"] = display_df["Green Score"].round(0)
        st.dataframe(display_df, hide_index=True)

st.divider()

st.subheader("🧾 Journal des événements")

if st.session_state.event_history:
    for event in st.session_state.event_history[:5]:
        st.write(f"{event['emoji']} **{event['name']}** — {event['description']}")
else:
    st.write("Aucun événement déclenché pour le moment.")

st.divider()

st.caption(
    "Prototype pédagogique réalisé pour un hackathon sur le thème de l’énergie. "
    "Les calculs sont volontairement simplifiés pour illustrer les compromis entre performance, coût, température et sobriété énergétique."
)
