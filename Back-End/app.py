from extension import db
from routes import main_bp, auth_bp, courses_bp
from flask import Flask, app
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONT_END_DIR = os.path.join(BASE_DIR, "..", "Front-End")

def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(FRONT_END_DIR, "templates"),
        static_folder=os.path.join(FRONT_END_DIR, "static"),
    )
    app.secret_key = "aula-virtual-secret"

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "mysql+pymysql://root:@127.0.0.1:3306/aula_virtual")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(courses_bp)
    
    return app


app = create_app()

if __name__ == "__main__":
    
    app.run(debug=True)
