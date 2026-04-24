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


# ---------------- SIGN UP ----------------
@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data sent"}), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    existing_user = User.query.filter_by(username=username).first()

    if existing_user:
        return jsonify({"error": "Username already exists"}), 400

    new_user = User(username=username)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "Signup successful",
        "id": new_user.id,
        "username": new_user.username
    }), 201


# ---------------- LOG IN ----------------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data sent"}), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"error": "User not found"}), 401

    if not user.check_password(password):
        return jsonify({"error": "Wrong password"}), 401

    access_token = create_access_token(identity=user.id)

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": {
            "id": user.id,
            "username": user.username
        }
    }), 200


# ---------------- LOG OUT ----------------
@app.route("/logout", methods=["DELETE", "POST"])
def logout():
    return jsonify({
        "message": "Logout successful"
    }), 200


# ---------------- TEST AUTH BUTTON ----------------
@app.route("/authorized", methods=["GET"])
@jwt_required()
def authorized():
    current_user_id = get_jwt_identity()

    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "message": f"You are logged in as {user.username}"
    }), 200


# ---------------- GET TASKS ----------------
@app.route("/tasks", methods=["GET"])
@jwt_required()
def get_tasks():
    current_user_id = get_jwt_identity()

    tasks = Task.query.filter_by(user_id=current_user_id).all()

    tasks_list = []

    for task in tasks:
        tasks_list.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed
        })

    return jsonify(tasks_list), 200


# ---------------- CREATE TASK ----------------
@app.route("/tasks", methods=["POST"])
@jwt_required()
def create_task():
    current_user_id = get_jwt_identity()
    data = request.get_json()

    title = data.get("title")
    description = data.get("description", "")

    if not title:
        return jsonify({"error": "Title required"}), 400

    task = Task(
        title=title,
        description=description,
        user_id=current_user_id
    )

    db.session.add(task)
    db.session.commit()

    return jsonify({"message": "Task created"}), 201


# ---------------- UPDATE TASK ----------------
@app.route("/tasks/<int:id>", methods=["PATCH"])
@jwt_required()
def update_task(id):
    current_user_id = get_jwt_identity()

    task = Task.query.filter_by(id=id, user_id=current_user_id).first()

    if not task:
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json()

    task.title = data.get("title", task.title)
    task.description = data.get("description", task.description)
    task.completed = data.get("completed", task.completed)

    db.session.commit()

    return jsonify({"message": "Task updated"}), 200


# ---------------- DELETE TASK ----------------
@app.route("/tasks/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_task(id):
    current_user_id = get_jwt_identity()

    task = Task.query.filter_by(id=id, user_id=current_user_id).first()

    if not task:
        return jsonify({"error": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()

    return jsonify({"message": "Task deleted"}), 200


if __name__ == "__main__":
    app.run(port=5555, debug=True)