import joblib
import pandas as pd

class PredictionAgent:

    def __init__(self, model_path):
        self.model = joblib.load(model_path)

    def detect_disaster(self, message):
        message = message.lower()

        if "flood" in message:
            return "Flood"
        elif "cyclone" in message:
            return "Cyclone"
        elif "earthquake" in message:
            return "Earthquake"
        else:
            return "General"

    def predict_severity(self, input_data):
        df = pd.DataFrame([input_data])
        return self.model.predict(df)[0]
