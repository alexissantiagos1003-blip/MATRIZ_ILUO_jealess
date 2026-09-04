from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///matriz_iluo.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# =========================
# CONFIGURACIÓN DE ARCHIVOS
# =========================

UPLOAD_FOLDER = os.path.join(
    app.root_path,
    "uploads",
    "cursos"
)

ALLOWED_EXTENSIONS = {"pdf"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

def archivo_permitido(nombre):

    return (
        "." in nombre
        and nombre.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )



# =========================
# TABLA: PUESTOS
# =========================

class Puesto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)


# =========================
# TABLA: COLABORADORES
# =========================

class Colaborador(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero_empleado = db.Column(db.String(50), nullable=False, unique=True)
    nombre = db.Column(db.String(150), nullable=False)

    puesto_id = db.Column(
        db.Integer,
        db.ForeignKey("puesto.id"),
        nullable=False
    )

    puesto = db.relationship(
        "Puesto",
        backref="colaboradores"
    )


# =========================
# TABLA: HABILIDADES
# =========================

class Habilidad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(
        db.String(150),
        nullable=False,
        unique=True
    )


# =========================
# TABLA: PUESTO-HABILIDAD
# =========================

class PuestoHabilidad(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    puesto_id = db.Column(
        db.Integer,
        db.ForeignKey("puesto.id"),
        nullable=False
    )

    habilidad_id = db.Column(
        db.Integer,
        db.ForeignKey("habilidad.id"),
        nullable=False
    )

    puesto = db.relationship("Puesto")
    habilidad = db.relationship("Habilidad")


# =========================
# TABLA: EVALUACIONES ILUO
# =========================

class Evaluacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    colaborador_id = db.Column(
        db.Integer,
        db.ForeignKey("colaborador.id"),
        nullable=False
    )

    habilidad_id = db.Column(
        db.Integer,
        db.ForeignKey("habilidad.id"),
        nullable=False
    )

    nivel = db.Column(
        db.String(1),
        nullable=False
    )

    colaborador = db.relationship("Colaborador")
    habilidad = db.relationship("Habilidad")


# =========================

class Curso(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nombre = db.Column(
        db.String(200),
        nullable=False
    )

    descripcion = db.Column(
        db.Text,
        nullable=True
    )

    duracion = db.Column(
        db.String(100),
        nullable=True
    )

    enlace = db.Column(
        db.String(500),
        nullable=True
    )

    habilidad_id = db.Column(
        db.Integer,
        db.ForeignKey("habilidad.id"),
        nullable=False
    )

    habilidad = db.relationship(
        "Habilidad"
    )

# INICIO
# =========================

@app.route("/")
def inicio():

    colaboradores = Colaborador.query.count()
    habilidades = Habilidad.query.count()
    evaluaciones = Evaluacion.query.count()

    return render_template(
        "index.html",
        colaboradores=colaboradores,
        habilidades=habilidades,
        evaluaciones=evaluaciones
    )


# =========================
# COLABORADORES
# =========================

@app.route("/colaboradores")
def colaboradores():

    lista_colaboradores = Colaborador.query.order_by(
        Colaborador.nombre
    ).all()

    puestos = Puesto.query.order_by(
        Puesto.nombre
    ).all()

    return render_template(
        "colaboradores.html",
        colaboradores=lista_colaboradores,
        puestos=puestos
    )


@app.route(
    "/colaboradores/agregar",
    methods=["POST"]
)
def agregar_colaborador():

    numero_empleado = request.form.get(
        "numero_empleado"
    )

    nombre = request.form.get(
        "nombre"
    )

    puesto_id = request.form.get(
        "puesto_id",
        type=int
    )

    nuevo_colaborador = Colaborador(
        numero_empleado=numero_empleado,
        nombre=nombre,
        puesto_id=puesto_id
    )

    db.session.add(
        nuevo_colaborador
    )

    db.session.commit()

    return redirect(
        url_for("colaboradores")
    )


@app.route(
    "/colaboradores/eliminar/<int:id>"
)
def eliminar_colaborador(id):

    colaborador = Colaborador.query.get_or_404(id)

    db.session.delete(
        colaborador
    )

    db.session.commit()

    return redirect(
        url_for("colaboradores")
    )


# =========================
# HABILIDADES POR PUESTO
# =========================

@app.route(
    "/puesto-habilidades",
    methods=["GET", "POST"]
)
def puesto_habilidades():

    puestos = Puesto.query.order_by(
        Puesto.nombre
    ).all()

    habilidades = Habilidad.query.order_by(
        Habilidad.nombre
    ).all()

    puesto_seleccionado = request.args.get(
        "puesto_id",
        type=int
    )

    if request.method == "POST":

        puesto_id = request.form.get(
            "puesto_id",
            type=int
        )

        habilidades_seleccionadas = request.form.getlist(
            "habilidades"
        )

        PuestoHabilidad.query.filter_by(
            puesto_id=puesto_id
        ).delete()

        for habilidad_id in habilidades_seleccionadas:

            db.session.add(
                PuestoHabilidad(
                    puesto_id=puesto_id,
                    habilidad_id=int(habilidad_id)
                )
            )

        db.session.commit()

        return redirect(
            url_for(
                "puesto_habilidades",
                puesto_id=puesto_id
            )
        )

    habilidades_asignadas = []

    if puesto_seleccionado:

        asignaciones = PuestoHabilidad.query.filter_by(
            puesto_id=puesto_seleccionado
        ).all()

        habilidades_asignadas = [
            asignacion.habilidad_id
            for asignacion in asignaciones
        ]

    return render_template(
        "puesto_habilidades.html",
        puestos=puestos,
        habilidades=habilidades,
        puesto_seleccionado=puesto_seleccionado,
        habilidades_asignadas=habilidades_asignadas
    )


# =========================
# EVALUACIONES
# =========================

@app.route("/evaluaciones")
def evaluaciones():

    lista_colaboradores = Colaborador.query.order_by(
        Colaborador.nombre
    ).all()

    colaborador_seleccionado = request.args.get(
        "colaborador_id",
        type=int
    )

    colaborador_actual = None
    habilidades = []
    evaluaciones_guardadas = {}

    if colaborador_seleccionado:

        colaborador_actual = Colaborador.query.get_or_404(
            colaborador_seleccionado
        )

        asignaciones = PuestoHabilidad.query.filter_by(
            puesto_id=colaborador_actual.puesto_id
        ).all()

        habilidades = [
            asignacion.habilidad
            for asignacion in asignaciones
        ]

        registros = Evaluacion.query.filter_by(
            colaborador_id=colaborador_actual.id
        ).all()

        evaluaciones_guardadas = {
            registro.habilidad_id: registro.nivel
            for registro in registros
        }

    return render_template(
        "evaluaciones.html",
        colaboradores=lista_colaboradores,
        colaborador_seleccionado=colaborador_seleccionado,
        colaborador_actual=colaborador_actual,
        habilidades=habilidades,
        evaluaciones=evaluaciones_guardadas
    )


# =========================
# GUARDAR EVALUACION
# =========================

@app.route(
    "/evaluaciones/guardar",
    methods=["POST"]
)
def guardar_evaluacion():

    colaborador_id = request.form.get(
        "colaborador_id",
        type=int
    )

    colaborador = Colaborador.query.get_or_404(
        colaborador_id
    )

    habilidades_asignadas = PuestoHabilidad.query.filter_by(
        puesto_id=colaborador.puesto_id
    ).all()

    for asignacion in habilidades_asignadas:

        habilidad_id = asignacion.habilidad_id

        nivel = request.form.get(
            f"nivel_{habilidad_id}"
        )

        if not nivel:
            continue

        evaluacion = Evaluacion.query.filter_by(
            colaborador_id=colaborador_id,
            habilidad_id=habilidad_id
        ).first()

        if evaluacion:

            evaluacion.nivel = nivel

        else:

            evaluacion = Evaluacion(
                colaborador_id=colaborador_id,
                habilidad_id=habilidad_id,
                nivel=nivel
            )

            db.session.add(
                evaluacion
            )

    db.session.commit()

    return redirect(
        url_for(
            "evaluaciones",
            colaborador_id=colaborador_id
        )
    )

# =========================
# MATRIZ ILUO
# =========================

@app.route("/matriz")
def matriz():

    colaboradores = Colaborador.query.order_by(
        Colaborador.nombre
    ).all()

    matriz = []

    for colaborador in colaboradores:

        asignaciones = PuestoHabilidad.query.filter_by(
            puesto_id=colaborador.puesto_id
        ).all()

        habilidades_colaborador = []

        for asignacion in asignaciones:

            habilidad = asignacion.habilidad

            evaluacion = Evaluacion.query.filter_by(
                colaborador_id=colaborador.id,
                habilidad_id=habilidad.id
            ).first()

            nivel = evaluacion.nivel if evaluacion else ""

            habilidades_colaborador.append({
                "id": habilidad.id,
                "nombre": habilidad.nombre,
                "nivel": nivel
            })

        # =========================
        # CALCULAR % DE DOMINIO
        # =========================

        valores = {
            "I": 25,
            "L": 50,
            "U": 75,
            "O": 100
        }

        total = 0
        cantidad = len(habilidades_colaborador)

        for habilidad in habilidades_colaborador:

            nivel = habilidad["nivel"]

            if nivel in valores:
                total += valores[nivel]

        if cantidad > 0:
            porcentaje = round(total / cantidad)
        else:
            porcentaje = 0

        matriz.append({
            "colaborador": colaborador,
            "habilidades": habilidades_colaborador,
            "porcentaje": porcentaje
        })

    return render_template(
        "matriz.html",
        matriz=matriz
    )



# =========================

# =========================
# CURSOS
# =========================

@app.route("/cursos", methods=["GET", "POST"])
def cursos():

    if request.method == "POST":

        nombre = request.form.get("nombre")
        descripcion = request.form.get("descripcion")
        duracion = request.form.get("duracion")
        enlace = request.form.get("enlace")
        habilidad_id = request.form.get("habilidad_id")

        if nombre and habilidad_id:

            curso = Curso(
                nombre=nombre,
                descripcion=descripcion,
                duracion=duracion,
                enlace=enlace,
                habilidad_id=int(habilidad_id)
            )

            db.session.add(curso)
            db.session.commit()

        return redirect(url_for("cursos"))

    cursos_registrados = Curso.query.order_by(
        Curso.nombre
    ).all()

    habilidades = Habilidad.query.order_by(
        Habilidad.nombre
    ).all()

    return render_template(
        "cursos.html",
        cursos=cursos_registrados,
        habilidades=habilidades
    )

# INICIAR APLICACIÓN
# =========================

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)







