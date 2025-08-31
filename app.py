from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta
from sqlalchemy.sql import func

app = Flask(__name__)
CORS(app)

# Database configuratie
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///posts.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Model
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "created_at": self.created_at.isoformat()
        }

# Database aanmaken
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

# Feed endpoint: willekeurig + recent
@app.route("/api/feed", methods=["GET"])
def get_feed():
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    # Haal query params op, standaard limit=10, offset=0
    limit = int(request.args.get("limit", 10))
    offset = int(request.args.get("offset", 0))
    
    posts = (
        Post.query
        .filter(Post.created_at >= thirty_days_ago)
        .order_by(func.random())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return jsonify([p.to_dict() for p in posts])

# Post ophalen / updaten / verwijderen
@app.route("/api/posts/<int:post_id>", methods=["GET"])
def get_post(post_id):
    post = Post.query.get_or_404(post_id)
    return jsonify(post.to_dict())

@app.route("/api/posts/<int:post_id>", methods=["PUT"])
def update_post(post_id):
    data = request.json
    post = Post.query.get_or_404(post_id)
    post.title = data.get("title", post.title)
    post.content = data.get("content", post.content)
    db.session.commit()
    return jsonify({"message": "Post updated!", "post": post.to_dict()})

@app.route("/api/posts/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return jsonify({"message": "Post deleted!"})

# Run server
if __name__ == "__main__":
    app.run(debug=True)
