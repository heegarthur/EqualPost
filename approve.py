import os
import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report

# --------------------------
# Config
# --------------------------
DATA_FILE = "data.csv"   # CSV met kolommen: post,label
MODEL_FILE = "post_model.pkl"

# --------------------------
# Train functie
# --------------------------
def train_model(data_file=DATA_FILE, model_file=MODEL_FILE):
    # Dataset laden
    data = pd.read_csv(data_file)
    posts = data["post"].values
    labels = data["label"].values

    # Pipeline: TF-IDF + Logistic Regression
    clf = Pipeline([
        ("tfidf", TfidfVectorizer(lowercase=True, stop_words="english")),
        ("lr", LogisticRegression(max_iter=1000, class_weight="balanced"))
    ])

    # Trainen
    clf.fit(posts, labels)

    # Train evaluatie
    preds = clf.predict(posts)
    print("Training report:\n", classification_report(labels, preds))

    # Opslaan
    joblib.dump(clf, model_file)
    print(f"Model saved to {model_file}")

# --------------------------
# Laden en checken
# --------------------------
def load_model(model_file=MODEL_FILE):
    if not os.path.exists(model_file):
        print("No trained model found. Training new one...")
        train_model()
    return joblib.load(model_file)

def check_post(content, model_file=MODEL_FILE):
    clf = load_model(model_file)
    if len(content) > 700:
        return "too long"
    pred = clf.predict([content])[0]
    return pred

# --------------------------
# Direct test
# --------------------------
if __name__ == "__main__":
    if not os.path.exists(MODEL_FILE):
        train_model()

    clf = load_model()

    tests = [
        "I love my cat",
        "Buy cheap products at http://spam.com",
        "trump vote for trump",
        "I had a horrible day",
        "jezus loves you everyone should be cristian",
        "Going to the park is fun"
    ]

    for t in tests:
        print(t, "->", check_post(t))
