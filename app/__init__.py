from flask import Flask
from app.extensions import db, migrate

def create_app():
    app = Flask(__name__)

    # Load config
    app.config.from_object('app.config.Config')

    db.init_app(app)
    migrate.init_app(app, db)

    # register blueprints
    from app.routes.user_routes import user_bp
    app.register_blueprint(user_bp, url_prefix='/api/users')

    return app
