import streamlit as st
import numpy as np
import plotly.graph_objects as go
from fpdf import FPDF
import base64
from io import BytesIO
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

st.set_page_config(page_title="Relationship Survival Predictor", page_icon="❤️", layout="centered")

st.title("❤️ Relationship Survival Predictor")
st.markdown("Quant model based on Gottman Institute research + survival analysis", unsafe_allow_html=True)

# ────────────────────────────── Inputs (7 core variables) ──────────────────────────────
st.sidebar.header("Your Relationship Data")

compatibility = st.sidebar.slider("Compatibility score (0–10)", 0.0, 10.0, 6.5, 0.1)
pos_neg_ratio = st.sidebar.slider("Positive:Negative ratio", 0.5, 10.0, 3.5, 0.1, help="Ideal ≥5:1")
conflict_freq = st.sidebar.slider("Conflicts per month", 0, 20, 4)
four_horsemen = st.sidebar.slider("Four Horsemen severity (0–10)", 0, 10, 3, help="Criticism, Contempt, Defensiveness, Stonewalling — rate intensity")
repair_success = st.sidebar.slider("Repair attempt success (0–10)", 0, 10, 6)
shared_values = st.sidebar.slider("Shared values/goals (0–10)", 0.0, 10.0, 6.0, 0.1)
external_stress = st.sidebar.slider("External stress (0–10)", 0, 10, 4)

time_together = st.sidebar.number_input("Time together (months)", min_value=1, value=18, step=1)

premium = st.sidebar.checkbox("Unlock Premium ($4.99 one-time)", value=False)

# ────────────────────────────── Model ──────────────────────────────
lambda_base = 0.035
lambda_penalty = (
    0.012 * (5.0 - pos_neg_ratio) +
    0.008 * conflict_freq +
    0.009 * four_horsemen +
    -0.006 * compatibility +
    -0.005 * shared_values +
    0.007 * external_stress +
    -0.006 * repair_success
)
lambda_monthly = max(0.01, lambda_base + lambda_penalty)

def survival_prob(months):
    return np.exp(-lambda_monthly * months)

happiness = max(10, min(100,
    65 + 4.0*compatibility + 3.2*pos_neg_ratio -2.5*conflict_freq -3.8*four_horsemen +
    3.5*shared_values -3.0*external_stress +4.2*repair_success
))

# ────────────────────────────── Outputs ──────────────────────────────
col1, col2, col3 = st.columns(3)
col1.metric("1-Year Survival", f"{survival_prob(12)*100:.1f}%")
col2.metric("5-Year Survival", f"{survival_prob(60)*100:.1f}%")
col3.metric("Happiness Score", f"{happiness:.0f}/100")

# Survival Curve
months = np.arange(0, 241, 1)
probs = survival_prob(months)

fig = go.Figure()
fig.add_trace(go.Scatter(x=months/12, y=probs*100, mode='lines', line=dict(color='#e63946', width=3), name='Your relationship'))
if premium:
    # Simple Monte Carlo uncertainty (premium)
    n_sims = 500
    lambda_samples = np.random.normal(lambda_monthly, 0.005, n_sims)
    sim_probs = np.array([np.exp(-lam * months) for lam in lambda_samples])
    p5, p95 = np.percentile(sim_probs, [5, 95], axis=0) * 100
    fig.add_trace(go.Scatter(x=np.concatenate([months/12, months[::-1]/12]),
                             y=np.concatenate([p95, p5[::-1]]),
                             fill='toself', fillcolor='rgba(230,57,70,0.2)', line=dict(color='rgba(255,255,255,0)'), name='80% CI'))
fig.add_trace(go.Scatter(x=[1,5,10], y=[survival_prob(12)*100, survival_prob(60)*100, survival_prob(120)*100],
                         mode='markers+text', marker=dict(size=12, color='#1d3557'),
                         text=[f"{survival_prob(12)*100:.1f}%", f"{survival_prob(60)*100:.1f}%", f"{survival_prob(120)*100:.1f}%"],
                         textposition="top center"))
fig.update_layout(title="Relationship Survival Over Time", xaxis_title="Years", yaxis_title="Probability (%)", yaxis_range=[0,100], template="plotly_white", height=500)
st.plotly_chart(fig, use_container_width=True)

# Impact Bar
impact_data = {
    "Compatibility": 4.0 * compatibility,
    "Pos:Neg Ratio": 3.2 * pos_neg_ratio,
    "Conflicts": -2.5 * conflict_freq,
    "Four Horsemen": -3.8 * four_horsemen,
    "Shared Values": 3.5 * shared_values,
    "External Stress": -3.0 * external_stress,
    "Repair Success": 4.2 * repair_success
}
fig2 = go.Figure(go.Bar(x=list(impact_data.keys()), y=list(impact_data.values()),
                        marker_color=['#2a9d8f' if v>0 else '#e63946' for v in impact_data.values()],
                        text=[f"+{v:.1f}" if v>0 else f"{v:.1f}" for v in impact_data.values()],
                        textposition='auto'))
fig2.update_layout(title="Predictor Impact on Longevity", yaxis_title="Relative Impact", template="plotly_white", height=450)
st.plotly_chart(fig2, use_container_width=True)

# ────────────────────────────── Premium Features ──────────────────────────────
if premium:
    # PDF Report
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Your Personalized Relationship Report", ln=1, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.ln(10)
    pdf.cell(0, 10, f"1-Year Survival: {survival_prob(12)*100:.1f}%", ln=1)
    pdf.cell(0, 10, f"5-Year Survival: {survival_prob(60)*100:.1f}%", ln=1)
    pdf.cell(0, 10, f"Estimated Happiness: {happiness:.0f}/100", ln=1)
    pdf.ln(10)
    pdf.set_font("Arial", "I", 10)
    pdf.multi_cell(0, 8, "This is a simplified exponential survival model calibrated to Gottman research. "
                         "Higher compatibility, positive interactions, successful repairs, and shared values improve odds. "
                         "Frequent conflicts, Four Horsemen behaviors, and external stress reduce them. "
                         "Use as insight only — not a diagnosis or guarantee.")
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_bytes = pdf_output.getvalue()

    st.download_button("Download Full Report (PDF)", pdf_bytes, "relationship_report.pdf", "application/pdf")

    # Shareable PNG (simple summary)
    fig_summary, ax = plt.subplots(figsize=(6, 4))
    ax.text(0.5, 0.8, f"1-Year Survival: {survival_prob(12)*100:.1f}%", ha='center', va='center', fontsize=14)
    ax.text(0.5, 0.6, f"5-Year Survival: {survival_prob(60)*100:.1f}%", ha='center', va='center', fontsize=14)
    ax.text(0.5, 0.4, f"Happiness Score: {happiness:.0f}/100", ha='center', va='center', fontsize=14)
    ax.axis('off')
    buf = BytesIO()
    fig_summary.savefig(buf, format="png", bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode()
    st.markdown(f'<img src="data:image/png;base64,{img_base64}" width="100%" />', unsafe_allow_html=True)
    st.download_button("Download Shareable Summary (PNG)", buf.getvalue(), "relationship_summary.png", "image/png")

# ────────────────────────────── Ads Banner ──────────────────────────────
st.markdown("---")
st.markdown("""
<div style="background:#f8f9fa; padding:20px; border-radius:12px; text-align:center; border:1px solid #dee2e6;">
    <h3 style="margin:0;">This Tool is Ad-Supported</h3>
    <p style="margin:12px 0;">Enjoy free access thanks to our sponsors.</p>
    <div style="background:#e9ecef; padding:20px; border-radius:8px; min-height:100px; margin:16px auto; max-width:728px;">
        <p style="margin:40px 0; color:#6c757d; font-style:italic;">Advertisement space – your brand could be here</p>
    </div>
    <p style="margin-top:16px;">Want no ads + premium features (PDF report, uncertainty bands, shareable summary)?</p>
    <a href="https://your-gumroad-or-stripe-link-here" target="_blank" style="display:inline-block; padding:12px 32px; background:#0d6efd; color:white; border-radius:8px; text-decoration:none; font-weight:bold;">
        Upgrade to Premium – $4.99 one-time
    </a>
</div>
""", unsafe_allow_html=True)

st.caption("Simplified exponential survival model based on Gottman Institute data. Educational/entertainment use only.")
