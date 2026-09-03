from extension import db
from flask import Flask, render_template, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import secrets #Generador de cifrados alfanuméricos únicos aleatorios en vez de random.
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


class Rol(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(30), unique=True, nullable=False)
    


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    
    # El rol no define si es docente o estudiante...
    # Docentes_cursos e Inscripciones definen si un usuario es docente o estudiante en un curso específico.
    rol_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=True) # Self dc.
    # Un mismo usuario ahora puede ser estudiante y profesor dependiendo del modo en el cual se introdujo al curso.
    
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    rol = db.relationship("Rol")
    
class CicloLectivo(db.Model):
    __tablename__ = "ciclos_lectivos"

    id = db.Column(db.Integer, primary_key=True)

    nombre = db.Column(db.String(50),nullable=False )

    fecha_inicio = db.Column(db.Date)

    fecha_fin = db.Column(db.Date )
    
class Curso(db.Model):
    __tablename__ = "cursos"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text)
    codigo = db.Column(db.String(20), unique = True, nullable = True)
    ciclo_lectivo_id = db.Column(db.Integer, db.ForeignKey("ciclos_lectivos.id"), nullable=True)
    creado_por = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    activo = db.Column(db.Boolean, default=True)
    creado_en = db.Column(db.DateTime, server_default=db.func.now())

class DocenteCurso(db.Model):
    __tablename__ = "docentes_cursos"

    id = db.Column(db.Integer, primary_key=True)
    curso_id = db.Column(db.Integer, db.ForeignKey("cursos.id"), nullable=False)
    docente_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    asignado_en = db.Column(db.DateTime, server_default=db.func.now())  

class Inscripcion(db.Model):
    __tablename__ = "inscripciones"

    id = db.Column(db.Integer, primary_key=True)
    curso_id = db.Column(db.Integer, db.ForeignKey("cursos.id"), nullable=False)
    estudiante_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    inscrito_en = db.Column(db.DateTime, server_default=db.func.now())

# X usuario es docente del curso Y para DocenteCurso, X usuario es estudiante del curso Y para Inscripcion.

def requiere_login(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"message": "No autorizado"}), 401

        token = auth_header.replace("Bearer ", "")
        if not token.startswith("tok_"):
            return jsonify({"message": "No autorizado"}), 401

        email = token.replace("tok_", "", 1)
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario is None:
            return jsonify({"message": "No autorizado"}), 401

        request.usuario_actual = usuario
        return f(*args, **kwargs)
    return wrapper


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def generar_codigo_curso():
    caracteres = (
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789"
    ) #Fuente de digit.
    while True:
        codigo = "".join(
            secrets.choice(caracteres)
            for _ in range(6)
        ) #Genera 6 x aleatorios: voilá K847SM
        existente = Curso.query.filter_by(
            codigo=codigo
        ).first()

        if existente is None:
            return codigo
        
    #Si ya existe, lo vuelve a hacer hasta que hace uno que no exista. :d


def curso_a_dict(curso, rol):
    #Método para no repetir código al obtener cursos de un usuario, ya sea como docente o estudiante.
    data = {
        "id": curso.id,
        "name": curso.nombre,
        "description": curso.descripcion or "",
        "role": rol,
        "status": "active" if curso.activo else "inactive",
    }
    
    #Código solo se muestra al docente.
    if rol == "docente":
        data["code"] = curso.codigo
    return data


def obtener_cursos_usuario(usuario_id):
    cursos = {}

    #Docente.
    cursos_docente = (
        db.session.query(Curso)
        .join(DocenteCurso, DocenteCurso.curso_id == Curso.id)
        .filter(DocenteCurso.docente_id == usuario_id, 
                Curso.activo.is_(True)).all()
    )
    
    for curso in cursos_docente:
        cursos[curso.id] = curso_a_dict(curso, "docente")

    #Alumno.
    cursos_estudiante = (
        db.session.query(Curso)
        .join(Inscripcion, Inscripcion.curso_id == Curso.id)
        .filter(Inscripcion.estudiante_id == usuario_id, 
                Curso.activo.is_(True)).all()
    )

    for curso in cursos_estudiante:
    # Combinación de cursos en caso de que un usuario sea docente y estudiante en el mismo cursos, 
    # priorize docente para no duplicarlo.
        if curso.id not in cursos:
            
            cursos[curso.id] = curso_a_dict(curso, "estudiante")
    
    return list(cursos.values())

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
def courses_page():

    return render_template(
        "homepage.html"
    )


@app.route("/courses/<int:cid>")
def course_detail_page(cid):

    return render_template(
        "courses.html",
        course_id=cid
    )


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
    data = request.get_json(silent = True) or {} #JSON no, si en diccionario vacío.

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    
    if not email or not password:
        return jsonify({"message": "Email y contraseña son campos obligatorios."}), 400
    
    # Se busca usuario de bd.
    usuario = Usuario.query.filter_by(email=email).first()
    
    # Verifica passwold.
    if (usuario is None or not usuario.activo or not check_password_hash(usuario.password_hash, password)):
        return jsonify({"message": "Email o contraseña incorrectos."}), 401

    return jsonify({
            "token": "tok_" + usuario.email, # Este es una verga, pero no tengo ni idea como hacer uno no tan predecible y el chat no ayuda. ;-;
            "user": {
                "id": usuario.id,
                "username": usuario.nombre,
                "lastname": usuario.apellido,
                "email": usuario.email
            }}), 200
""" Te lo dejo como para que te quede para vos, es lo mismo pero valido desde 0, btw es para eliminar lo de rol. :)
    usuario = Usuario.query.filter_by(email=data.get("email")).first()

    if usuario and check_password_hash(usuario.password_hash, data.get("password", "")):
        return jsonify(
            {
                "token": "tok_" + usuario.email,
                "user": {
                    "id": usuario.id,
                    "username": usuario.nombre,
                    "lastname": usuario.apellido,
                    "email": usuario.email,
                    "role": usuario.rol.nombre,
                },
            }
        )

    return jsonify({"message": "Email o contrasena incorrectos"}), 401

También porque devuelve el rol, pero no es necesario, ya que el usuario puede ser estudiante y docente a la vez, dependiendo del curso. Por eso lo eliminé. :v
Solo agrege el id de enumeración, nombre, apellido y email. 
"""

@app.route("/api/register", methods=["POST"])
def api_register(): # Redefino estructura eliminando ppios.
    data = request.get_json() or {} # Si JSON no es validado, se guarda en un diccionario vacío.

    # Lectura de campos. btw strip es una función que elimina los espacios innecesarios.
    nombre = data.get("username", "").strip()
    apellido = data.get("lastname", "").strip()
    email = data.get("email", "").strip().lower() #solo minúsculas.
    password = data.get("password", "")

    # Validación de campos.
    if not nombre: 
        return jsonify({"message": "El nombre es obligatorio."}), 400

    if not apellido:
        return jsonify({"message": "El apellido es obligatorio."}), 400

    if not email:
        return jsonify({"message": "El email es obligatorio."}), 400

    if not password:
        return jsonify({"message": "La contraseña es obligatoria."}), 400

    if len(password) < 6:
        return jsonify({"message": "La contraseña debe tener al menos 6 caracteres."}), 400

    #Limite de caracteres en base a bd.
    
    if len(nombre) > 100:
        return jsonify({"message": "El nombre no puede superar los 100 caracteres."}), 400

    if len(apellido) > 100:
        return jsonify({"message": "El apellido no puede superar los 100 caracteres."}), 400

    if len(email) > 150:
        return jsonify({"message": "El email no puede superar los 150 caracteres."}), 400

    # Email momento.
    
    usuario_existente = Usuario.query.filter_by(email=email).first()
    
    if usuario_existente:
        return jsonify({"message": "El email ya está registrado, intentelo de nuevo o trate con otro correo disponible."}), 400


    # New pipol, (usuario).
    
    nuevo_usuario = Usuario(
        nombre=nombre,
        apellido=apellido,
        email=email,
        password_hash=generate_password_hash(password),
        rol_id = None,
        activo = True
    )
    
    #Commit a db.
    try:
        db.session.add(nuevo_usuario)
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        print(f"Error al registrar usuario: {error}")
        return jsonify({"message": "Error al registrar usuario, intentelo de nuevo."}), 500
    
    return jsonify({"message": "Registro exitoso", 
                    "user": 
                            {"id": nuevo_usuario.id, 
                            "name": nuevo_usuario.nombre,
                            "lastname": nuevo_usuario.apellido, 
                            "email": nuevo_usuario.email}}), 201
        
    # Esa es la respuesta l crear nuevos usuarios.
    # En resumen: 
    # El endpoint de registro valida los datos, 
    # verifica si el email ya está registrado, 
    # y si todo es correcto, crea un nuevo usuario en la base de datos
    # y devuelve un mensaje de éxito junto con los detalles del usuario creado.
"""
    if Usuario.query.filter_by(email=data.get("email")).first():
        return jsonify({"message": "El email ya esta registrado"}), 400

    nombre_rol = data.get("role", "estudiante")
    rol = Rol.query.filter_by(nombre=nombre_rol).first()
    if rol is None:
        rol = Rol(nombre=nombre_rol)
        db.session.add(rol)
        db.session.commit()

    nuevo_usuario = Usuario(
        nombre=nombre, .... 
        apellido=apellido, ASNDASOKFAMADAF
        email=data.get("email", ""), 
        password_hash=generate_password_hash(data.get("password", "")),  # ojo, esto lo mejoramos en el próximo paso
        rol_id=rol.id,
    )
    db.session.add(nuevo_usuario)
    db.session.commit()

    return jsonify({"message": "Registro exitoso"}), 201
"""

@app.route("/api/courses", methods=["GET", "POST"])
@requiere_login
def api_courses():
    
    usuario = request.usuario_actual
    
    #Lista de cursos de x usuario.
    
    if request.method == "GET":
        return jsonify({"courses": obtener_cursos_usuario(usuario.id)})

    #  Creación cursos.
    
    data = request.get_json(silent = True) or {}
    nombre = data.get("name", "").strip()
    descripcion = data.get("description", "").strip()
    
    #Vld.
    if not nombre:
        return jsonify({"message": "El nombre del curso es obligatorio."}), 400
    
    if len(nombre) > 150:
        return jsonify({"message": "El nombre del curso no puede superar los 150 caracteres."}), 400
    
    nuevo_curso = Curso( 
                        nombre=nombre, 
                        descripcion=descripcion,
                        codigo = generar_codigo_curso(),
                        creado_por=usuario.id, 
                        activo=True)
    
    try:
        #Nuevo curso a db.
        db.session.add(nuevo_curso)
        db.session.flush() # El flush es para extraer un id antes de hacer commit, para poder usarlo en la relación docente_curso.
        #Toma el id del nuevo curso y lo asigna al docente que lo creó, para que quede registrado como docente del curso.
        relacion_docente = DocenteCurso(curso_id=nuevo_curso.id, docente_id=usuario.id)
        db.session.add(relacion_docente)
        
        db.session.commit()
    
    except Exception as error:
        db.session.rollback()
        print(f"Error al crear el curso: {error}")
        return jsonify({"message": "Error al crear el curso"}), 500
    
    return jsonify(curso_a_dict(nuevo_curso, "docente")), 201



@app.route("/api/courses/mine", methods=["GET"])
@requiere_login
def api_courses_mine():
    usuario = request.usuario_actual
    cursos = obtener_cursos_usuario(usuario.id)
    return jsonify({"courses": cursos}), 200

#Esta es la Api en sí, que devuelve los cursos de un usuario, 
# ya sea como docente o estudiante, 
# dependiendo de su rol en cada curso.

@app.route(
    "/api/courses/join",
    methods=["POST"]
)
@requiere_login
def api_join_course():

    usuario = request.usuario_actual

    # LEER DATOS

    data = request.get_json(
        silent=True
    ) or {}


    codigo = (
        data.get(
            "code",
            ""
        )
        .strip()
        .upper()
    )

    # Valida código.

    if not codigo:

        return jsonify({
            "message":
                "Ingresá el código del curso"
        }), 400

    # Buscar curso.

    curso = Curso.query.filter_by(
        codigo=codigo
    ).first()


    if curso is None:

        return jsonify({
            "message":
                "No existe un curso con ese código"
        }), 404

    # verificar estado.
    if not curso.activo:

        return jsonify({
            "message":
                "Este curso ya no está activo"
        }), 400
    # ¿ES DOCENTE?

    es_docente = (
        DocenteCurso.query
        .filter_by(
            curso_id=curso.id,
            docente_id=usuario.id
        )
        .first()
    )


    if es_docente:

        return jsonify({
            "message":
                "Ya sos docente de este curso"
        }), 409

    # ¿YA ESTÁ INSCRIPTO?
    inscripcion_existente = (
        Inscripcion.query
        .filter_by(
            curso_id=curso.id,
            estudiante_id=usuario.id
        )
        .first()
    )


    if inscripcion_existente:

        return jsonify({
            "message":
                "Ya estás inscripto en este curso"
        }), 409

    # Nueva inscripción.

    nueva_inscripcion = Inscripcion(

        curso_id=curso.id,

        estudiante_id=usuario.id

    )


    try:

        db.session.add(
            nueva_inscripcion
        )

        db.session.commit()


    except Exception as error:

        db.session.rollback()


        print(
            "Error al inscribir usuario:",
            error
        )


        return jsonify({
            "message":
                "No se pudo realizar la inscripción"
        }), 500

    # Answer.

    return jsonify({

        "message":
            "Te uniste al curso correctamente",

        "course":
            curso_a_dict(
                curso,
                "estudiante"
            )

    }), 201

#Transforma a mayúscula el código y lo verifica en base de lo que haya recibido.
# Si uno no esta activo, no te deja entrar :c y que el docente no pueda unirse a su propio curso.
# Solo una inscripción.

@app.route("/api/courses/<int:cid>", methods=["GET", "PUT", "DELETE"])
@requiere_login
def api_course(cid):
    
    usuario = request.usuario_actual
    
    curso = db.session.get(Curso, cid) #Busca curso.
    
    if curso is None:
        return jsonify({"message": "Curso no encontrado"}), 404
    
    # Validación relación de usuarios.
    
    relacion_docente = (DocenteCurso.query.filter_by(curso_id=cid, docente_id=usuario.id).first())
    inscripcion = (Inscripcion.query.filter_by(curso_id=cid, estudiante_id=usuario.id).first())
    
    #Rol dentro de curso.
    
    if relacion_docente:
        rol = "docente"
    elif inscripcion:
        rol = "estudiante"
    else:
        return jsonify({"message": "No debes de estar en este curso."}), 403
    
    #Coonsultar curso.
    
    if request.method == "GET":
        
        data = curso_a_dict(curso, rol)
        
        # La cantidad de estudiantes
        # solamente la necesita el docente.

        if rol == "docente":

            data["student_count"] = (
                Inscripcion.query
                .filter_by(
                    curso_id=cid
                )
                .count()
            )


        return jsonify({
            "course": data
        }), 200

    # Put DELETE para docentes.
    if rol != "docente":
        return jsonify({"message": "No tienes autorización para modificar el curso."}), 403
    
    # archivar, esto es para que no eliminen el cuerpo, siendo inactivo para no poder romper
    # las relaciones con los estudiantes, contenido y evaluaciones del curso.
    
    if request.method == "DELETE":
        curso.activo = False
        db.session.commit()
        return jsonify({"message": "Curso archivado"}), 200
    
    # Permiso de edición.
    data=request.get_json(silent = True) or {}
    
    if "name" in data:
        nombre = data.get("name", "").strip()
        
        if not nombre:
            return jsonify({"message": "El nombre del curso es obligatorio."}), 400
        
        if len(nombre) > 150:
            return jsonify({"message": "El nombre del curso no puede superar los 150 caracteres."}), 400
        
        curso.nombre = nombre
    
    if "description" in data:
        curso.descripcion = data.get("description", "").strip()
    
    db.session.commit()
    return jsonify(curso_a_dict(curso, "docente")), 200
    
    
    """ 
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
    if "code" in data:
        curso.codigo = data.get("code")
    if "teacher" in data:
        curso.profesor = data.get("teacher")
    if "status" in data:
        curso.activo = data.get("status") == "active"

    db.session.commit()
    return jsonify({
        "id": curso.id,
        "name": curso.nombre,
        "description": curso.descripcion,
        "code": curso.codigo,
        "teacher": curso.profesor,
        "status": "active" if curso.activo else "inactive",
    })
"""

@app.route("/api/students", methods=["GET", "POST"])
@requiere_login
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
@requiere_login
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
@requiere_login
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
@requiere_login
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
@requiere_login
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
@requiere_login
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
    
