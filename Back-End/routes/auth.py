from flask import (
    Blueprint,
    render_template,
    request,
    jsonify
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from extension import db

from models import Usuario


auth_bp = Blueprint(
    "auth",
    __name__
)
# PÁGINAS

@auth_bp.route("/login")
def login_page():

    return render_template(
        "login.html"
    )


@auth_bp.route("/register")
def register_page():

    return render_template(
        "register.html"
    )

# LOGIN

@auth_bp.route(
    "/api/login",
    methods=["POST"]
)
def api_login():

    data = request.get_json(
        silent=True
    ) or {}


    email = (
        data.get(
            "email",
            ""
        )
        .strip()
        .lower()
    )


    password = data.get(
        "password",
        ""
    )


    if not email or not password:

        return jsonify({
            "message":
                "Email y contraseña son obligatorios"
        }), 400


    usuario = (
        Usuario.query
        .filter_by(
            email=email,
            activo=True
        )
        .first()
    )


    if (
        usuario is None
        or not check_password_hash(
            usuario.password_hash,
            password
        )
    ):

        return jsonify({
            "message":
                "Email o contraseña incorrectos"
        }), 401


    return jsonify({

        "token":
            "tok_" + usuario.email,

        "user": {

            "id":
                usuario.id,

            "username":
                usuario.nombre,

            "lastname":
                usuario.apellido,

            "email":
                usuario.email
        }

    }), 200

# REGISTRO

@auth_bp.route(
    "/api/register",
    methods=["POST"]
)
def api_register():

    data = request.get_json(
        silent=True
    ) or {}


    nombre = (
        data.get(
            "username",
            ""
        ).strip()
    )


    apellido = (
        data.get(
            "lastname",
            ""
        ).strip()
    )


    email = (
        data.get(
            "email",
            ""
        )
        .strip()
        .lower()
    )


    password = data.get(
        "password",
        ""
    )


    if (
        not nombre
        or not apellido
        or not email
    ):

        return jsonify({
            "message":
                "Nombre, apellido y email son obligatorios"
        }), 400


    if len(password) < 6:

        return jsonify({
            "message":
                "La contraseña debe tener al menos 6 caracteres"
        }), 400


    if len(nombre) > 100:

        return jsonify({
            "message":
                "El nombre es demasiado largo"
        }), 400


    if len(apellido) > 100:

        return jsonify({
            "message":
                "El apellido es demasiado largo"
        }), 400


    if len(email) > 150:

        return jsonify({
            "message":
                "El email es demasiado largo"
        }), 400


    existente = (
        Usuario.query
        .filter_by(
            email=email
        )
        .first()
    )


    if existente:

        return jsonify({
            "message":
                "El email ya está registrado"
        }), 409


    nuevo_usuario = Usuario(

        nombre=nombre,

        apellido=apellido,

        email=email,

        password_hash=
            generate_password_hash(
                password
            ),

        rol_id=None,

        activo=True
    )


    try:

        db.session.add(
            nuevo_usuario
        )

        db.session.commit()


    except Exception as error:

        db.session.rollback()

        print(
            "Error al registrar usuario:",
            error
        )


        return jsonify({
            "message":
                "No se pudo crear la cuenta"
        }), 500


    return jsonify({

        "message":
            "Registro exitoso",

        "user": {

            "id":
                nuevo_usuario.id,

            "name":
                nuevo_usuario.nombre,

            "lastname":
                nuevo_usuario.apellido,

            "email":
                nuevo_usuario.email

        }

    }), 201