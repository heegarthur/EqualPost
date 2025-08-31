
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS   # zodat frontend requests werken

app = Flask(__name__)
CORS(app)  # staat JavaScript toe om met Flask te praten

# ---------------- Database configuratie ----------------
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///posts.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ---------------- Model ----------------
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {"id": self.id, "title": self.title, "content": self.content}

# ---------------- Database aanmaken ----------------
with app.app_context():
    db.create_all()

# ---------------- API Routes ----------------

# Alle posts ophalen
@app.route("/api/posts", methods=["GET"])
def get_posts():
    posts = Post.query.all()
    return jsonify([p.to_dict() for p in posts])

# Nieuwe post toevoegen
@app.route("/api/posts", methods=["POST"])
def add_post():
    data = request.json
    if not data or "title" not in data or "content" not in data:
        return jsonify({"error": "Invalid input"}), 400

    new_post = Post(title=data["title"], content=data["content"])
    db.session.add(new_post)
    db.session.commit()
    return jsonify({"message": "Post added!", "post": new_post.to_dict()}), 201

# Eén post ophalen
@app.route("/api/posts/<int:post_id>", methods=["GET"])
def get_post(post_id):
    post = Post.query.get_or_404(post_id)
    return jsonify(post.to_dict())

# Post updaten
@app.route("/api/posts/<int:post_id>", methods=["PUT"])
def update_post(post_id):
    data = request.json
    post = Post.query.get_or_404(post_id)
    post.title = data.get("title", post.title)
    post.content = data.get("content", post.content)
    db.session.commit()
    return jsonify({"message": "Post updated!", "post": post.to_dict()})

# Post verwijderen
@app.route("/api/posts/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return jsonify({"message": "Post deleted!"})

# ---------------- Run server ----------------
if __name__ == "__main__":
    app.run(debug=True)
