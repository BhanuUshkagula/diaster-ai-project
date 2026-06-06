import streamlit as st
import spacy
from openai import OpenAI

# ==============================
# 🔐 SET YOUR OPENAI API KEY
# ==============================
client = OpenAI(api_key="YOUR_API_KEY")

# Load spaCy model
nlp = spacy.load("en_core_web_sm")


# ==================================
# 🧠 Agent 1: Disaster Classification
# ==================================
def classify_disaster(text):
    prompt = f"""
    Identify the disaster type from the message.
    Categories: Flood, Fire, Earthquake, Medical Emergency, Cyclone, Other.

    Message: {text}

    Return only the category name.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content.strip()


# ==================================
# 🚨 Agent 2: Urgency Detection
# ==================================
def detect_urgency(text):
    prompt = f"""
    Determine urgency level of this message.
    Categories: High, Medium, Low.

    Message: {text}

    Return only one word.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content.strip()


# ==================================
# 📍 Agent 3: Location Extraction
# ==================================
def extract_location(text):
    doc = nlp(text)
    locations = [ent.text for ent in doc.ents if ent.label_ == "GPE"]

    if locations:
        return ", ".join(locations)
    else:
        return "Location Not Found"


# ==================================
# 🏥 Agent 4: Response Generator
# ==================================
def generate_action(text, disaster, urgency):
    prompt = f"""
    Based on the disaster message, disaster type, and urgency,
    suggest a short and practical action for emergency authorities.

    Message: {text}
    Disaster Type: {disaster}
    Urgency: {urgency}

    Keep response concise.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content.strip()


# ==================================
# 🌪 Streamlit User Interface
# ==================================
st.set_page_config(page_title="Agentic AI Disaster Response", layout="centered")

st.title("🌪 Agentic AI Disaster Response System")
st.write("Enter an emergency message to analyze.")

user_input = st.text_area("Emergency Message")

if st.button("Analyze Emergency"):

    if user_input.strip() == "":
        st.warning("Please enter an emergency message.")
    else:
        with st.spinner("Analyzing with AI Agents..."):

            disaster = classify_disaster(user_input)
            urgency = detect_urgency(user_input)
            location = extract_location(user_input)
            action = generate_action(user_input, disaster, urgency)

        st.success("Analysis Complete")

        st.subheader("📊 Analysis Result")
        st.write("**Disaster Type:**", disaster)
        st.write("**Urgency Level:**", urgency)
        st.write("**Location:**", location)
        st.write("**Recommended Action:**", action)
