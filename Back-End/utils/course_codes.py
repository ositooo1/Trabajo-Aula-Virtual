import secrets
from models import Curso

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