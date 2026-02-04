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
st.markdown("Quant model based on Gottman Institute research + survival analysis<br>Free: 7 variables. Premium: extra inputs + detailed PDF + shareable card", unsafe_allow_html=True)

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
conflict_freq = st.sidebar.slider("Conflicts  per month", 0, 20, 4)
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
… (rest of the code unchanged from previous version)
