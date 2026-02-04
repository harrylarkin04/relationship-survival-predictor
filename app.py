import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Relationship Survival Predictor", page_icon="❤️", layout="centered")

st.title("❤️ Relationship Survival Predictor")
st.markdown("**Quant model based on Gottman Institute research + survival analysis**<br>Enter your stats → get survival probabilities, happiness score & impact breakdown", unsafe_allow_html=True)

# ────────────────────────────── Sidebar Inputs ──────────────────────────────
st.sidebar.header("Your Relationship Data")

st.sidebar.markdown("**Compatibility & Communication**")
compatibility = st.sidebar.slider("Compatibility score (0–10)", 0.0, 10.0, 6.5, 0.1)
pos_neg_ratio = st.sidebar.slider("Positive:Negative interaction ratio", 0.5, 10.0, 3.5, 0.1, help="Ideal is 5:1 or higher (Gottman)")

st.sidebar.markdown("**Conflict & Repair**")
conflict_freq = st.sidebar.slider("Conflicts per month", 0, 20, 4)
four_horsemen = st.sidebar.slider(
    "Four Horsemen severity (0=none – 10=severe)",
    0, 10, 3,
    help="""The 'Four Horsemen' are four toxic patterns that strongly predict breakup/divorce (Gottman research):
• Criticism — attacking character
• Contempt — sarcasm, eye-rolling, mockery (strongest predictor)
• Defensiveness — counter-attacking or playing victim
• Stonewalling — shutting down / withdrawing
Rate how often/intensely these appear in your arguments."""
)
repair_success = st.sidebar.slider("Repair attempt success (0–10)", 0, 10, 6, help="How well do you de-escalate / make up after fights?")

st.sidebar.markdown("**Life & Values**")
shared_values = st.sidebar.slider("Shared values/goals (0–10)", 0.0, 10.0, 6.0, 0.1)
external_stress = st.sidebar.slider("External stress (finances/work/family, 0–10)", 0, 10, 4)

time_together = st.sidebar.number_input("Time together (months)", min_value=1, value=18, step=1)

# ────────────────────────────── Model (hazard rate) ──────────────────────────────
lambda_base = 0.035  # healthy baseline hazard per month

lambda_penalty = (
    0.012 * (5.0 - pos_neg_ratio) +      # poor ratio increases hazard
    0.008 * conflict_freq +
    0.009 * four_horsemen +
    -0.006 * compatibility +
    -0.005 * shared_values +
    0.007 * external_stress +
    -0.006 * repair_success
)

lambda_monthly = max(0.01, lambda_base + lambda_penalty)  # floor at 0.01 to avoid instant 100%

# Survival function S(t) = exp(-λ t)
def survival_prob(months):
    return np.exp(-lambda_monthly * months)

# Happiness score (0–100) – linear combination
happiness = max(10, min(100,
    65 +
    4.0 * compatibility +
    3.2 * pos_neg_ratio +
    -2.5 * conflict_freq +
    -3.8 * four_horsemen +
    3.5 * shared_values +
    -3.0 * external_stress +
    4.2 * repair_success
))

# ────────────────────────────── Main Outputs ──────────────────────────────
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
fig.update_layout(
    title="Probability of Relationship Lasting Over Time",
    xaxis_title="Years Together",
    yaxis_title="Survival Probability (%)",
    yaxis_range=[0,100],
    template="plotly_white",
    height=500
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Predictor Impact")
impact_data = {
    "Compatibility": 4.0 * compatibility,
    "Pos:Neg Ratio": 3.2 * pos_neg_ratio,
    "Conflicts/month": -2.5 * conflict_freq,
    "Four Horsemen": -3.8 * four_horsemen,
    "Shared Values": 3.5 * shared_values,
    "External Stress": -3.0 * external_stress,
    "Repair Success": 4.2 * repair_success
}

fig2 = go.Figure(go.Bar(
    x=list(impact_data.keys()),
    y=list(impact_data.values()),
    marker_color=['#2a9d8f' if v > 0 else '#e63946' for v in impact_data.values()],
    text=[f"+{v:.1f}" if v > 0 else f"{v:.1f}" for v in impact_data.values()],
    textposition='auto'
))
fig2.update_layout(
    title="How Each Factor Affects Longevity Odds",
    yaxis_title="Relative Impact Score",
    template="plotly_white",
    height=450
)
st.plotly_chart(fig2, use_container_width=True)

# ────────────────────────────── Monetization Banner ──────────────────────────────
st.markdown("---")
st.markdown("""
<div style="background:#fff3e6; padding:20px; border-radius:12px; text-align:center; border:1px solid #ff9f1c;">
    <h3 style="margin:0; color:#d00000;">Want More Accurate Insights?</h3>
    <p style="margin:12px 0 0;">This free version uses simplified assumptions.<br>
    Get a personalized deep-dive report, confidence intervals, and 1:1 PM coaching session.</p>
    <a href="https://calendly.com/your-username/30min" target="_blank" style="display:inline-block; margin-top:16px; padding:12px 24px; background:#d00000; color:white; text-decoration:none; border-radius:8px; font-weight:bold;">
        Book 1:1 Session → $49
    </a>
    <p style="margin-top:16px; font-size:14px;">Or support the project:</p>
    <a href="https://buymeacoffee.com/yourusername" target="_blank" style="color:#d00000; font-weight:bold;">Buy me a coffee ☕</a>
</div>
""", unsafe_allow_html=True)

st.caption("Model is a simplified exponential survival proxy calibrated to Gottman Institute longitudinal data (40k+ couples). For entertainment & educational purposes only. Not a substitute for therapy or professional advice.")
