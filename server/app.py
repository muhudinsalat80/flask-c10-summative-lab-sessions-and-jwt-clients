# app.py

from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)

from config import create_app, db
from models import User, Task

app = create_app()

# ---------------- REGISTER ----------------
@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data received"}), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400

    user = User(username=username)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201


# ---------------- LOGIN ----------------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data received"}), 400

    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        token = create_access_token(identity=user.id)
        return jsonify(access_token=token), 200

    return jsonify({"error": "Invalid credentials"}), 401


# ---------------- GET TASKS ----------------
@app.route("/tasks", methods=["GET"])
@jwt_required()
def get_tasks():
    user_id = get_jwt_identity()

    page = request.args.get("page", 1, type=int)
    per_page = 5

    tasks = Task.query.filter_by(user_id=user_id).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    results = []

    for task in tasks.items:
        results.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed
        })

    return jsonify({
        "tasks": results,
        "page": page,
        "pages": tasks.pages
    })


# ---------------- CREATE TASK ----------------
@app.route("/tasks", methods=["POST"])
@jwt_required()
def create_task():
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data received"}), 400

    title = data.get("title")

    if not title:
        return jsonify({"error": "Title required"}), 400

    task = Task(
        title=title,
        description=data.get("description", ""),
        user_id=user_id
    )

    db.session.add(task)
    db.session.commit()

    return jsonify({"message": "Task created"}), 201


# ---------------- UPDATE TASK ----------------
@app.route("/tasks/<int:id>", methods=["PATCH"])
@jwt_required()
def update_task(id):
    user_id = get_jwt_identity()

    task = Task.query.filter_by(id=id, user_id=user_id).first()

    if not task:
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"error": "No data received"}), 400

    task.title = data.get("title", task.title)
    task.description = data.get("description", task.description)
    task.completed = data.get("completed", task.completed)

    db.session.commit()

    return jsonify({"message": "Task updated"}), 200


# ---------------- DELETE TASK ----------------
@app.route("/tasks/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_task(id):
    user_id = get_jwt_identity()

    task = Task.query.filter_by(id=id, user_id=user_id).first()

    if not task:
        return jsonify({"error": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()

    return jsonify({"message": "Task deleted"}), 200


if __name__ == "__main__":
    app.run(debug=True)