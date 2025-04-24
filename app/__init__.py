from flask import Flask
import os

def create_app(test_config=None):
    """Create and configure the Flask application"""
    app = Flask(__name__, instance_relative_config=True)
    
    # Set up configuration
    app.config.from_mapping(
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev'),
        MONGO_URI=os.getenv('MONGO_URI', 'mongodb://localhost:27017/'),
        DB_NAME=os.getenv('DB_NAME', 'PBSC-Ignite-db'),
    )
    
    if test_config:
        app.config.from_mapping(test_config)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.roadmap import roadmap_bp
    from app.routes.career_coach import career_coach_bp
    from app.routes.tutor import tutor_bp  # Import the new tutor blueprint
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(roadmap_bp)
    app.register_blueprint(career_coach_bp)
    app.register_blueprint(tutor_bp)  # Register the new tutor blueprint
    
    return app