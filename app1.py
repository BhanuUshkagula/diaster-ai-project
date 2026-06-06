import streamlit as st
from agents.prediction_agent import PredictionAgent
from agents.monitoring_agent import MonitoringAgent
from agents.resource_agent import ResourceAgent
from agents.communication_agent import CommunicationAgent

prediction_agent = PredictionAgent("models/disaster_model.pkl")
monitoring_agent = MonitoringAgent()
resource_agent = ResourceAgent()
communication_agent = CommunicationAgent()

st.title("🌍 AI Disaster Response Multi-Agent System")

# Step 1: Message Input
message = st.text_area("Enter Emergency Message")

if st.button("Detect Disaster Type"):

    if message.strip() == "":
        st.warning("Please enter emergency message.")
    else:
        disaster_type = prediction_agent.detect_disaster(message)
        st.session_state.disaster_type = disaster_type

# Step 2: Dynamic Form
if "disaster_type" in st.session_state:

    st.success(f"Detected Disaster: {st.session_state.disaster_type}")

    st.subheader("Enter Environmental Parameters")

    rainfall_mm = st.number_input("Rainfall (mm)", 0.0)
    river_level = st.number_input("River Level", 0.0)
    wind_speed = st.number_input("Wind Speed", 0.0)
    temperature = st.number_input("Temperature", 0.0)
    humidity = st.number_input("Humidity", 0.0)
    soil_moisture = st.number_input("Soil Moisture", 0.0)
    urban_area = st.number_input("Urban Area (0 or 1)", 0)
    drainage_index = st.number_input("Drainage Index", 0.0)
    available_rescue = st.number_input("Available Rescue Teams", 0)
    available_relief = st.number_input("Available Relief Units", 0)
    available_shelter = st.number_input("Available Shelters", 0)
    nearest_hospital_distance = st.number_input("Nearest Hospital Distance", 0.0)
    evacuation_centers = st.number_input("Evacuation Centers", 0)
    location = st.text_input("Location")

    if st.button("Analyze Disaster"):

        input_data = {
            "rainfall_mm": rainfall_mm,
            "river_level": river_level,
            "wind_speed": wind_speed,
            "temperature": temperature,
            "humidity": humidity,
            "soil_moisture": soil_moisture,
            "urban_area": urban_area,
            "drainage_index": drainage_index,
            "available_rescue": available_rescue,
            "available_relief": available_relief,
            "available_shelter": available_shelter,
            "nearest_hospital_distance": nearest_hospital_distance,
            "evacuation_centers": evacuation_centers
        }

        severity = prediction_agent.predict_severity(input_data)

        monitoring_status = monitoring_agent.monitor(
            st.session_state.disaster_type, severity
        )

        resources = resource_agent.allocate_resources(severity)

        alert = communication_agent.generate_alert(
            st.session_state.disaster_type,
            severity,
            location
        )

        st.success("Analysis Completed")

        st.write("### 📊 Predicted Severity")
        st.write(severity)

        st.write("### 🛰 Monitoring Status")
        st.write(monitoring_status)

        st.write("### 🚑 Resource Allocation")
        st.write(resources)

        st.write("### 📢 Alert Message")
        st.write(alert)
