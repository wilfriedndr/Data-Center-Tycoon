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


def build_24h_dataframe(metrics: dict) -> pd.DataFrame:
    hours = np.arange(24)
    load_curve = 0.75 + 0.25 * np.sin((hours - 7) / 24 * 2 * np.pi)
    energy = metrics["daily_energy_kwh"] / 24 * load_curve
    temperature = metrics["temperature"] + 5 * np.sin((hours - 12) / 24 * 2 * np.pi)

    return pd.DataFrame(
        {
            "Heure": hours,
            "Consommation kWh": energy,
            "Température °C": temperature,
        }
    )


if "active_event" not in st.session_state:
    st.session_state.active_event = None

if "event_history" not in st.session_state:
    st.session_state.event_history = []


st.title("⚡ Data Center Tycoon: GreenOps Simulator")

st.markdown(
    """
    Gérez un mini data center en équilibrant **performance**, **consommation énergétique**,
    **coût**, **température**, **émissions carbone** et **disponibilité du service**.

    L’objectif : obtenir le meilleur **Green Score** sans sacrifier la stabilité de l’infrastructure.
    """
)

with st.sidebar:
    st.header("🎛️ Paramètres du data center")

    servers = st.slider("Serveurs actifs", 1, 80, 24)
    user_load = st.slider("Charge utilisateur (%)", 0, 100, 65)
    cooling = st.slider("Refroidissement (%)", 0, 100, 55)
    optimization = st.slider("Optimisation logicielle (%)", 0, 100, 35)
    renewable_energy = st.slider("Énergie renouvelable (%)", 0, 100, 40)
    energy_price = st.slider("Prix électricité (€/kWh)", 0.10, 0.50, 0.22, 0.01)

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

col1, col2, col3 = st.columns(3)
col4, col5, col6 = st.columns(3)

col1.metric("Consommation / jour", f"{metrics['daily_energy_kwh']:.0f} kWh")
col2.metric("Coût / jour", f"{metrics['daily_cost']:.2f} €")
col3.metric("Température", f"{metrics['temperature']:.1f} °C")

col4.metric("Disponibilité", f"{metrics['availability']:.1f} %")
col5.metric("Émissions CO₂ / jour", f"{metrics['co2_kg']:.1f} kg")
col6.metric("Green Score", f"{metrics['green_score']:.0f} / 100")

st.progress(int(metrics["green_score"]) / 100)

verdict_title, verdict_text = get_verdict(
    metrics["green_score"],
    metrics["availability"],
    metrics["temperature"],
)

st.subheader(f"🏁 Verdict : {verdict_title}")
st.write(verdict_text)

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
    )
    st.plotly_chart(fig_power, use_container_width=True)

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
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.subheader("📈 Simulation sur 24h")

hourly_df = build_24h_dataframe(metrics)

fig_line = go.Figure()
fig_line.add_trace(
    go.Scatter(
        x=hourly_df["Heure"],
        y=hourly_df["Consommation kWh"],
        mode="lines+markers",
        name="Consommation kWh",
    )
)
fig_line.add_trace(
    go.Scatter(
        x=hourly_df["Heure"],
        y=hourly_df["Température °C"],
        mode="lines+markers",
        name="Température °C",
        yaxis="y2",
    )
)
fig_line.update_layout(
    xaxis_title="Heure",
    yaxis_title="Consommation kWh",
    yaxis2=dict(
        title="Température °C",
        overlaying="y",
        side="right",
    ),
    legend=dict(orientation="h"),
)
st.plotly_chart(fig_line, use_container_width=True)

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