import numpy as np
import pandas as pd
import os

# --------------------------
# Config
# --------------------------
DATA_FILE = "data.csv"   # CSV with columns: post,label
EPOCHS = 500
LR = 0.01
HIDDEN_SIZE = 5

# --------------------------
# Helpers
# --------------------------
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def build_vocab(posts):
    vocab = {}
    for post in posts:
        for word in post.lower().split():
            if word not in vocab:
                vocab[word] = len(vocab)
    return vocab

def text_to_vector(post, vocab):
    vec = np.zeros(len(vocab))
    for word in post.lower().split():
        if word in vocab:
            vec[vocab[word]] += 1
    return vec

# --------------------------
# Classifier
# --------------------------
class PostChecker:
    def __init__(self):
        self.vocab = None
        self.W1 = None
        self.b1 = None
        self.W2 = None
        self.b2 = None

    def train(self, data_file=DATA_FILE, epochs=EPOCHS, lr=LR, hidden_size=HIDDEN_SIZE):
        data = pd.read_csv(data_file)
        posts = data['post'].values
        labels = np.array([1 if l.lower() == "good" else 0 for l in data['label'].values])

        # vocab & vectors
        self.vocab = build_vocab(posts)
        X = np.array([text_to_vector(p, self.vocab) for p in posts])

        input_size = X.shape[1]
        output_size = 1

        # initialize weights
        np.random.seed(42)
        self.W1 = np.random.randn(input_size, hidden_size) * 0.01
        self.b1 = np.zeros(hidden_size)
        self.W2 = np.random.randn(hidden_size, output_size) * 0.01
        self.b2 = np.zeros(output_size)

        # training loop
        for epoch in range(epochs):
            Z1 = np.dot(X, self.W1) + self.b1
            A1 = np.tanh(Z1)
            Z2 = np.dot(A1, self.W2) + self.b2
            A2 = sigmoid(Z2)
            loss = -np.mean(labels*np.log(A2+1e-8) + (1-labels)*np.log(1-A2+1e-8))

            # backprop
            dZ2 = A2 - labels.reshape(-1,1)
            dW2 = np.dot(A1.T, dZ2)/X.shape[0]
            db2 = np.mean(dZ2, axis=0)
            dA1 = np.dot(dZ2, self.W2.T)
            dZ1 = dA1 * (1 - A1**2)
            dW1 = np.dot(X.T, dZ1)/X.shape[0]
            db1 = np.mean(dZ1, axis=0)

            self.W1 -= lr * dW1
            self.b1 -= lr * db1
            self.W2 -= lr * dW2
            self.b2 -= lr * db2

            if (epoch+1)%100 == 0:
                print(f"Epoch {epoch+1}, Loss: {loss:.4f}")

        # save weights
        np.savez("post_model.npz", W1=self.W1, b1=self.b1, W2=self.W2, b2=self.b2, vocab=self.vocab)

    def load(self, path="post_model.npz"):
        data = np.load(path, allow_pickle=True)
        self.W1 = data["W1"]
        self.b1 = data["b1"]
        self.W2 = data["W2"]
        self.b2 = data["b2"]
        self.vocab = data["vocab"].item()

    def check(self, post):
        if self.vocab is None:
            raise Exception("Model not loaded or trained")
        x = text_to_vector(post, self.vocab)
        a1 = np.tanh(np.dot(x, self.W1) + self.b1)
        a2 = sigmoid(np.dot(a1, self.W2) + self.b2)
        return "good" if a2 > 0.5 else "bad"


# --------------------------
# Direct test
# --------------------------
def check_post(content):
    if len(content) > 700:
        return "too long"
    pc = PostChecker()
    if not os.path.exists("post_model.npz"):
        print("Training new model...")
        pc.train()
    else:
        pc.load()

    test_post = content
    ending = pc.check(test_post)
    return ending

if __name__ == "__main__":
    pc = PostChecker()
    if not os.path.exists("post_model.npz"):
        print("Training new model...")
        pc.train()
    else:
        pc.load()

    test_post = "This is an amazing day!"
    print(test_post, "->", pc.check(test_post))
