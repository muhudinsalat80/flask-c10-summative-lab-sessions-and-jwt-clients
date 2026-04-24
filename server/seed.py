from app import app
from config import db
from models import User, Task

with app.app_context():
    db.drop_all()
    db.create_all()

    user = User(username="admin")
    user.set_password("1234")

    db.session.add(user)
    db.session.commit()

    task = Task(
        title="Finish lab",
        description="Submit project",
        user_id=user.id
    )

    db.session.add(task)
    db.session.commit()

    print("Seeded!")