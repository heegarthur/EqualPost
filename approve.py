import os
import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report


DATA_FILE = "data.csv"
MODEL_FILE = "post_model.pkl"
MAX_LENGTH = 700   
MIN_WORDS = 3      

def train_model(data_file=DATA_FILE, model_file=MODEL_FILE):
    data = pd.read_csv(data_file)
    posts = data["post"].values
    labels = data["label"].values

    clf = Pipeline([
        ("tfidf", TfidfVectorizer(lowercase=True, stop_words="english")),
        ("lr", LogisticRegression(max_iter=1000, class_weight="balanced"))
    ])

    clf.fit(posts, labels)

    preds = clf.predict(posts)
    print("Training report:\n", classification_report(labels, preds))

    joblib.dump(clf, model_file)
    print(f"Model saved to {model_file}")

def load_model(model_file=MODEL_FILE):
    if not os.path.exists(model_file):
        print("No trained model found. Training new one...")
        train_model()
    return joblib.load(model_file)

def check_post(content, model_file=MODEL_FILE):
    # Te lang?
    if len(content) > MAX_LENGTH:
        return "too long"
    
    if len(content.split()) < MIN_WORDS:
        return "too short"


    # Model check
    clf = load_model(model_file)
    pred = clf.predict([content])[0]
    return pred

