import os

from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column

""" database models """

db = SQLAlchemy()


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]


class Device(db.Model):
    __bind_key__ = "device_db"
    id: Mapped[int] = mapped_column(primary_key=True)
    memory: Mapped[int]


""" API blueprints """

user_api = Blueprint("user_api", __name__)


@user_api.get("/username/<user_id>")
def get_name(user_id):
    user = db.session.get(User, user_id)
    if user:
        return {"name": user.name}
    return None


device_api = Blueprint("device_api", __name__)


@device_api.get("/memory/<device_id>")
def get_memory(device_id):
    device = db.session.get(Device, device_id)
    if device:
        return {"memory": device.memory}
    return None


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
    app.config["SQLALCHEMY_BINDS"] = {
        "device_db": os.getenv("DEVICE_DB_URI"),
    }

    db.init_app(app)
    app.register_blueprint(user_api, url_prefix="/")
    app.register_blueprint(device_api, url_prefix="/device")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8888)
