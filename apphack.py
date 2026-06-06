import streamlit as st
import spacy
from transformers import pipeline

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Load free HuggingFace models
classifier = pipeline("text-classification", model="facebook/bart-large-mnli")
sentiment = pipeline("sentiment-analysis")

# -----------------------------
# Agent 1: Disaster Classification
# -----------------------------
def classify_disaster(text):
    labels = ["Flood", "Fire", "Earthquake", "Medical Emergency", "Cyclone", "Other"]
    result = classifier(text, labels)
    return result["labels"][0]

# -----------------------------
# Agent 2: Urgency Detection
# -----------------------------
def detect_urgency(text):
    result = sentiment(text)[0]

    if result["label"] == "NEGATIVE" and result["score"] > 0.8:
        return "High"
    elif result["label"] == "NEGATIVE":
        return "Medium"
    else:
        return "Low"

# -----------------------------
# Agent 3: Location Extraction
# -----------------------------
def extract_location(text):
    doc = nlp(text)
    locations = [ent.text for ent in doc.ents if ent.label_ == "GPE"]

    if locations:
        return ", ".join(locations)
    else:
        return "Location Not Found"

# -----------------------------
# Agent 4: Response Suggestion
# -----------------------------
def generate_action(disaster, urgency):
    if urgency == "High":
        return f"Immediately dispatch emergency rescue team for {disaster}."
    elif urgency == "Medium":
        return f"Alert local authorities and monitor the {disaster} situation."
    else:
        return f"Record the {disaster} report and keep monitoring."

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("🌪 Agentic AI Disaster Response System (FREE VERSION)")

user_input = st.text_area("Enter Emergency Message")

if st.button("Analyze Emergency"):

    if user_input.strip() == "":
        st.warning("Please enter an emergency message.")
    else:
        disaster = classify_disaster(user_input)
        urgency = detect_urgency(user_input)
        location = extract_location(user_input)
        action = generate_action(disaster, urgency)

        st.subheader("📊 Analysis Result")
        st.write("**Disaster Type:**", disaster)
        st.write("**Urgency Level:**", urgency)
        st.write("**Location:**", location)
        st.write("**Recommended Action:**", action)
