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
st.markdown("Quant model based on Gottman Institute research + survival analysis.", unsafe_allow_html=True)

# Sidebar Inputs
st.sidebar.header("Your Relationship Data")

st.sidebar.markdown("**Compatibility & Communication**")
compatibility = st.sidebar.slider("Compatibility score (0–10)", 0.0, 10.0, 6.5, 0.1)
pos_neg_ratio = st.sidebar.slider(
    "Positive:Negative interaction ratio",
    0.5, 10.0, 3.5, 0.1,
    help="""Gottman's 'Magic Ratio': In stable relationships, there are at least 5 positive interactions (compliments, affection, laughter, support) for every 1 negative interaction (criticism, sarcasm, argument). 
Count typical daily/weekly interactions — aim for 5:1 or higher (e.g. 5.0+ on slider). Below 1:1 predicts high risk."""
)

st.sidebar.markdown("**Conflict & Repair**")
conflict_freq = st.sidebar.slider("Conflicts per month", 0, 20, 4)
four_horsemen = st.sidebar.slider(
    "Four Horsemen severity (0=none – 10=severe)",
    0, 10, 3,
    help="Criticism, Contempt, Defensiveness, Stonewalling — rate how often/intensely these appear in arguments."
)
repair_success = st.sidebar.slider("Repair attempt success (0–10)", 0, 10, 6, help="How well do you de-escalate / make up after fights?")

st.sidebar.markdown("**Life & Values**")
shared_values = st.sidebar.slider("Shared values/goals (0–10)", 0.0, 10.0, 6.0, 0.1)
external_stress = st.sidebar.slider("External stress (finances/work/family, 0–10)", 0, 10, 4)

time_together = st.sidebar.number_input("Time together (months)", min_value=1, value=18, step=1)

# Premium code input
st.sidebar.markdown("**Premium Access**")
premium_code = st.sidebar.text_input("Enter Premium Code (from Gumroad email)", "")
premium = premium_code.strip() == "PREMIUM2026"  # Change if you used a different code

if premium:
    st.sidebar.success("Premium unlocked! Extra variables + downloads available.")
else:
    if premium_code.strip():
        st.sidebar.error("Invalid code. Get yours for $4.99 on Gumroad.")
    else:
        st.sidebar.info("Enter code to unlock premium features")

# Premium variables
if premium:
    st.sidebar.markdown("**Premium Variables**")
    intimacy_freq = st.sidebar.slider("Physical intimacy frequency (times/month)", 0, 30, 8, 1)
    age_at_start = st.sidebar.slider("Age when relationship started (years)", 18, 50, 25, 1)
    financial_compat = st.sidebar.slider("Financial compatibility (0–10)", 0.0, 10.0, 6.0, 0.1)
else:
    intimacy_freq = 8
    age_at_start = 25
    financial_compat = 6.0

# Model
lambda_base = 0.028

lambda_penalty = (
    0.014 * (5.0 - pos_neg_ratio) +
    0.009 * conflict_freq +
    0.010 * four_horsemen +
    -0.007 * compatibility +
    -0.006 * shared_values +
    0.008 * external_stress +
    -0.007 * repair_success +
    -0.005 * (intimacy_freq / 10) +
    0.0025 * max(0, abs(age_at_start - 28)) +
    -0.006 * financial_compat
)

lambda_monthly = max(0.008, lambda_base + lambda_penalty)

def survival_prob(months):
    return np.exp(-lambda_monthly * months)

happiness = max(10, min(100,
    60 +
    4.0 * compatibility +
    3.0 * pos_neg_ratio +
    -2.5 * conflict_freq +
    -3.5 * four_horsemen +
    3.5 * shared_values +
    -2.8 * external_stress +
    4.0 * repair_success +
    2.5 * (intimacy_freq / 5) +
    -1.5 * max(0, abs(age_at_start - 28)) +
    3.0 * financial_compat
))

# Main Outputs
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
    "Pos:Neg Ratio": 3.0 * pos_neg_ratio,
    "Conflicts": -2.5 * conflict_freq,
    "Four Horsemen": -3.5 * four_horsemen,
    "Shared Values": 3.5 * shared_values,
    "External Stress": -2.8 * external_stress,
    "Repair Success": 4.0 * repair_success,
}
if premium:
    impact_data["Intimacy Freq"] = 2.5 * (intimacy_freq / 5)
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
    # Detailed PDF Report
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 15, "Your Personalized Relationship Report", ln=1, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"Current Duration: {time_together} months", ln=1)
    pdf.ln(5)
    pdf.cell(0, 10, "Key Predictions", ln=1)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"1-Year Survival Probability: {survival_prob(12)*100:.1f}%", ln=1)
    pdf.cell(0, 8, f"5-Year Survival Probability: {survival_prob(60)*100:.1f}%", ln=1)
    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Happiness Estimate", ln=1)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Score: {happiness:.0f}/100", ln=1)
    pdf.cell(0, 8, f"Interpretation: {'Outstanding' if happiness >= 90 else 'Excellent' if happiness >= 80 else 'Strong' if happiness >= 70 else 'Good' if happiness >= 60 else 'Moderate' if happiness >= 50 else 'Needs attention'}", ln=1)
    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Your Strengths", ln=1)
    pdf.set_font("Arial", "", 11)
    strengths = []
    if compatibility >= 8: strengths.append("- High compatibility is a major strength")
    if pos_neg_ratio >= 5: strengths.append("- Excellent positive interaction ratio")
    if repair_success >= 8: strengths.append("- Strong repair skills during conflicts")
    if shared_values >= 8: strengths.append("- Aligned values and goals")
    if intimacy_freq >= 12 and premium: strengths.append("- Healthy intimacy frequency")
    if financial_compat >= 8 and premium: strengths.append("- Solid financial harmony")
    if not strengths: strengths.append("- Building positive patterns will strengthen your foundation")
    pdf.multi_cell(0, 6, "\n".join(strengths))
    pdf.ln(8)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Areas to Watch", ln=1)
    pdf.set_font("Arial", "", 11)
    risks = []
    if conflict_freq >= 6: risks.append("- Frequent conflicts can build up over time")
    if four_horsemen >= 4: risks.append("- Watch for toxic patterns like contempt or stonewalling")
    if external_stress >= 6: risks.append("- External stress is impacting stability")
    if not risks: risks.append("- You're in a great spot - keep nurturing what works")
    pdf.multi_cell(0, 6, "\n".join(risks))
    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Quick Tips to Improve", ln=1)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 6, "- Aim for 5+ positive interactions per negative one\n"
                         "- Practice repair attempts during arguments\n"
                         "- Schedule regular check-ins on goals and finances\n"
                         "- Keep nurturing intimacy and shared experiences")
    pdf.ln(10)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 8, "Made by @views094 - For entertainment & insight only.", ln=1, align="C")

    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_bytes = pdf_output.getvalue()

    st.download_button("Download Detailed PDF Report", pdf_bytes, "relationship_report.pdf", "application/pdf")

    # Shareable Summary Card
    fig_summary, ax = plt.subplots(figsize=(8, 5))
    fig_summary.patch.set_facecolor('#fff0f5')
    ax.set_facecolor('#fff0f5')
    ax.add_patch(plt.Rectangle((0,0),1,1, transform=ax.transAxes, color='#ffebee', alpha=0.7))
    ax.text(0.5, 0.92, "❤️ My Relationship Snapshot ❤️", ha='center', fontsize=20, fontweight='bold', color='#c62828')
    ax.text(0.5, 0.75, f"1-Year Survival: {survival_prob(12)*100:.1f}%", ha='center', fontsize=18, color='#b71c1c')
    ax.text(0.5, 0.55, f"5-Year Survival: {survival_prob(60)*100:.1f}%", ha='center', fontsize=18, color='#2e7d32')
    ax.text(0.5, 0.35, f"Happiness: {happiness:.0f}/100", ha='center', fontsize=18, color='#1565c0')
    ax.text(0.5, 0.15, "@views094 • Quant Insights", ha='center', fontsize=12, color='#757575', style='italic')
    ax.axis('off')

    buf = BytesIO()
    fig_summary.savefig(buf, format="png", bbox_inches='tight', dpi=200, facecolor=fig_summary.get_facecolor())
    buf.seek(0)
    st.download_button("Download Shareable Card (PNG)", buf.getvalue(), "relationship_card.png", "image/png")
    plt.close(fig_summary)

# Monetization Banner
st.markdown("---")
st.markdown("""
<div style="background:#f8f9fa; padding:20px; border-radius:12px; text-align:center; border:1px solid #dee2e6;">
    <h3 style="margin:0;">Unlock Premium Features</h3>
    <p style="margin:12px 0 8px; font-size:16px;">For $0.99 one-time you get:</p>
    <ul style="text-align:left; max-width:500px; margin:0 auto 16px;">
        <li>Extra inputs: intimacy frequency, age at start, financial compatibility</li>
        <li>Detailed, beautiful PDF report</li>
        <li>Shareable summary card image</li>
    </ul>
    <a href="YOUR_GUMROAD_PRODUCT_LINK_HERE" target="_blank" style="display:inline-block; padding:14px 36px; background:#0d6efd; color:white; border-radius:8px; text-decoration:none; font-weight:bold; font-size:18px;">
        Pay $0.99 & Get Code
    </a>
    <p style="margin-top:20px; font-size:14px;">
        Already paid? Enter your code in the sidebar box.
    </p>
</div>
""", unsafe_allow_html=True)

st.caption("Simplified exponential survival model based on Gottman Institute data. Educational/entertainment use only. Made by @views094")
