import streamlit as st
from agents.prediction_agent import PredictionAgent
from agents.communication_agent import CommunicationAgent

prediction_agent    = PredictionAgent("models/disaster_model.pkl")
communication_agent = CommunicationAgent()

st.set_page_config(page_title="Disaster Alert System", page_icon="🚨", layout="centered")

st.markdown("""
<style>
    .alert-box {
        background: linear-gradient(135deg, #ff4444, #cc0000);
        border-radius: 16px;
        padding: 30px;
        text-align: center;
        color: white;
        margin: 20px 0;
        box-shadow: 0 4px 20px rgba(255,0,0,0.3);
    }
    .alert-title { font-size: 2.5em; font-weight: bold; margin-bottom: 10px; }
    .alert-body  { font-size: 1.3em; line-height: 1.7; }
</style>
""", unsafe_allow_html=True)

st.title("🚨 Disaster Alert System")
st.markdown("Send instant danger alerts to the public via SMS")
st.divider()

# ── Step 1: Basic Info ──────────────────────────────────────────────────────
st.subheader("📍 Disaster Information")

col1, col2 = st.columns(2)
with col1:
    disaster_type = st.selectbox(
        "Disaster Type",
        ["Flood", "Cyclone", "Earthquake", "Landslide", "Fire", "Tsunami", "General Emergency"]
    )
with col2:
    severity = st.selectbox(
        "Severity Level",
        ["Extreme", "Severe", "High", "Moderate", "Low"]
    )

location = st.text_input("📍 Affected Location", placeholder="e.g. Chennai, Tamil Nadu")

SEVERITY_EMOJI = {
    "Extreme": "🔴🔴🔴", "Severe": "🔴🔴",
    "High": "🟠", "Moderate": "🟡", "Low": "🟢",
}
SAFETY_TIPS = {
    "Flood":             "Move to higher ground immediately. Do NOT walk through floodwater.",
    "Cyclone":           "Stay indoors away from windows. Move to a strong building.",
    "Earthquake":        "Drop, Cover, and Hold On. Stay away from buildings after shaking stops.",
    "Landslide":         "Evacuate the area immediately. Move to flat ground away from slopes.",
    "Fire":              "Evacuate immediately. Cover your nose with a wet cloth.",
    "Tsunami":           "Move inland to higher ground NOW. Do not wait for official orders.",
    "General Emergency": "Follow official instructions. Move to the nearest safe zone.",
}

emoji   = SEVERITY_EMOJI.get(severity, "🔴")
tip     = SAFETY_TIPS.get(disaster_type, "Move to a safe zone immediately.")
loc_str = location.strip() if location.strip() else "your area"

public_message = (
    f"{emoji} DANGER ALERT {emoji}\n"
    f"WARNING: {disaster_type.upper()} in {loc_str}!\n"
    f"Severity: {severity}\n\n"
    f"ACTION: {tip}\n\n"
    f"Emergency Helpline: 112\n"
    f"Move to nearest safe zone NOW!\n"
    f"-- Disaster Management Authority"
)

# ── Live Alert Preview ──────────────────────────────────────────────────────
st.subheader("📢 Alert Message Preview")
st.markdown(f"""
<div class="alert-box">
  <div class="alert-title">{emoji} DANGER ALERT</div>
  <div class="alert-body">
    <b>{disaster_type.upper()}</b> in <b>{loc_str}</b><br>
    Severity: <b>{severity}</b><br><br>
    ⚠️ {tip}<br><br>
    📞 Emergency: <b>112</b><br>
    🏥 <b>Move to the nearest safe zone NOW!</b>
  </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── Step 2: Send SMS ────────────────────────────────────────────────────────
st.subheader("📱 Send SMS Alert to People")

sms_provider = st.radio(
    "Choose SMS Provider",
    ["Fast2SMS (India — Free)", "Twilio (Worldwide)"],
    horizontal=True,
)

if sms_provider == "Fast2SMS (India — Free)":
    st.info("✅ Free for India | Sign up at fast2sms.com → Dev API → copy API Key")
    fast2sms_key = st.text_input("Fast2SMS API Key", type="password")
    numbers_raw  = st.text_area(
        "Mobile Numbers (10 digits, one per line)",
        placeholder="9876543210\n9123456789\n8012345678"
    )
    twilio_sid = twilio_token = twilio_from = ""
else:
    st.info("✅ Works worldwide | Sign up at twilio.com → copy SID & Token")
    twilio_sid   = st.text_input("Account SID",  type="password")
    twilio_token = st.text_input("Auth Token",   type="password")
    twilio_from  = st.text_input("Twilio Number (e.g. +15551234567)")
    numbers_raw  = st.text_area(
        "Mobile Numbers (with country code, one per line)",
        placeholder="+919876543210\n+918012345678"
    )
    fast2sms_key = ""

st.divider()

if st.button("🚨 SEND DANGER ALERT TO ALL", use_container_width=True, type="primary"):
    if not location.strip():
        st.warning("⚠️ Please enter the affected location.")
    elif not numbers_raw.strip():
        st.warning("⚠️ Please enter at least one phone number.")
    else:
        raw     = numbers_raw.replace(",", "\n")
        numbers = [n.strip() for n in raw.splitlines() if n.strip()]

        with st.spinner(f"Sending alert to {len(numbers)} people..."):
            if sms_provider == "Fast2SMS (India — Free)":
                if not fast2sms_key:
                    st.error("❌ Please enter your Fast2SMS API Key.")
                else:
                    result = communication_agent.send_sms_fast2sms(public_message, numbers, fast2sms_key)
                    if result["success"]:
                        st.success(f"✅ Danger alert sent to {len(numbers)} people!")
                        st.balloons()
                    else:
                        st.error(result["message"])
            else:
                if not (twilio_sid and twilio_token and twilio_from):
                    st.error("❌ Please fill in all Twilio credentials.")
                else:
                    result = communication_agent.send_sms_twilio(
                        public_message, numbers, twilio_sid, twilio_token, twilio_from
                    )
                    if result["success"]:
                        st.success(f"✅ Danger alert sent to {len(numbers)} people!")
                        st.balloons()
                    else:
                        st.error(result["message"])

        with st.expander("📋 View exact SMS message sent"):
            st.code(public_message)
