from flask import (
    Blueprint,
    render_template,
    request,
    jsonify
)

from extension import db

from models import (
    Curso,
    DocenteCurso,
    Inscripcion
)

from utils.auth import (
    requiere_login
)

from utils.course_codes import (
    generar_codigo_curso
)

from utils.course_helpers import (
    curso_a_dict,
    obtener_cursos_usuario
)


courses_bp = Blueprint(
    "courses",
    __name__
)

# PÁGINAS

@courses_bp.route("/courses")
def courses_page():

    return render_template(
        "homepage.html"
    )


@courses_bp.route(
    "/courses/<int:cid>"
)
def course_detail_page(cid):

    return render_template(
        "courses.html",
        course_id=cid
    )

# LISTAR / CREAR

@courses_bp.route(
    "/api/courses",
    methods=[
        "GET",
        "POST"
    ]
)
@requiere_login
def api_courses():

    usuario = (
        request.usuario_actual
    )


    if request.method == "GET":

        return jsonify({

            "courses":
                obtener_cursos_usuario(
                    usuario.id
                )

        }), 200


    data = request.get_json(
        silent=True
    ) or {}


    nombre = (
        data.get(
            "name",
            ""
        ).strip()
    )


    descripcion = (
        data.get(
            "description",
            ""
        ).strip()
    )


    if not nombre:

        return jsonify({
            "message":
                "El nombre del curso es obligatorio"
        }), 400


    if len(nombre) > 150:

        return jsonify({
            "message":
                "El nombre del curso es demasiado largo"
        }), 400


    nuevo_curso = Curso(

        nombre=nombre,

        descripcion=descripcion,

        codigo=
            generar_codigo_curso(),

        creado_por=
            usuario.id,

        activo=True

    )


    try:

        db.session.add(
            nuevo_curso
        )


        db.session.flush()


        relacion_docente = (
            DocenteCurso(

                curso_id=
                    nuevo_curso.id,

                docente_id=
                    usuario.id

            )
        )


        db.session.add(
            relacion_docente
        )


        db.session.commit()


    except Exception as error:

        db.session.rollback()


        print(
            "Error al crear curso:",
            error
        )


        return jsonify({
            "message":
                "No se pudo crear el curso"
        }), 500


    return jsonify(
        curso_a_dict(
            nuevo_curso,
            "docente"
        )
    ), 201



# MIS CURSOS

@courses_bp.route(
    "/api/courses/mine",
    methods=["GET"]
)
@requiere_login
def api_courses_mine():

    usuario = (
        request.usuario_actual
    )


    return jsonify({

        "courses":
            obtener_cursos_usuario(
                usuario.id
            )

    }), 200

# UNIRSE POR CÓDIGO
@courses_bp.route(
    "/api/courses/join",
    methods=["POST"]
)
@requiere_login
def api_join_course():

    usuario = (
        request.usuario_actual
    )


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


    if not codigo:

        return jsonify({
            "message":
                "Ingresá el código del curso"
        }), 400


    curso = (
        Curso.query
        .filter_by(
            codigo=codigo
        )
        .first()
    )


    if curso is None:

        return jsonify({
            "message":
                "No existe un curso con ese código"
        }), 404


    if not curso.activo:

        return jsonify({
            "message":
                "Este curso ya no está activo"
        }), 400


    es_docente = (
        DocenteCurso.query
        .filter_by(
            curso_id=
                curso.id,

            docente_id=
                usuario.id
        )
        .first()
    )


    if es_docente:

        return jsonify({
            "message":
                "Ya sos docente de este curso"
        }), 409


    inscripcion_existente = (
        Inscripcion.query
        .filter_by(
            curso_id=
                curso.id,

            estudiante_id=
                usuario.id
        )
        .first()
    )


    if inscripcion_existente:

        return jsonify({
            "message":
                "Ya estás inscripto en este curso"
        }), 409


    nueva_inscripcion = (
        Inscripcion(

            curso_id=
                curso.id,

            estudiante_id=
                usuario.id

        )
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


    return jsonify({

        "message":
            "Te uniste al curso correctamente",

        "course":
            curso_a_dict(
                curso,
                "estudiante"
            )

    }), 201


# CURSO INDIVIDUAL

@courses_bp.route(
    "/api/courses/<int:cid>",
    methods=[
        "GET",
        "PUT",
        "DELETE"
    ]
)
@requiere_login
def api_course(cid):

    usuario = (
        request.usuario_actual
    )


    curso = db.session.get(
        Curso,
        cid
    )


    if curso is None:

        return jsonify({
            "message":
                "Curso no encontrado"
        }), 404


    relacion_docente = (
        DocenteCurso.query
        .filter_by(
            curso_id=cid,
            docente_id=
                usuario.id
        )
        .first()
    )


    inscripcion = (
        Inscripcion.query
        .filter_by(
            curso_id=cid,
            estudiante_id=
                usuario.id
        )
        .first()
    )


    if relacion_docente:

        rol = "docente"

    elif inscripcion:

        rol = "estudiante"

    else:

        return jsonify({
            "message":
                "No pertenecés a este curso"
        }), 403

    # GETs
    if request.method == "GET":

        data = curso_a_dict(
            curso,
            rol
        )


        if rol == "docente":

            data[
                "student_count"
            ] = (
                Inscripcion.query
                .filter_by(
                    curso_id=cid
                )
                .count()
            )


        return jsonify({
            "course": data
        }), 200
    # SOLO DOCENTE

    if rol != "docente":

        return jsonify({
            "message":
                "No tenés permisos para modificar este curso"
        }), 403

    # DELETEs

    if request.method == "DELETE":

        curso.activo = False

        db.session.commit()


        return jsonify({
            "message":
                "Curso archivado correctamente"
        }), 200


    # =========================
    # PUT
    # =========================

    data = request.get_json(
        silent=True
    ) or {}


    if "name" in data:

        nombre = (
            data.get(
                "name",
                ""
            ).strip()
        )


        if not nombre:

            return jsonify({
                "message":
                    "El nombre del curso es obligatorio"
            }), 400


        if len(nombre) > 150:

            return jsonify({
                "message":
                    "El nombre del curso es demasiado largo"
            }), 400


        curso.nombre = nombre


    if "description" in data:

        curso.descripcion = (
            data.get(
                "description",
                ""
            ).strip()
        )


    db.session.commit()


    return jsonify(
        curso_a_dict(
            curso,
            "docente"
        )
    ), 200