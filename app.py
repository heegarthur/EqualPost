from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta
from sqlalchemy.sql import func
import approve, time



app = Flask(__name__)
CORS(app)

ip_requests = {}
LIMIT_SECONDS = 14400  # 1 minuut

# Database configuratie
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///posts.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

def check_ip_limit():
    ip = request.remote_addr
    now = time.time()

    if ip in ip_requests:
        last_request = ip_requests[ip]
        if now - last_request < LIMIT_SECONDS:
            return False  # te snel opnieuw
    ip_requests[ip] = now
    return True  # mag doorgaan

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
    if not check_ip_limit():
        return jsonify({"status":"rejected","reason":"Too many requests, wait a bit"}), 429
    

    data = request.json
    if not data or "title" not in data or "content" not in data:
        return jsonify({"status":"error","reason": "Invalid input"}), 400

    post_check = f"{data['title']} {data['content']}"
    approved = approve.check_post(post_check)
    print(post_check)
    if approved.lower() == "good":
        new_post = Post(title=data["title"], content=data["content"])
        db.session.add(new_post)
        db.session.commit()
        return jsonify({"status":"approved","message": "Post created successfully!", "post": new_post.to_dict()}), 201
    elif approved.lower() == "bad":
        return jsonify({"status":"rejected","reason":"Post rejected by AI moderation"}), 200
    elif approved.lower() == "english":
        return jsonify({"status":"rejected","reason":"Post is not in English"})
    elif approved.lower() == "lang err":
        return jsonify({"status":"rejected","reason":"unknown language error: language not detected"})
    elif approved.lower() == "too long":
        return jsonify({"status":"rejected","reason":"Post is too long"})
    else:
        return jsonify({"status":"error","reason":"Unknown AI approval error"}), 500

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
