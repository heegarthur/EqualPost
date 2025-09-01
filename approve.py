import os
import pandas as pd
import joblib
from langdetect import detect, DetectorFactory
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report

DetectorFactory.seed = 0  # voor consistente detecties

# --------------------------
# Config
# --------------------------
DATA_FILE = "data.csv"
MODEL_FILE = "post_model.pkl"
MAX_LENGTH = 700   # max karakters
MIN_WORDS = 3      # min woorden
BLOCK_NON_ENGLISH = True

# --------------------------
# Train functie
# --------------------------
def train_model(data_file=DATA_FILE, model_file=MODEL_FILE):
    data = pd.read_csv(data_file)
    posts = data["post"].values
    labels = data["label"].values

    clf = Pipeline([
        ("tfidf", TfidfVectorizer(lowercase=True, stop_words="english")),
        ("lr", LogisticRegression(max_iter=1000, class_weight="balanced"))
    ])

    clf.fit(posts, labels)

    # Eval
    preds = clf.predict(posts)
    print("Training report:\n", classification_report(labels, preds))

    # Save
    joblib.dump(clf, model_file)
    print(f"Model saved to {model_file}")

# --------------------------
# Load model
# --------------------------
def load_model(model_file=MODEL_FILE):
    if not os.path.exists(model_file):
        print("No trained model found. Training new one...")
        train_model()
    return joblib.load(model_file)

# --------------------------
# Check post
# --------------------------
def check_post(content, model_file=MODEL_FILE):
    # Te lang?
    if len(content) > MAX_LENGTH:
        return "too long"
    
    # Te kort?
    if len(content.split()) < MIN_WORDS:
        return "too short"

    # Taal detectie
    lang = "unknown"
    try:
        lang = detect(content)
    except:
        pass

    if BLOCK_NON_ENGLISH and lang != "en":
        return "bad"

    # Model check
    clf = load_model(model_file)
    pred = clf.predict([content])[0]
    return pred

# --------------------------
# Test
# --------------------------
if __name__ == "__main__":
    clf = load_model()

    tests = [
        "I love my cat",
        "Je suis très heureux",
        "trump vote for trump",
        "Dit is een test",
        "Hi",
        "Buy cheap products at http://spam.com",
        "Going to the park is fun",
        "jezus loves everyone"
    ]

    for t in tests:
        print(f"'{t}' -> {check_post(t)}")
