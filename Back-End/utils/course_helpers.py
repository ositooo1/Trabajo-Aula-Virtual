from extension import db

from models import (
    Curso,
    DocenteCurso,
    Inscripcion
)


def curso_a_dict(
    curso,
    rol
):

    data = {
        "id":
            curso.id,

        "name":
            curso.nombre,

        "description":
            curso.descripcion or "",

        "role":
            rol,

        "status":
            (
                "active"
                if curso.activo
                else "inactive"
            )
    }


    if rol == "docente":

        data["code"] = (
            curso.codigo
        )


    return data



def obtener_cursos_usuario(
    usuario_id
):

    cursos = {}

    # COMO DOCENTE

    cursos_docente = (
        db.session
        .query(Curso)
        .join(
            DocenteCurso,
            DocenteCurso.curso_id
            == Curso.id
        )
        .filter(
            DocenteCurso.docente_id
            == usuario_id,

            Curso.activo.is_(True)
        )
        .all()
    )


    for curso in cursos_docente:

        cursos[curso.id] = (
            curso_a_dict(
                curso,
                "docente"
            )
        )

    # ESTUDIANTE

    cursos_estudiante = (
        db.session
        .query(Curso)
        .join(
            Inscripcion,
            Inscripcion.curso_id
            == Curso.id
        )
        .filter(
            Inscripcion.estudiante_id
            == usuario_id,

            Curso.activo.is_(True)
        )
        .all()
    )


    for curso in cursos_estudiante:

        if curso.id not in cursos:

            cursos[curso.id] = (
                curso_a_dict(
                    curso,
                    "estudiante"
                )
            )


    return list(
        cursos.values()
    )