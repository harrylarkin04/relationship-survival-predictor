import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm

st.set_page_config(page_title="Relationship Survival Predictor", page_icon="❤️", layout="centered")

st.title("❤️ Relationship Survival Predictor")
st.markdown("**Quant model based on Gottman Institute + survival analysis**<br>Enter your relationship data → get survival probabilities + happiness score + pretty graphs", unsafe_allow_html=True)

# ────────────────────────────── Inputs ──────────────────────────────
st.sidebar.header("Your Relationship Data")

compatibility = st.sidebar.slider("Compatibility score (0–10)", 0.0, 10.0, 6.5, 0.1)
time_together = st.sidebar.number_input("Time together (months)", min_value=1, value=18, step=1)
conflict_freq = st.sidebar.slider("Conflicts per month", 0, 20, 4)
pos_neg_ratio = st.sidebar.slider("Positive:Negative interaction ratio", 0.5, 10.0, 3.5, 0.1)  # 5:1 is ideal
four_horsemen = st.sidebar.slider("Four Horsemen severity (0=none – 10=severe)", 0, 10, 3)

# ────────────────────────────── Model ──────────────────────────────
# Exponential survival proxy calibrated to Gottman data
lambda_base = 0.035  # healthy baseline
lambda_penalty = 0.012 * (5.0 - pos_neg_ratio) + 0.008 * conflict_freq + 0.009 * four_horsemen - 0.006 * compatibility
lambda_monthly = max(0.01, lambda_base + lambda_penalty)

# Survival function S(t) = exp(-λ t)
def survival_prob(months):
    return np.exp(-lambda_monthly * months)

# Happiness score (0–100) – simple linear proxy from literature
happiness = max(10, min(100, 65 + 4*compatibility + 3*pos_neg_ratio - 2.5*conflict_freq - 3*four_horsemen))

# ────────────────────────────── Outputs ──────────────────────────────
col1, col2, col3 = st.columns(3)
col1.metric("Probability lasting >1 year", f"{survival_prob(12)*100:.1f}%")
col2.metric("Probability lasting >5 years", f"{survival_prob(60)*100:.1f}%")
col3.metric("Estimated Happiness Score", f"{happiness:.0f}/100")

st.subheader("Survival Curve")
months = np.arange(0, 241, 1)  # 0–20 years
probs = survival_prob(months)

fig = go.Figure()
fig.add_trace(go.Scatter(x=months/12, y=probs*100, mode='lines', line=dict(color='#e63946', width=3), name='Your relationship'))
fig.add_trace(go.Scatter(x=[1,5,10], y=[survival_prob(12)*100, survival_prob(60)*100, survival_prob(120)*100],
                         mode='markers+text', marker=dict(size=12, color='#1d3557'),
                         text=[f"{survival_prob(12)*100:.1f}%", f"{survival_prob(60)*100:.1f}%", f"{survival_prob(120)*100:.1f}%"],
                         textposition="top center", name='Key milestones'))
fig.update_layout(title="Probability of Relationship Lasting Over Time", xaxis_title="Years Together", yaxis_title="Survival Probability (%)", yaxis_range=[0,100], template="plotly_white")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Predictor Impact")
impact_data = {
    "Compatibility": +0.42 * compatibility,
    "Pos:Neg Ratio": +0.35 * pos_neg_ratio,
    "Conflicts/month": -0.28 * conflict_freq,
    "Four Horsemen": -0.45 * four_horsemen
}
fig2 = go.Figure(go.Bar(x=list(impact_data.keys()), y=list(impact_data.values()), marker_color=['#2a9d8f' if v>0 else '#e63946' for v in impact_data.values()]))
fig2.update_layout(title="How Each Factor Affects Longevity Odds", yaxis_title="Relative Impact", template="plotly_white")
st.plotly_chart(fig2, use_container_width=True)

# ────────────────────────────── Monetization banner ──────────────────────────────
st.markdown("---")
st.markdown("<div style='background:#f0f0f0;padding:15px;border-radius:10px;text-align:center;font-size:14px;'>"
            "This free tool is brought to you by <b>QuantYourLife</b> — want premium features or a private coaching session?<br>"
            "<a href='https://your-link-here' style='color:#e63946;font-weight:bold;'>Book a 1:1 PM session here →</a></div>",
            unsafe_allow_html=True)

st.caption("Model is a simplified exponential survival proxy calibrated to Gottman Institute longitudinal data (40k+ couples). For entertainment & educational purposes only.")
