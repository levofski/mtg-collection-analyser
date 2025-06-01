"""
Database configuration module.
"""
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

# Create a SQLAlchemy instance
db = SQLAlchemy()


def init_app(app: Flask) -> None:
    """
    Initialize the database with the Flask application.

    Args:
        app: The Flask application instance.
    """
    # Configure SQLite database
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mtg_collection.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize the database with the app
    db.init_app(app)

    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
