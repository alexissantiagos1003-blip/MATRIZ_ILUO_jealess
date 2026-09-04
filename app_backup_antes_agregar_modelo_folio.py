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

    departamento_id = db.Column(
        db.Integer,
        db.ForeignKey("departamento.id"),
        nullable=True
    )

    departamento = db.relationship(
        "Departamento",
        backref="puestos"
    )



# =========================
# TABLA: AREAS
# =========================

class Area(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nombre = db.Column(
        db.String(100),
        nullable=False,
        unique=True
    )


# =========================
# TABLA: DEPARTAMENTOS
# =========================

class Departamento(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nombre = db.Column(
        db.String(100),
        nullable=False,
        unique=True
    )

    area_id = db.Column(
        db.Integer,
        db.ForeignKey("area.id"),
        nullable=True
    )

    area = db.relationship(
        "Area",
        backref="departamentos"
    )

# =========================
# TABLA: COLABORADORES
# =========================

class Colaborador(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero_empleado = db.Column(db.String(50), nullable=False, unique=True)
    nombre = db.Column(db.String(150), nullable=False)

    activo = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    departamento_id = db.Column(
        db.Integer,
        db.ForeignKey("departamento.id"),
        nullable=True
    )

    puesto_id = db.Column(
        db.Integer,
        db.ForeignKey("puesto.id"),
        nullable=False
    )

    puesto = db.relationship(
        "Puesto",
        backref="colaboradores"
    )

    departamento = db.relationship(
        "Departamento",
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

    general = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    produccion = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    mp = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )


# =========================
# TABLA: PUESTO-HABILIDAD
# =========================

class PuestoHabilidad(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    departamento_id = db.Column(
        db.Integer,
        db.ForeignKey("departamento.id"),
        nullable=True
    )

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

    id = db.Column(
        db.Integer,
        primary_key=True
    )

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

    evaluador = db.Column(
        db.String(150),
        nullable=True
    )

    rol_evaluador = db.Column(
        db.String(80),
        nullable=True
    )

    fecha_evaluacion = db.Column(
        db.Date,
        nullable=True
    )

    comentario = db.Column(
        db.Text,
        nullable=True
    )

    firma_archivo = db.Column(
        db.String(500),
        nullable=True
    )

    confirmacion_colaborador = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    colaborador = db.relationship(
        "Colaborador"
    )

    habilidad = db.relationship(
        "Habilidad"
    )

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

    archivo_pdf = db.Column(
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

    lista_colaboradores = Colaborador.query.filter_by(
        activo=1
    ).order_by(
        Colaborador.nombre
    ).all()

    puestos = Puesto.query.order_by(
        Puesto.nombre
    ).all()

    departamentos = Departamento.query.order_by(
        Departamento.nombre
    ).all()

    return render_template(
        "colaboradores.html",
        colaboradores=lista_colaboradores,
        puestos=puestos,
        departamentos=departamentos
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

    departamento_id = request.form.get(
        "departamento_id",
        type=int
    )

    puesto_id = request.form.get(
        "puesto_id",
        type=int
    )

    area_id = request.form.get(
        "area_id",
        type=int
    )

    nuevo_colaborador = Colaborador(
        numero_empleado=numero_empleado,
        nombre=nombre,
        departamento_id=departamento_id,
        puesto_id=puesto_id,
        activo=1
    )

    db.session.add(
        nuevo_colaborador
    )

    db.session.commit()

    return redirect(
        url_for("colaboradores")
    )


@app.route(
    "/colaboradores/baja/<int:id>"
)
def dar_de_baja_colaborador(id):

    colaborador = Colaborador.query.get_or_404(id)

    colaborador.activo = 0

    db.session.commit()

    return redirect(
        url_for("colaboradores")
    )


# =========================
# COLABORADORES INACTIVOS
# =========================

@app.route("/colaboradores/inactivos")
def colaboradores_inactivos():

    lista_inactivos = Colaborador.query.filter_by(
        activo=0
    ).order_by(
        Colaborador.nombre
    ).all()

    return render_template(
        "colaboradores_inactivos.html",
        colaboradores=lista_inactivos
    )


@app.route(
    "/colaboradores/reactivar/<int:id>"
)
def reactivar_colaborador(id):

    colaborador = Colaborador.query.get_or_404(id)

    colaborador.activo = 1

    db.session.commit()

    return redirect(
        url_for("colaboradores_inactivos")
    )


# =========================
# DEPARTAMENTOS
# =========================

@app.route("/departamentos")
def departamentos():

    lista_departamentos = Departamento.query.order_by(
        Departamento.nombre
    ).all()

    areas = Area.query.order_by(
        Area.nombre
    ).all()

    return render_template(
        "departamentos.html",
        departamentos=lista_departamentos,
        areas=areas
    )


@app.route(
    "/departamentos/agregar",
    methods=["POST"]
)
def agregar_departamento():

    nombre = request.form.get(
        "nombre"
    )

    area_id = request.form.get(
        "area_id",
        type=int
    )

    if nombre:

        nombre = nombre.strip()

        existente = Departamento.query.filter_by(
            nombre=nombre
        ).first()

        if not existente:

            nuevo_departamento = Departamento(
                nombre=nombre,
                area_id=area_id
            )

            db.session.add(
                nuevo_departamento
            )

            db.session.commit()

    return redirect(
        url_for("departamentos")
    )


@app.route(
    "/departamentos/eliminar/<int:id>"
)
def eliminar_departamento(id):

    departamento = Departamento.query.get_or_404(id)

    colaboradores_asignados = Colaborador.query.filter_by(
        departamento_id=departamento.id
    ).count()

    if colaboradores_asignados > 0:

        return redirect(
            url_for("departamentos")
        )

    db.session.delete(
        departamento
    )

    db.session.commit()

    return redirect(
        url_for("departamentos")
    )

# =========================
# PUESTOS
# =========================

@app.route("/puestos")
def puestos():

    lista_puestos = Puesto.query.order_by(
        Puesto.nombre
    ).all()

    departamentos = Departamento.query.order_by(
        Departamento.nombre
    ).all()

    areas = Area.query.order_by(
        Area.nombre
    ).all()

    return render_template(
        "puestos.html",
        puestos=lista_puestos,
        departamentos=departamentos,
        areas=areas
    )


@app.route(
    "/puestos/agregar",
    methods=["POST"]
)
def agregar_puesto():

    nombre = request.form.get(
        "nombre"
    )

    departamento_id = request.form.get(
        "departamento_id",
        type=int
    )

    if nombre:

        nombre = nombre.strip()

        existente = Puesto.query.filter_by(
            nombre=nombre
        ).first()

        if not existente:

            nuevo_puesto = Puesto(
                nombre=nombre,
                departamento_id=departamento_id
            )

            db.session.add(
                nuevo_puesto
            )

            db.session.commit()

    return redirect(
        url_for("puestos")
    )


@app.route(
    "/puestos/editar/<int:id>",
    methods=["POST"]
)
def editar_puesto(id):

    puesto = Puesto.query.get_or_404(id)

    departamento_id = request.form.get(
        "departamento_id",
        type=int
    )

    puesto.departamento_id = departamento_id

    db.session.commit()

    return redirect(
        url_for("puestos")
    )


@app.route(
    "/puestos/eliminar/<int:id>"
)
def eliminar_puesto(id):

    puesto = Puesto.query.get_or_404(id)

    db.session.delete(
        puesto
    )

    db.session.commit()

    return redirect(
        url_for("puestos")
    )


# =========================
# HABILIDADES
# =========================

@app.route("/habilidades")
def habilidades():

    lista_habilidades = Habilidad.query.order_by(
        Habilidad.nombre
    ).all()

    return render_template(
        "habilidades.html",
        habilidades=lista_habilidades
    )


@app.route(
    "/habilidades/agregar",
    methods=["POST"]
)
def agregar_habilidad():

    nombre = request.form.get(
        "nombre"
    )

    area_id = request.form.get(
        "area_id",
        type=int
    )

    if nombre:

        nueva_habilidad = Habilidad(
            nombre=nombre
        )

        db.session.add(
            nueva_habilidad
        )

        db.session.commit()

    return redirect(
        url_for("habilidades")
    )


@app.route(
    "/habilidades/eliminar/<int:id>"
)
def eliminar_habilidad(id):

    habilidad = Habilidad.query.get_or_404(id)

    PuestoHabilidad.query.filter_by(
        habilidad_id=habilidad.id
    ).delete()

    db.session.delete(
        habilidad
    )

    db.session.commit()

    return redirect(
        url_for("habilidades")
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

    departamentos = Departamento.query.order_by(
        Departamento.nombre
    ).all()

    habilidades = Habilidad.query.order_by(
        Habilidad.nombre
    ).all()

    departamento_seleccionado = request.args.get(
        "departamento_id",
        type=int
    )

    puesto_seleccionado = request.args.get(
        "puesto_id",
        type=int
    )

    if request.method == "POST":

        puesto_id = request.form.get(
            "puesto_id",
            type=int
        )

        puesto = Puesto.query.get_or_404(
            puesto_id
        )

        departamento_id = puesto.departamento_id

        habilidades_seleccionadas = request.form.getlist(
            "habilidades"
        )

        PuestoHabilidad.query.filter_by(
            puesto_id=puesto_id
        ).delete()

        for habilidad_id in habilidades_seleccionadas:

            db.session.add(
                PuestoHabilidad(
                    departamento_id=departamento_id,
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
        departamentos=departamentos,
        habilidades=habilidades,
        departamento_seleccionado=departamento_seleccionado,
        puesto_seleccionado=puesto_seleccionado,
        habilidades_asignadas=habilidades_asignadas
    )


# =========================
# EVALUACIONES
# =========================

@app.route("/evaluaciones")
def evaluaciones():

    # =========================
    # COLABORADORES ACTIVOS
    # =========================

    lista_colaboradores = Colaborador.query.filter_by(
        activo=1
    ).order_by(
        Colaborador.nombre
    ).all()

    # =========================
    # FILTROS
    # =========================

    colaborador_seleccionado = request.args.get(
        "colaborador_id",
        type=int
    )

    area_seleccionada = request.args.get(
        "area_id",
        type=int
    )

    # =========================
    # DATOS INICIALES
    # =========================

    colaborador_actual = None

    habilidades = []

    evaluaciones_guardadas = {}

    evaluaciones_detalle = {}

    # =========================
    # COLABORADOR SELECCIONADO
    # =========================

    if colaborador_seleccionado:

        colaborador_actual = Colaborador.query.get_or_404(
            colaborador_seleccionado
        )

        # =========================
        # HABILIDADES DEL PUESTO
        # =========================

        asignaciones = PuestoHabilidad.query.filter_by(
            puesto_id=colaborador_actual.puesto_id
        ).all()

        habilidades = [
            asignacion.habilidad
            for asignacion in asignaciones
        ]

        # =========================
        # EVALUACIONES DEL COLABORADOR
        # =========================

        registros = Evaluacion.query.filter_by(
            colaborador_id=colaborador_actual.id
        ).all()

        # =========================
        # NIVEL ACTUAL
        # =========================

        evaluaciones_guardadas = {
            registro.habilidad_id: registro.nivel
            for registro in registros
        }

        # =========================
        # DETALLE COMPLETO
        # =========================

        evaluaciones_detalle = {

            registro.habilidad_id: {

                "id": registro.id,

                "nivel": registro.nivel,

                "evaluador": registro.evaluador,

                "rol_evaluador": registro.rol_evaluador,

                "fecha_evaluacion": registro.fecha_evaluacion,

                "comentario": registro.comentario

            }

            for registro in registros

        }

    # =========================
    # MOSTRAR PANTALLA
    # =========================

    return render_template(

        "evaluaciones.html",

        colaboradores=lista_colaboradores,

        colaborador_seleccionado=colaborador_seleccionado,

        area_seleccionada=area_seleccionada,

        colaborador_actual=colaborador_actual,

        habilidades=habilidades,

        evaluaciones=evaluaciones_guardadas,

        evaluaciones_detalle=evaluaciones_detalle

    )


# =========================
# GUARDAR EVALUACION
# =========================

@app.route(
    "/evaluaciones/guardar",
    methods=["POST"]
)
def guardar_evaluacion():

    import base64
    import os
    import uuid
    from datetime import date

    # =========================
    # DATOS PRINCIPALES
    # =========================

    colaborador_id = request.form.get(
        "colaborador_id",
        type=int
    )

    if not colaborador_id:

        return (
            "Colaborador no especificado.",
            400
        )

    colaborador = Colaborador.query.get_or_404(
        colaborador_id
    )

    # =========================
    # FOLIO ÚNICO DE EVALUACIÓN
    # =========================

    folio = (
        "EVAL-"
        + date.today().strftime("%Y%m%d")
        + "-"
        + uuid.uuid4().hex[:6].upper()
    )

    # =========================
    # DATOS DEL EVALUADOR
    # =========================

    evaluador = request.form.get(
        "evaluador",
        ""
    ).strip()

    rol_evaluador = request.form.get(
        "rol_evaluador",
        ""
    ).strip()

    comentario = request.form.get(
        "comentario",
        ""
    ).strip()

    # =========================
    # FECHA
    # =========================

    fecha_evaluacion = request.form.get(
        "fecha_evaluacion",
        ""
    ).strip()

    fecha_objeto = None

    if fecha_evaluacion:

        try:

            fecha_objeto = date.fromisoformat(
                fecha_evaluacion
            )

        except ValueError:

            return (
                "La fecha de evaluación no es válida.",
                400
            )

    # =========================
    # CONFIRMACIÓN
    # =========================

    confirmacion = request.form.get(
        "confirmacion_colaborador"
    )

    confirmacion_colaborador = (
        confirmacion == "1"
    )

    # =========================
    # FIRMA
    # =========================

    firma_data = request.form.get(
        "firma_data",
        ""
    ).strip()

    # =========================
    # HABILIDADES DEL PUESTO
    # =========================

    habilidades_asignadas = PuestoHabilidad.query.filter_by(
        puesto_id=colaborador.puesto_id
    ).all()

    # =========================
    # VALIDAR TODAS LAS HABILIDADES
    # =========================

    habilidades_sin_evaluar = []

    niveles_recibidos = []

    for asignacion in habilidades_asignadas:

        nivel = request.form.get(
            f"nivel_{asignacion.habilidad_id}"
        )

        if not nivel or not nivel.strip():

            if asignacion.habilidad:

                habilidades_sin_evaluar.append(
                    asignacion.habilidad.nombre
                )

            else:

                habilidades_sin_evaluar.append(
                    f"Habilidad {asignacion.habilidad_id}"
                )

        else:

            niveles_recibidos.append(
                nivel.strip().upper()
            )

    # =========================
    # NO PERMITIR EVALUACIÓN
    # INCOMPLETA
    # =========================

    if habilidades_sin_evaluar:

        lista_faltantes = ", ".join(
            habilidades_sin_evaluar
        )

        return (
            "No se puede guardar la evaluación. "
            "Faltan por evaluar: "
            + lista_faltantes,
            400
        )

    # =========================
    # VALIDAR NIVELES ILUO
    # =========================

    niveles_validos = {
        "I",
        "L",
        "U",
        "O"
    }

    niveles_invalidos = [
        nivel
        for nivel in niveles_recibidos
        if nivel not in niveles_validos
    ]

    if niveles_invalidos:

        return (
            "Se encontró un nivel ILUO no válido.",
            400
        )

    # =========================
    # FIRMA OBLIGATORIA
    # =========================

    if not firma_data:

        return (
            "La firma del colaborador es obligatoria.",
            400
        )

    # =========================
    # CONFIRMACIÓN OBLIGATORIA
    # =========================

    if not confirmacion_colaborador:

        return (
            "El colaborador debe confirmar que fue evaluado.",
            400
        )

    # =========================
    # VALIDAR FORMATO FIRMA
    # =========================

    prefijo = "data:image/png;base64,"

    if not firma_data.startswith(prefijo):

        return (
            "El formato de la firma no es válido.",
            400
        )

    try:

        contenido_base64 = firma_data[
            len(prefijo):
        ]

        datos_firma = base64.b64decode(
            contenido_base64,
            validate=True
        )

    except Exception:

        return (
            "No fue posible procesar la firma.",
            400
        )

    # =========================
    # VALIDAR TAMAÑO
    # =========================

    if len(datos_firma) < 100:

        return (
            "La firma capturada está vacía o es demasiado pequeña.",
            400
        )

    if len(datos_firma) > 2 * 1024 * 1024:

        return (
            "La firma es demasiado grande.",
            400
        )

    # =========================
    # CREAR CARPETA
    # =========================

    carpeta_firmas = os.path.join(
        app.root_path,
        "static",
        "uploads",
        "firmas"
    )

    os.makedirs(
        carpeta_firmas,
        exist_ok=True
    )

    # =========================
    # NOMBRE ÚNICO
    # =========================

    nombre_firma = (
        f"firma_{colaborador.id}_"
        f"{uuid.uuid4().hex}.png"
    )

    ruta_firma = os.path.join(
        carpeta_firmas,
        nombre_firma
    )

    # =========================
    # GUARDAR PNG
    # =========================

    try:

        with open(
            ruta_firma,
            "wb"
        ) as archivo_firma:

            archivo_firma.write(
                datos_firma
            )

    except Exception:

        return (
            "No fue posible guardar la firma.",
            500
        )

    # =========================
    # NIVELES PERMITIDOS
    # =========================

    niveles_validos = {
        "I",
        "L",
        "U",
        "O"
    }

    # =========================
    # GUARDAR EVALUACIONES
    # =========================

    for asignacion in habilidades_asignadas:

        habilidad_id = asignacion.habilidad_id

        nivel = request.form.get(
            f"nivel_{habilidad_id}"
        )

        if not nivel:

            continue

        nivel = nivel.strip().upper()

        # =========================
        # VALIDAR ILUO
        # =========================

        if nivel not in niveles_validos:

            return (
                f"Nivel ILUO inválido para "
                f"la habilidad {habilidad_id}.",
                400
            )

        # =========================
        # BUSCAR EVALUACIÓN
        # =========================

        evaluacion = Evaluacion.query.filter_by(
            colaborador_id=colaborador_id,
            habilidad_id=habilidad_id
        ).first()

        # =========================
        # ACTUALIZAR
        # =========================

        if evaluacion:

            evaluacion.nivel = nivel

            evaluacion.evaluador = (
                evaluador
                if evaluador
                else evaluacion.evaluador
            )

            evaluacion.rol_evaluador = (
                rol_evaluador
                if rol_evaluador
                else evaluacion.rol_evaluador
            )

            evaluacion.fecha_evaluacion = (
                fecha_objeto
                if fecha_objeto
                else evaluacion.fecha_evaluacion
            )

            evaluacion.comentario = (
                comentario
                if comentario
                else evaluacion.comentario
            )

            evaluacion.firma_archivo = (
                f"uploads/firmas/{nombre_firma}"
            )

            evaluacion.confirmacion_colaborador = True

        # =========================
        # CREAR
        # =========================

        else:

            evaluacion = Evaluacion(

                folio=folio,

                colaborador_id=colaborador_id,

                habilidad_id=habilidad_id,

                nivel=nivel,

                evaluador=(
                    evaluador
                    if evaluador
                    else None
                ),

                rol_evaluador=(
                    rol_evaluador
                    if rol_evaluador
                    else None
                ),

                fecha_evaluacion=fecha_objeto,

                comentario=(
                    comentario
                    if comentario
                    else None
                ),

                firma_archivo=(
                    f"uploads/firmas/{nombre_firma}"
                ),

                confirmacion_colaborador=True

            )

            db.session.add(
                evaluacion
            )

    # =========================
    # GUARDAR
    # =========================

    db.session.commit()

    # =========================
    # REGRESAR
    # =========================

    return redirect(
        url_for(
            "evaluaciones",
            colaborador_id=colaborador_id
        )
    )

# =========================
# HISTORIAL DE EVALUACIONES
# =========================

@app.route("/historial-evaluaciones")
def historial_evaluaciones():

    # =========================
    # FILTROS
    # =========================

    colaborador_id = request.args.get(
        "colaborador_id",
        type=int
    )

    area_id = request.args.get(
        "area_id",
        type=int
    )

    departamento_id = request.args.get(
        "departamento_id",
        type=int
    )

    puesto_id = request.args.get(
        "puesto_id",
        type=int
    )

    # =========================
    # LISTAS PARA FILTROS
    # =========================

    colaboradores = Colaborador.query.filter_by(
        activo=1
    ).order_by(
        Colaborador.nombre
    ).all()

    areas = Area.query.order_by(
        Area.nombre
    ).all()

    departamentos = Departamento.query.order_by(
        Departamento.nombre
    ).all()

    puestos = Puesto.query.order_by(
        Puesto.nombre
    ).all()

    # =========================
    # CONSULTA BASE
    # =========================

    consulta = Evaluacion.query.join(
        Colaborador,
        Evaluacion.colaborador_id == Colaborador.id
    )

    # =========================
    # FILTRO COLABORADOR
    # =========================

    if colaborador_id:

        consulta = consulta.filter(
            Evaluacion.colaborador_id == colaborador_id
        )

    # =========================
    # OBTENER REGISTROS
    # =========================

    evaluaciones = consulta.order_by(
        Evaluacion.fecha_evaluacion.desc(),
        Evaluacion.id.desc()
    ).all()

    # =========================
    # FILTROS COMPLEMENTARIOS
    # =========================

    evaluaciones_filtradas = []

    for evaluacion in evaluaciones:

        colaborador = evaluacion.colaborador

        if not colaborador:
            continue

        if area_id:

            if not colaborador.departamento:
                continue

            if colaborador.departamento.area_id != area_id:
                continue

        if departamento_id:

            if colaborador.departamento_id != departamento_id:
                continue

        if puesto_id:

            if colaborador.puesto_id != puesto_id:
                continue

        evaluaciones_filtradas.append(
            evaluacion
        )

    # =========================
    # AGRUPAR POR EVALUACIÓN
    # =========================

    historial = {}

    for evaluacion in evaluaciones_filtradas:

        clave = (
            evaluacion.colaborador_id,
            evaluacion.fecha_evaluacion
        )

        if clave not in historial:

            historial[clave] = {
                "colaborador": evaluacion.colaborador,
                "fecha": evaluacion.fecha_evaluacion,
                "evaluador": evaluacion.evaluador,
                "rol_evaluador": evaluacion.rol_evaluador,
                "firma_archivo": evaluacion.firma_archivo,
                "confirmacion_colaborador":
                    evaluacion.confirmacion_colaborador,
                "evaluaciones": []
            }

        historial[clave]["evaluaciones"].append(
            evaluacion
        )

    historial_lista = list(
        historial.values()
    )

    # =========================
    # MOSTRAR HISTORIAL
    # =========================

    return render_template(
        "historial_evaluaciones.html",
        historial=historial_lista,
        colaboradores=colaboradores,
        areas=areas,
        departamentos=departamentos,
        puestos=puestos,
        colaborador_seleccionado=colaborador_id,
        area_seleccionada=area_id,
        departamento_seleccionado=departamento_id,
        puesto_seleccionado=puesto_id
    )

# =========================
# MATRIZ ILUO
# =========================

@app.route("/matriz")
def matriz():

    areas = Area.query.order_by(
        Area.nombre
    ).all()

    departamentos = Departamento.query.order_by(
        Departamento.nombre
    ).all()

    puestos = Puesto.query.order_by(
        Puesto.nombre
    ).all()

    colaboradores = Colaborador.query.filter_by(
        activo=1
    ).order_by(
        Colaborador.nombre
    ).all()

    # =========================
    # FILTROS
    # =========================

    area_seleccionada = request.args.get(
        "area_id",
        type=int
    )

    departamento_seleccionado = request.args.get(
        "departamento_id",
        type=int
    )

    puesto_seleccionado = request.args.get(
        "puesto_id",
        type=int
    )

    colaborador_seleccionado = request.args.get(
        "colaborador_id",
        type=int
    )

    # =========================
    # ÁREA POR DEFECTO
    # =========================

    if not area_seleccionada and areas:
        area_seleccionada = areas[0].id

    # =========================
    # FILTRAR COLABORADORES
    # =========================

    colaboradores_filtrados = colaboradores

    if area_seleccionada:

        colaboradores_filtrados = [
            colaborador
            for colaborador in colaboradores_filtrados
            if colaborador.departamento
            and colaborador.departamento.area_id == area_seleccionada
        ]

    if departamento_seleccionado:

        colaboradores_filtrados = [
            colaborador
            for colaborador in colaboradores_filtrados
            if colaborador.departamento_id == departamento_seleccionado
        ]

    if puesto_seleccionado:

        colaboradores_filtrados = [
            colaborador
            for colaborador in colaboradores_filtrados
            if colaborador.puesto_id == puesto_seleccionado
        ]

    if colaborador_seleccionado:

        colaboradores_filtrados = [
            colaborador
            for colaborador in colaboradores_filtrados
            if colaborador.id == colaborador_seleccionado
        ]

    # =========================
    # DETERMINAR HABILIDADES
    # SEGÚN EL NIVEL DE FILTRO
    # =========================

    ids_habilidades = set()

    # -------------------------
    # 1. COLABORADOR
    # -------------------------

    if colaborador_seleccionado:

        colaborador = Colaborador.query.get(
            colaborador_seleccionado
        )

        if colaborador:

            asignaciones = PuestoHabilidad.query.filter_by(
                puesto_id=colaborador.puesto_id
            ).all()

            ids_habilidades = {
                asignacion.habilidad_id
                for asignacion in asignaciones
            }

    # -------------------------
    # 2. PUESTO
    # -------------------------

    elif puesto_seleccionado:

        asignaciones = PuestoHabilidad.query.filter_by(
            puesto_id=puesto_seleccionado
        ).all()

        ids_habilidades = {
            asignacion.habilidad_id
            for asignacion in asignaciones
        }

    # -------------------------
    # 3. DEPARTAMENTO
    # -------------------------

    elif departamento_seleccionado:

        puestos_departamento = Puesto.query.filter_by(
            departamento_id=departamento_seleccionado
        ).all()

        ids_puestos = {
            puesto.id
            for puesto in puestos_departamento
        }

        if ids_puestos:

            asignaciones = PuestoHabilidad.query.filter(
                PuestoHabilidad.puesto_id.in_(ids_puestos)
            ).all()

            ids_habilidades = {
                asignacion.habilidad_id
                for asignacion in asignaciones
            }

    # -------------------------
    # 4. ÁREA
    # -------------------------

    elif area_seleccionada:

        puestos_area = Puesto.query.join(
            Departamento,
            Departamento.id == Puesto.departamento_id
        ).filter(
            Departamento.area_id == area_seleccionada
        ).all()

        ids_puestos = {
            puesto.id
            for puesto in puestos_area
        }

        if ids_puestos:

            asignaciones = PuestoHabilidad.query.filter(
                PuestoHabilidad.puesto_id.in_(ids_puestos)
            ).all()

            ids_habilidades = {
                asignacion.habilidad_id
                for asignacion in asignaciones
            }

    # =========================
    # OBTENER HABILIDADES
    # =========================

    if ids_habilidades:

        habilidades_area = Habilidad.query.filter(
            Habilidad.id.in_(ids_habilidades)
        ).order_by(
            Habilidad.nombre
        ).all()

    else:

        habilidades_area = []

    # =========================
    # CONSTRUIR MATRIZ
    # =========================

    matriz = []

    for colaborador in colaboradores_filtrados:

        asignaciones = PuestoHabilidad.query.filter_by(
            puesto_id=colaborador.puesto_id
        ).all()

        habilidades_puesto = {
            asignacion.habilidad_id
            for asignacion in asignaciones
        }

        evaluaciones = Evaluacion.query.filter_by(
            colaborador_id=colaborador.id
        ).all()

        evaluaciones_por_habilidad = {
            evaluacion.habilidad_id: evaluacion.nivel
            for evaluacion in evaluaciones
        }

        habilidades_colaborador = []

        for habilidad in habilidades_area:

            aplica = habilidad.id in habilidades_puesto

            nivel = ""

            if aplica:

                nivel = evaluaciones_por_habilidad.get(
                    habilidad.id,
                    ""
                )

            habilidades_colaborador.append({
                "id": habilidad.id,
                "nombre": habilidad.nombre,
                "aplica": aplica,
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
        habilidades_evaluadas = 0

        for habilidad in habilidades_colaborador:

            nivel = habilidad["nivel"]

            if nivel in valores:

                total += valores[nivel]

                habilidades_evaluadas += 1

        if habilidades_evaluadas > 0:

            porcentaje = round(
                total / habilidades_evaluadas
            )

        else:

            porcentaje = 0

        matriz.append({
            "colaborador": colaborador,
            "habilidades": habilidades_colaborador,
            "porcentaje": porcentaje
        })

    # =========================
    # MOSTRAR MATRIZ
    # =========================

    return render_template(
        "matriz.html",
        matriz=matriz,
        habilidades_area=habilidades_area,
        areas=areas,
        departamentos=departamentos,
        puestos=puestos,
        colaboradores=colaboradores,
        area_seleccionada=area_seleccionada,
        departamento_seleccionado=departamento_seleccionado,
        puesto_seleccionado=puesto_seleccionado,
        colaborador_seleccionado=colaborador_seleccionado
    )

# =========================
    # FILTRAR COLABORADORES
    # =========================

    colaboradores_filtrados = colaboradores

    # =========================
    # FILTRAR POR ÁREA
    # =========================

    if area_seleccionada:

        colaboradores_filtrados = [
            colaborador
            for colaborador in colaboradores_filtrados
            if colaborador.departamento
            and colaborador.departamento.area_id == area_seleccionada
        ]

    if departamento_seleccionado:

        colaboradores_filtrados = [
            colaborador
            for colaborador in colaboradores_filtrados
            if colaborador.departamento_id == departamento_seleccionado
        ]


    if puesto_seleccionado:

        colaboradores_filtrados = [
            colaborador
            for colaborador in colaboradores_filtrados
            if colaborador.puesto_id == puesto_seleccionado
        ]


    if colaborador_seleccionado:

        colaboradores_filtrados = [
            colaborador
            for colaborador in colaboradores_filtrados
            if colaborador.id == colaborador_seleccionado
        ]


    # =========================
    # CONSTRUIR MATRIZ
    # =========================

    matriz = []


    for colaborador in colaboradores_filtrados:

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

        habilidades_evaluadas = 0


        for habilidad in habilidades_colaborador:

            nivel = habilidad["nivel"]


            if nivel in valores:

                total += valores[nivel]

                habilidades_evaluadas += 1


        if habilidades_evaluadas > 0:

            porcentaje = round(
                total / habilidades_evaluadas
            )

        else:

            porcentaje = 0


        matriz.append({
            "colaborador": colaborador,
            "habilidades": habilidades_colaborador,
            "porcentaje": porcentaje
        })


    return render_template(
        "matriz.html",
        matriz=matriz,
        departamentos=departamentos,
        puestos=puestos,
        colaboradores=colaboradores,
        areas=areas,
        departamento_seleccionado=departamento_seleccionado,
        puesto_seleccionado=puesto_seleccionado,
        colaborador_seleccionado=colaborador_seleccionado,
        area_seleccionada=area_seleccionada
    )

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

        archivo = request.files.get("archivo_pdf")

        archivo_guardado = None

        if archivo and archivo.filename:

            if archivo_permitido(archivo.filename):

                nombre_seguro = secure_filename(
                    archivo.filename
                )

                nombre_final = (
                    str(int(__import__("time").time()))
                    + "_"
                    + nombre_seguro
                )

                ruta = os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    nombre_final
                )

                archivo.save(ruta)

                archivo_guardado = nombre_final

        if nombre and habilidad_id:

            curso = Curso(
                nombre=nombre,
                descripcion=descripcion,
                duracion=duracion,
                enlace=enlace,
                archivo_pdf=archivo_guardado,
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



# =========================
# ARCHIVOS PDF DE CURSOS
# =========================

@app.route("/curso-pdf/<nombre_archivo>")
def curso_pdf(nombre_archivo):

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        nombre_archivo
    )



# INICIAR APLICACIÓN
# =========================

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)























































@app.route("/puesto-habilidades-matriz", methods=["GET", "POST"])
def puesto_habilidades_matriz():
    puestos = Puesto.query.order_by(Puesto.nombre).all()
    habilidades = Habilidad.query.order_by(Habilidad.nombre).all()

    if request.method == "POST":
        PuestoHabilidad.query.delete()
        for key in request.form:
            if key.startswith("ph_"):
                parts = key.split("_")
                puesto_id = int(parts[1])
                habilidad_id = int(parts[2])
                nueva_relacion = PuestoHabilidad(
                    puesto_id=puesto_id,
                    habilidad_id=habilidad_id
                )
                db.session.add(nueva_relacion)
        db.session.commit()
        return redirect(url_for("puesto_habilidades_matriz"))

    asignaciones = PuestoHabilidad.query.all()
    mapa_asignaciones = {(a.puesto_id, a.habilidad_id): True for a in asignaciones}

    return render_template(
        "puesto_habilidades_matriz.html",
        puestos=puestos,
        habilidades=habilidades,
        mapa_asignaciones=mapa_asignaciones
    )













