from flask import Flask, request, jsonify, session
from flask_migrate import Migrate
from flask_cors import CORS

from models import db, bcrypt, User, Note

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "secret123"

CORS(app, supports_credentials=True)

db.init_app(app)
bcrypt.init_app(app)
migrate = Migrate(app, db)


def current_user():
    user_id = session.get("user_id")

    if not user_id:
        return None

    return User.query.get(user_id)


@app.route("/")
def home():
    return "Backend Running"


@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()

    user = User(username=data["username"])
    user.set_password(data["password"])

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created"}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    user = User.query.filter_by(username=data["username"]).first()

    if user and user.check_password(data["password"]):
        session["user_id"] = user.id
        return jsonify({"id": user.id, "username": user.username})

    return jsonify({"error": "Invalid login"}), 401


@app.route("/check_session")
def check_session():
    user = current_user()

    if user:
        return jsonify({"id": user.id, "username": user.username})

    return jsonify({"error": "Unauthorized"}), 401


@app.route("/logout", methods=["DELETE"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})


@app.route("/notes", methods=["GET"])
def get_notes():
    user = current_user()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    page = request.args.get("page", 1, type=int)

    notes = Note.query.filter_by(user_id=user.id).paginate(
        page=page,
        per_page=5
    )

    result = []

    for note in notes.items:
        result.append({
            "id": note.id,
            "title": note.title,
            "content": note.content
        })

    return jsonify(result)


@app.route("/notes", methods=["POST"])
def create_note():
    user = current_user()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()

    note = Note(
        title=data["title"],
        content=data["content"],
        user_id=user.id
    )

    db.session.add(note)
    db.session.commit()

    return jsonify({"message": "Created"}), 201


@app.route("/notes/<int:id>", methods=["PATCH"])
def update_note(id):
    user = current_user()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    note = Note.query.get(id)

    if not note or note.user_id != user.id:
        return jsonify({"error": "Forbidden"}), 403

    data = request.get_json()

    note.title = data.get("title", note.title)
    note.content = data.get("content", note.content)

    db.session.commit()

    return jsonify({"message": "Updated"})


@app.route("/notes/<int:id>", methods=["DELETE"])
def delete_note(id):
    user = current_user()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    note = Note.query.get(id)

    if not note or note.user_id != user.id:
        return jsonify({"error": "Forbidden"}), 403

    db.session.delete(note)
    db.session.commit()

    return jsonify({"message": "Deleted"})


if __name__ == "__main__":
    app.run(port=5555, debug=True)
