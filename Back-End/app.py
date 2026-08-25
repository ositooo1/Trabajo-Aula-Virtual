from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
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
db = SQLAlchemy(app)

class Rol(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(30), unique=True, nullable=False)
    


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    rol_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    rol = db.relationship("Rol")
    
class Curso(db.Model):
    __tablename__ = "cursos"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)




DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def load_data(name):
    path = os.path.join(DATA_DIR, f"{name}.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_data(name, data):
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, f"{name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@app.route("/")
def homepage():
    return render_template("homepage.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/courses")
def courses():
    return render_template("courses.html")


@app.route("/students")
def students():
    return render_template("students.html")


@app.route("/content")
def content():
    return render_template("content.html")


@app.route("/evaluations")
def evaluations():
    return render_template("evaluations.html")


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()

    usuario = Usuario.query.filter_by(email=data.get("email")).first()

    if usuario and check_password_hash(usuario.password_hash, data.get("password", "")):
        return jsonify(
            {
                "token": "tok_" + usuario.email,
                "user": {
                    "id": usuario.id,
                    "username": usuario.nombre,
                    "role": usuario.rol.nombre,
                },
            }
        )

    return jsonify({"message": "Email o contrasena incorrectos"}), 401


@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json()

    if Usuario.query.filter_by(email=data.get("email")).first():
        return jsonify({"message": "El email ya esta registrado"}), 400

    nombre_rol = data.get("role", "estudiante")
    rol = Rol.query.filter_by(nombre=nombre_rol).first()
    if rol is None:
        rol = Rol(nombre=nombre_rol)
        db.session.add(rol)
        db.session.commit()

    nuevo_usuario = Usuario(
        nombre=data.get("username", ""),
        apellido="",
        email=data.get("email", ""),
        password_hash=generate_password_hash(data.get("password", "")),  # ojo, esto lo mejoramos en el próximo paso
        rol_id=rol.id,
    )
    db.session.add(nuevo_usuario)
    db.session.commit()

    return jsonify({"message": "Registro exitoso"}), 201


@app.route("/api/courses", methods=["GET", "POST"])
def api_courses():
    if request.method == "GET":
        cursos = Curso.query.all()
        return jsonify({
            "courses": [
                {
                    "id": c.id,
                    "name": c.nombre,
                    "description": c.descripcion,
                    "status": "active" if c.activo else "inactive",
                }
                for c in cursos
            ]
        })

    data = request.get_json()
    nuevo_curso = Curso(
        nombre=data.get("name", ""),
        descripcion=data.get("description", ""),
        activo=True,
    )
    db.session.add(nuevo_curso)
    db.session.commit()

    return jsonify({
        "id": nuevo_curso.id,
        "name": nuevo_curso.nombre,
        "description": nuevo_curso.descripcion,
        "status": "active",
    }), 201


@app.route("/api/courses/<int:cid>", methods=["PUT", "DELETE"])
def api_course(cid):
    curso = Curso.query.get(cid)
    if curso is None:
        return jsonify({"message": "No encontrado"}), 404

    if request.method == "DELETE":
        db.session.delete(curso)
        db.session.commit()
        return jsonify({"message": "Eliminado"})

    data = request.get_json()
    if "name" in data:
        curso.nombre = data.get("name")
    if "description" in data:
        curso.descripcion = data.get("description")
    if "status" in data:
        curso.activo = data.get("status") == "active"

    db.session.commit()
    return jsonify({
        "id": curso.id,
        "name": curso.nombre,
        "description": curso.descripcion,
        "status": "active" if curso.activo else "inactive",
    })


@app.route("/api/students", methods=["GET", "POST"])
def api_students():
    if request.method == "GET":
        return jsonify({"students": load_data("students")})
    data = request.get_json()
    students = load_data("students")
    new_id = max([s["id"] for s in students], default=0) + 1
    data["id"] = new_id
    students.append(data)
    save_data("students", students)
    return jsonify(data), 201


@app.route("/api/students/<int:sid>", methods=["PUT", "DELETE"])
def api_student(sid):
    students = load_data("students")
    if request.method == "DELETE":
        students = [s for s in students if s["id"] != sid]
        save_data("students", students)
        return jsonify({"message": "Eliminado"})
    data = request.get_json()
    for s in students:
        if s["id"] == sid:
            s.update(data)
            save_data("students", students)
            return jsonify(s)
    return jsonify({"message": "No encontrado"}), 404


@app.route("/api/content", methods=["GET", "POST"])
def api_content():
    if request.method == "GET":
        return jsonify({"contents": load_data("content")})
    data = request.get_json()
    contents = load_data("content")
    new_id = max([c["id"] for c in contents], default=0) + 1
    data["id"] = new_id
    contents.append(data)
    save_data("content", contents)
    return jsonify(data), 201


@app.route("/api/content/<int:cid>", methods=["PUT", "DELETE"])
def api_content_item(cid):
    contents = load_data("content")
    if request.method == "DELETE":
        contents = [c for c in contents if c["id"] != cid]
        save_data("content", contents)
        return jsonify({"message": "Eliminado"})
    data = request.get_json()
    for c in contents:
        if c["id"] == cid:
            c.update(data)
            save_data("content", contents)
            return jsonify(c)
    return jsonify({"message": "No encontrado"}), 404


@app.route("/api/evaluations", methods=["GET", "POST"])
def api_evaluations():
    if request.method == "GET":
        return jsonify({"evaluations": load_data("evaluations")})
    data = request.get_json()
    evaluations = load_data("evaluations")
    new_id = max([e["id"] for e in evaluations], default=0) + 1
    data["id"] = new_id
    evaluations.append(data)
    save_data("evaluations", evaluations)
    return jsonify(data), 201


@app.route("/api/evaluations/<int:eid>", methods=["PUT", "DELETE"])
def api_evaluation(eid):
    evaluations = load_data("evaluations")
    if request.method == "DELETE":
        evaluations = [e for e in evaluations if e["id"] != eid]
        save_data("evaluations", evaluations)
        return jsonify({"message": "Eliminado"})
    data = request.get_json()
    for e in evaluations:
        if e["id"] == eid:
            e.update(data)
            save_data("evaluations", evaluations)
            return jsonify(e)
    return jsonify({"message": "No encontrado"}), 404


if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    for name in ["users", "courses", "students", "content", "evaluations"]:
        if not os.path.exists(os.path.join(DATA_DIR, f"{name}.json")):
            save_data(name, [])
    with app.app_context():
        usuarios = Usuario.query.all()      
        print(f"Encontré {len(usuarios)} usuarios en la base")
    app.run(debug=True)                           
    
