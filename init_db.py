from flask import Flask
from werkzeug.security import generate_password_hash

from config import Config
from models import db, Admin


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)


with app.app_context():

    print("Creating database tables...")

    db.create_all()

    admin = Admin.query.filter_by(username="admin").first()

    if not admin:
        admin = Admin(
            username="admin",
            password=generate_password_hash("admin123")
        )

        db.session.add(admin)
        db.session.commit()

        print("Admin created.")

    print("Database initialized successfully.")