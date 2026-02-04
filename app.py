import streamlit as st
import numpy as np
import plotly.graph_objects as go
from fpdf import FPDF
import base64
from io import BytesIO
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

st.set_page_config(page_title="Relationship Survival Predictor", page_icon="❤️", layout="centered")

st.title("Relationship Survival Predictor")
st.markdown("Quant model based on Gottman Institute research + survival analysis<br>Free: 7 variables. Premium: extra insights + nice PDF + shareable card", unsafe_allow_html=True)

# Sidebar Inputs
st.sidebar.header("Your Relationship Data")

st.sidebar.markdown("**Compatibility & Communication**")
compatibility = st.sidebar.slider("Compatibility score (0-10)", 0.0, 10.0, 6.5, 0.1)
pos_neg_ratio = st.sidebar.slider("Positive:Negative ratio", 0.5, 10.0, 3.5, 0.1, help="Ideal >=5:1")

st.sidebar.markdown("**Conflict & Repair**")
conflict_freq = st.sidebar.slider("Conflicts per month", 0, 20, 4)
four_horsemen = st.sidebar.slider(
    "Four Horsemen severity (0=none - 10=severe)",
    0, 10, 3,
    help="Criticism, Contempt, Defensiveness, Stonewalling - rate how often/intensely these appear in arguments."
)
repair_success = st.sidebar.slider("Repair attempt success (0-10)", 0, 10, 6, help="How well do you de-escalate / make up after fights?")

st.sidebar.markdown("**Life & Values**")
shared_values = st.sidebar.slider("Shared values/goals (0-10)", 0.0, 10.0, 6.0, 0.1)
external_stress = st.sidebar.slider("External stress (finances/work/family, 0-10)", 0, 10, 4)

time_together = st.sidebar.number_input("Time together (months)", min_value=1, value=18, step=1)

# Premium code input
st.sidebar.markdown("**Premium Access**")
premium_code = st.sidebar.text_input("Enter Premium Code", "")
premium = premium_code.strip() == "PREMIUM2026"  # Change this to match your Gumroad thank-you code

if premium:
    st.sidebar.success("Premium unlocked! Extra features + downloads available.")
else:
    if premium_code.strip():
        st.sidebar.error("Invalid code. Get yours for $4.99 on Gumroad.")
    else:
        st.sidebar.info("Enter code to unlock premium")

# Premium variables
if premium:
    st.sidebar.markdown("**Premium Variables**")
    intimacy_freq = st.sidebar.slider("Physical intimacy frequency (times/month)", 0, 30, 8, 1)
    age_at_start = st.sidebar.slider("Age when relationship started (years)", 18, 50, 25, 1)
    financial_compat = st.sidebar.slider("Financial compatibility (0-10)", 0.0, 10.0, 6.0, 0.1)
else:
    intimacy_freq = 8
    age_at_start = 25
    financial_compat = 6.0

# Model
lambda_base = 0.035
lambda_penalty = (
    0.012 * (5.0 - pos_neg_ratio) +
    0.008 * conflict_freq +
    0.009 * four_horsemen +
    -0.006 * compatibility +
    -0.005 * shared_values +
    0.007 * external_stress +
    -0.006 * repair_success +
    -0.004 * (intimacy_freq / 10) +
    0.002 * max(0, abs(age_at_start - 28)) +
    -0.005 * financial_compat
)

lambda_monthly = max(0.01, lambda_base + lambda_penalty)

def survival_prob(months):
    return np.exp(-lambda_monthly * months)

happiness = max(10, min(100,
    65 +
    4.0 * compatibility +
    3.2 * pos_neg_ratio +
    -2.5 * conflict_freq +
    -3.8 * four_horsemen +
    3.5 * shared_values +
    -3.0 * external_stress +
    4.2 * repair_success +
    2.8 * (intimacy_freq / 5) +
    -1.5 * max(0, abs(age_at_start - 28)) +
    3.0 * financial_compat
))

# Outputs
col1, col2, col3 = st.columns(3)
col1.metric("1-Year Survival", f"{survival_prob(12)*100:.1f}%")
col2.metric("5-Year Survival", f"{survival_prob(60)*100:.1f}%")
col3.metric("Happiness Score", f"{happiness:.0f}/100")

# Survival Curve
months = np.arange(0, 241, 1)
probs = survival_prob(months)

fig = go.Figure()
fig.add_trace(go.Scatter(x=months/12, y=probs*100, mode='lines', line=dict(color='#e63946', width=3), name='Your relationship'))
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
    "Repair Success": 4.2 * repair_success,
}
if premium:
    impact_data["Intimacy Freq"] = 2.8 * (intimacy_freq / 5)
    impact_data["Age Risk"] = -1.5 * max(0, abs(age_at_start - 28))
    impact_data["Financial Compat"] = 3.0 * financial_compat

fig2 = go.Figure(go.Bar(
    x=list(impact_data.keys()),
    y=list(impact_data.values()),
    marker_color=['#2a9d8f' if v > 0 else '#e63946' for v in impact_data.values()],
    text=[f"+{v:.1f}" if v > 0 else f"{v:.1f}" for v in impact_data.values()],
    textposition='auto'
))
fig2.update_layout(title="Predictor Impact on Longevity", yaxis_title="Relative Impact", template="plotly_white", height=450)
st.plotly_chart(fig2, use_container_width=True)

# Premium Features
if premium:
    # PDF Report - nicer formatting
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 18)
    pdf.set_text_color(220, 53, 69)  # red-ish
    pdf.cell(0, 15, "Your Personalized Relationship Report", ln=1, align="C")
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f"Current Duration: {time_together} months", ln=1)
    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Key Predictions:", ln=1)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"1-Year Survival Probability: {survival_prob(12)*100:.1f}%", ln=1)
    pdf.cell(0, 10, f"5-Year Survival Probability: {survival_prob(60)*100:.1f}%", ln=1)
    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Happiness Estimate:", ln=1)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"{happiness:.0f}/100 - {'Strong' if happiness >= 70 else 'Moderate' if happiness >= 50 else 'Needs attention'}", ln=1)
    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "What This Means:", ln=1)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 6, "This model uses a simplified exponential survival approach calibrated to Gottman Institute data. "
                         "Strong points include good compatibility, positive interactions, and repair ability. "
                         "Areas to watch: conflicts, toxic patterns, and external stress. "
                         "Premium inputs like intimacy and financial harmony further refine the outlook.")
    pdf.ln(10)
    pdf.set_font("Arial", "I", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 6, "This is for entertainment and insight only. Relationships are complex - consider professional advice if needed.")

    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_bytes = pdf_output.getvalue()

    st.download_button("Download Beautiful PDF Report", pdf_bytes, "relationship_report.pdf", "application/pdf")

    # Shareable Summary Image - nicer card design
    fig_summary, ax = plt.subplots(figsize=(8, 5))
    ax.set_facecolor('#fff5f5')  # light pink background
    fig_summary.patch.set_facecolor('#fff5f5')

    # Title
    ax.text(0.5, 0.92, "My Relationship Snapshot", ha='center', va='center', fontsize=18, fontweight='bold', color='#c1121f')

    # Main stats with boxes
    ax.add_patch(FancyBboxPatch((0.15, 0.65), 0.7, 0.2, boxstyle="round,pad=0.05", ec="none", fc="#ffebee", alpha=0.8))
    ax.text(0.5, 0.75, f"1-Year Survival: {survival_prob(12)*100:.1f}%", ha='center', va='center', fontsize=16, color='#c1121f')

    ax.add_patch(FancyBboxPatch((0.15, 0.40), 0.7, 0.2, boxstyle="round,pad=0.05", ec="none", fc="#e8f5e9", alpha=0.8))
    ax.text(0.5, 0.5, f"5-Year Survival: {survival_prob(60)*100:.1f}%", ha='center', va='center', fontsize=16, color='#2e7d32')

    ax.add_patch(FancyBboxPatch((0.15, 0.15), 0.7, 0.2, boxstyle="round,pad=0.05", ec="none", fc="#e3f2fd", alpha=0.8))
    ax.text(0.5, 0.25, f"Happiness Score: {happiness:.0f}/100", ha='center', va='center', fontsize=16, color='#1565c0')

    ax.text(0.5, 0.05, "Powered by QuantYourLife", ha='center', va='center', fontsize=10, color='#757575', style='italic')
    ax.axis('off')

    buf = BytesIO()
    fig_summary.savefig(buf, format="png", bbox_inches='tight', dpi=150)
    buf.seek(0)
    st.download_button("Download Shareable Summary Card (PNG)", buf.getvalue(), "relationship_summary_card.png", "image/png")

    plt.close(fig_summary)

# Monetization Banner
st.markdown("---")
st.markdown("""
<div style="background:#f8f9fa; padding:20px; border-radius:12px; text-align:center; border:1px solid #dee2e6;">
    <h3 style="margin:0;">Unlock Premium Features</h3>
    <p style="margin:12px 0 8px; font-size:16px;">For $4.99 one-time you get:</p>
    <ul style="text-align:left; max-width:500px; margin:0 auto 16px;">
        <li>Extra inputs: intimacy frequency, age at start, financial compatibility</li>
        <li>Beautiful downloadable PDF report</li>
        <li>Shareable summary card image</li>
    </ul>
    <a href="YOUR_GUMROAD_PRODUCT_LINK_HERE" target="_blank" style="display:inline-block; padding:14px 36px; background:#0d6efd; color:white; border-radius:8px; text-decoration:none; font-weight:bold; font-size:18px;">
        Pay $4.99 & Get Code
    </a>
    <p style="margin-top:20px; font-size:14px;">
        Already paid? Enter your code in the sidebar box.
    </p>
</div>
""", unsafe_allow_html=True)

st.caption("Simplified exponential survival model based on Gottman Institute data. Educational/entertainment use only.")

st.caption("Simplified exponential survival model based on Gottman Institute data. Educational/entertainment use only.")
