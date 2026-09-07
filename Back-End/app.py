from extension import db
from models import ( Rol, Usuario, CicloLectivo, Curso, DocenteCurso, Inscripcion )
from routes import main_bp, auth_bp, courses_bp
from flask import Flask, render_template, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONT_END_DIR = os.path.join(BASE_DIR, "..", "Front-End")

app = Flask(
    __name__,
    template_folder=os.path.join(FRONT_END_DIR, "templates"),
    static_folder=os.path.join(FRONT_END_DIR, "static"),
)
app.secret_key = "aula-virtual-secret"


app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql+pymysql://root:@127.0.0.1:3306/aula_virtual"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
