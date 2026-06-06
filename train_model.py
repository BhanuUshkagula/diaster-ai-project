import pandas as pd
import joblib
import re

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Load dataset
df = pd.read_csv("data/disaster_dataset.csv")

print("Columns:", df.columns)

# Change these two lines according to your dataset
TEXT_COLUMN = df.columns[0]
TARGET_COLUMN = df.columns[1]

print("Using text column:", TEXT_COLUMN)
print("Using target column:", TARGET_COLUMN)

# Clean text
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    return text

df[TEXT_COLUMN] = df[TEXT_COLUMN].apply(clean_text)

X = df[TEXT_COLUMN]
y = df[TARGET_COLUMN]

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Build model
model = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1,2), max_features=10000)),
    ("clf", RandomForestClassifier(n_estimators=300, random_state=42))
])

# Train
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print("Model Accuracy:", accuracy)

# Save model
joblib.dump(model, "models/disaster_model.pkl")

print("✅ Model trained and saved successfully!")
