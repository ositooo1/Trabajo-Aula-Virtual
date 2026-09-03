from extension import db #Curso, ciclo lectivo, docentesCurso y inscripcion.


class CicloLectivo(db.Model):
    __tablename__ = "ciclos_lectivos"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nombre = db.Column(
        db.String(50),
        nullable=False
    )

    fecha_inicio = db.Column(
        db.Date
    )

    fecha_fin = db.Column(
        db.Date
    )


class Curso(db.Model):
    __tablename__ = "cursos"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nombre = db.Column(
        db.String(150),
        nullable=False
    )

    descripcion = db.Column(
        db.Text
    )

    codigo = db.Column(
        db.String(20),
        unique=True,
        nullable=True
    )

    ciclo_lectivo_id = db.Column(
        db.Integer,
        db.ForeignKey("ciclos_lectivos.id"),
        nullable=True
    )

    creado_por = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=True
    )

    activo = db.Column(
        db.Boolean,
        default=True
    )

    creado_en = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )


class DocenteCurso(db.Model):
    __tablename__ = "docentes_cursos"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    curso_id = db.Column(
        db.Integer,
        db.ForeignKey("cursos.id"),
        nullable=False
    )

    docente_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    asignado_en = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )


class Inscripcion(db.Model):
    __tablename__ = "inscripciones"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    curso_id = db.Column(
        db.Integer,
        db.ForeignKey("cursos.id"),
        nullable=False
    )

    estudiante_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    inscrito_en = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )