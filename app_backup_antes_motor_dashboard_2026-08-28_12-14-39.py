from flask import Flask, render_template, request, redirect, url_for, send_from_directory, send_file
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename
import uuid
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

    puesto_padre_id = db.Column(
        db.Integer,
        db.ForeignKey("puesto.id"),
        nullable=True
    )

    puesto_padre = db.relationship(
        "Puesto",
        remote_side=[id],
        backref="puestos_hijos"
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

    folio = db.Column(
        db.String(40),
        nullable=True,
        unique=True
    )

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

    orden = db.Column(
        db.Integer,
        nullable=False,
        default=1
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


# ============================================================
# HISTORIAL DE ACTUALIZACIONES DE CURSOS
# ============================================================

class CursoActualizacion(db.Model):

    __tablename__ = "curso_actualizacion"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    curso_id = db.Column(
        db.Integer,
        db.ForeignKey("curso.id"),
        nullable=False
    )

    fecha = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp()
    )

    cambios = db.Column(
        db.Text,
        nullable=True
    )

    pdf_anterior = db.Column(
        db.String(500),
        nullable=True
    )

    pdf_nuevo = db.Column(
        db.String(500),
        nullable=True
    )

    curso = db.relationship(
        "Curso",
        backref=db.backref(
            "actualizaciones",
            lazy=True,
            cascade="all, delete-orphan"
        )
    )


# ============================================================
# CURSOS
# ============================================================

# ============================================================
# MATRIZ ILUO
# ============================================================

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
        activo=True
    ).order_by(
        Colaborador.nombre
    ).all()


    # ========================================================
    # FILTROS
    # ========================================================

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


    # ========================================================
    # FILTRAR COLABORADORES
    # ========================================================

    colaboradores_filtrados = colaboradores


    if area_seleccionada:

        colaboradores_filtrados = [
            colaborador
            for colaborador in colaboradores_filtrados
            if (
                colaborador.departamento
                and colaborador.departamento.area_id == area_seleccionada
            )
            or (
                colaborador.departamento is None
                and area_seleccionada == 1
            )
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


    # ========================================================
    # CONSTRUIR LISTA GENERAL DE HABILIDADES
    # ========================================================

    habilidades_area = []

    habilidades_ids = set()


    for colaborador in colaboradores_filtrados:

        asignaciones = PuestoHabilidad.query.filter_by(
            puesto_id=colaborador.puesto_id
        ).all()


        for asignacion in asignaciones:

            habilidad = asignacion.habilidad

            if habilidad and habilidad.id not in habilidades_ids:

                habilidades_ids.add(habilidad.id)

                habilidades_area.append(habilidad)


    habilidades_area.sort(
        key=lambda habilidad: habilidad.nombre
    )


    # ========================================================
    # CONSTRUIR MATRIZ
    # ========================================================

    matriz = []


    valores = {
        "I": 25,
        "L": 50,
        "U": 75,
        "O": 100
    }


    for colaborador in colaboradores_filtrados:

        asignaciones = PuestoHabilidad.query.filter_by(
            puesto_id=colaborador.puesto_id
        ).all()


        habilidades_puesto = {
            asignacion.habilidad_id
            for asignacion in asignaciones
        }


        habilidades_colaborador = []


        for habilidad in habilidades_area:

            aplica = habilidad.id in habilidades_puesto


            evaluacion = None


            if aplica:

                evaluacion = Evaluacion.query.filter_by(
                    colaborador_id=colaborador.id,
                    habilidad_id=habilidad.id
                ).first()


            nivel = evaluacion.nivel if evaluacion else ""


            habilidades_colaborador.append({
                "id": habilidad.id,
                "nombre": habilidad.nombre,
                "nivel": nivel,
                "aplica": aplica
            })


        # ====================================================
        # CALCULAR % DE DOMINIO
        # ====================================================

        total = 0

        cantidad = 0


        for habilidad in habilidades_colaborador:

            nivel = habilidad["nivel"]

            if habilidad["aplica"]:

                cantidad += 1

                if nivel in valores:

                    total += valores[nivel]


        if cantidad > 0:

            porcentaje = round(
                total / cantidad
            )

        else:

            porcentaje = 0


        matriz.append({
            "colaborador": colaborador,
            "habilidades": habilidades_colaborador,
            "porcentaje": porcentaje
        })


    # ========================================================
    # RENDERIZAR
    # ========================================================

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


# ============================================================
# CURSOS
# ============================================================

# ============================================================

# ============================================================
@app.route("/cursos")
def cursos():

    lista_cursos = Curso.query.order_by(
        Curso.orden,
        Curso.nombre
    ).all()

    habilidades = Habilidad.query.order_by(
        Habilidad.nombre
    ).all()

    return render_template(
        "cursos.html",
        cursos=lista_cursos,
        habilidades=habilidades
    )

# ============================================================
# GESTIÓN DE CURSOS
# ============================================================

@app.route(
    "/cursos/agregar",
    methods=["POST"]
)
def agregar_curso():

    nombre = request.form.get(
        "nombre",
        ""
    ).strip()

    descripcion = request.form.get(
        "descripcion",
        ""
    ).strip()

    duracion = request.form.get(
        "duracion",
        ""
    ).strip()

    enlace = request.form.get(
        "enlace",
        ""
    ).strip()

    habilidad_id = request.form.get(
        "habilidad_id",
        type=int
    )

    archivo_pdf = request.files.get(
        "archivo_pdf"
    )

    if not nombre:
        return (
            "El nombre del curso es obligatorio.",
            400
        )

    if not habilidad_id:
        return (
            "La habilidad relacionada es obligatoria.",
            400
        )

    # ========================================================
    # ASIGNAR ORDEN AUTOMATICAMENTE
    # ========================================================

    ultimo_curso = Curso.query.order_by(
        Curso.orden.desc()
    ).first()

    siguiente_orden = (
        ultimo_curso.orden + 1
        if ultimo_curso
        else 1
    )

    curso = Curso(
        nombre=nombre,
        descripcion=descripcion,
        duracion=duracion,
        enlace=enlace,
        habilidad_id=habilidad_id,
        orden=siguiente_orden
    )

    db.session.add(curso)
    db.session.commit()

    # ========================================================
    # GUARDAR PDF DEL CURSO
    # ========================================================

    if archivo_pdf and archivo_pdf.filename:

        if not archivo_permitido(
            archivo_pdf.filename
        ):
            return (
                "El archivo debe ser un PDF.",
                400
            )

        nombre_original = secure_filename(
            archivo_pdf.filename
        )

        nombre_archivo = (
            f"curso_{curso.id}_"
            f"{uuid.uuid4().hex}.pdf"
        )

        ruta_pdf = os.path.join(
            app.config["UPLOAD_FOLDER"],
            nombre_archivo
        )

        archivo_pdf.save(
            ruta_pdf
        )

        curso.archivo_pdf = (
            f"cursos/{nombre_archivo}"
        )

        db.session.commit()

    return redirect(
        url_for("cursos")
    )


@app.route(
    "/cursos/pdf/<path:nombre_archivo>"
)
def curso_pdf(nombre_archivo):

    ruta = os.path.join(
        app.config["UPLOAD_FOLDER"],
        os.path.basename(nombre_archivo)
    )

    if not os.path.exists(ruta):
        return (
            "El archivo PDF no existe.",
            404
        )

    return send_file(
        ruta,
        mimetype="application/pdf",
        as_attachment=False
    )

# ============================================================
# EDITAR CURSO
# ============================================================

@app.route(
    "/cursos/editar/<int:id>",
    methods=["GET", "POST"]
)
def editar_curso(id):

    curso = Curso.query.get_or_404(id)

    habilidades = Habilidad.query.order_by(
        Habilidad.nombre
    ).all()

    # ========================================================
    # GET = MOSTRAR FORMULARIO
    # ========================================================

    if request.method == "GET":

        return render_template(
            "curso_editar.html",
            curso=curso,
            habilidades=habilidades
        )

    # ========================================================
    # POST = GUARDAR CAMBIOS
    # ========================================================

    nombre = request.form.get(
        "nombre",
        ""
    ).strip()

    descripcion = request.form.get(
        "descripcion",
        ""
    ).strip()

    duracion = request.form.get(
        "duracion",
        ""
    ).strip()

    enlace = request.form.get(
        "enlace",
        ""
    ).strip()

    cambios = request.form.get(
        "cambios",
        ""
    ).strip()

    habilidad_id = request.form.get(
        "habilidad_id",
        type=int
    )

    archivo_pdf = request.files.get(
        "archivo_pdf"
    )

    if not nombre:

        return (
            "El nombre del curso es obligatorio.",
            400
        )

    if not habilidad_id:

        return (
            "La habilidad relacionada es obligatoria.",
            400
        )

    if not cambios:

        return (
            "Debes indicar qué cambios se realizaron en el curso.",
            400
        )

    # ========================================================
    # GUARDAR REFERENCIA DEL PDF ANTERIOR
    # ========================================================

    pdf_anterior = curso.archivo_pdf

    pdf_nuevo = None

    # ========================================================
    # ACTUALIZAR DATOS DEL CURSO
    # ========================================================

    curso.nombre = nombre
    curso.descripcion = descripcion
    curso.duracion = duracion
    curso.enlace = enlace
    curso.habilidad_id = habilidad_id

    # ========================================================
    # REEMPLAZAR PDF SI SE SUBIO UNO NUEVO
    # ========================================================

    if archivo_pdf and archivo_pdf.filename:

        if not archivo_permitido(
            archivo_pdf.filename
        ):

            return (
                "El archivo debe ser un PDF.",
                400
            )

        nombre_archivo = (
            f"curso_{curso.id}_"
            f"{uuid.uuid4().hex}.pdf"
        )

        ruta_pdf = os.path.join(
            app.config["UPLOAD_FOLDER"],
            nombre_archivo
        )

        archivo_pdf.save(
            ruta_pdf
        )

        pdf_nuevo = (
            f"cursos/{nombre_archivo}"
        )

        curso.archivo_pdf = pdf_nuevo

    # ========================================================
    # REGISTRAR ACTUALIZACION
    # ========================================================

    actualizacion = CursoActualizacion(

        curso_id=curso.id,

        cambios=cambios,

        pdf_anterior=pdf_anterior,

        pdf_nuevo=pdf_nuevo
    )

    db.session.add(
        actualizacion
    )

    db.session.commit()

    return redirect(
        url_for("cursos")
    )

# ============================================================
# ELIMINAR CURSO
# ============================================================

# ============================================================
# HISTORIAL DE ACTUALIZACIONES DE UN CURSO
# ============================================================

@app.route(
    "/cursos/historial/<int:id>"
)
def historial_curso(id):

    curso = Curso.query.get_or_404(id)

    actualizaciones = CursoActualizacion.query.filter_by(
        curso_id=curso.id
    ).order_by(
        CursoActualizacion.fecha.desc()
    ).all()

    return render_template(
        "historial_curso.html",
        curso=curso,
        actualizaciones=actualizaciones
    )


# ============================================================
# ELIMINAR CURSO
# ============================================================

@app.route(
    "/cursos/eliminar/<int:id>",
    methods=["POST"]
)
def eliminar_curso(id):

    curso = Curso.query.get_or_404(id)

    db.session.delete(curso)

    db.session.commit()

    return redirect(
        url_for("cursos")
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

    # ========================================================
    # PUESTOS DISPONIBLES COMO PADRE
    # ========================================================

    puestos_padre = Puesto.query.order_by(
        Puesto.nombre
    ).all()

    return render_template(
        "puestos.html",
        puestos=lista_puestos,
        departamentos=departamentos,
        areas=areas,
        puestos_padre=puestos_padre
    )


# ============================================================
# AGREGAR PUESTO
# ============================================================

@app.route(
    "/puestos/agregar",
    methods=["POST"]
)
def agregar_puesto():

    nombre = request.form.get(
        "nombre",
        ""
    ).strip()

    departamento_id = request.form.get(
        "departamento_id",
        type=int
    )

    puesto_padre_id = request.form.get(
        "puesto_padre_id",
        type=int
    )

    if not nombre:
        return redirect(
            url_for("puestos")
        )

    existente = Puesto.query.filter_by(
        nombre=nombre
    ).first()

    if existente:
        return redirect(
            url_for("puestos")
        )

    if puesto_padre_id:

        puesto_padre = Puesto.query.get(
            puesto_padre_id
        )

        if not puesto_padre:
            puesto_padre_id = None

    nuevo_puesto = Puesto(
        nombre=nombre,
        departamento_id=departamento_id,
        puesto_padre_id=puesto_padre_id
    )

    db.session.add(
        nuevo_puesto
    )

    db.session.commit()

    return redirect(
        url_for("puestos")
    )


# ============================================================
# EDITAR PUESTO
# ============================================================

@app.route(
    "/puestos/editar/<int:id>",
    methods=["POST"]
)
def editar_puesto(id):

    puesto = Puesto.query.get_or_404(
        id
    )

    nombre = request.form.get(
        "nombre",
        ""
    ).strip()

    departamento_id = request.form.get(
        "departamento_id",
        type=int
    )

    puesto_padre_id = request.form.get(
        "puesto_padre_id",
        type=int
    )

    if not nombre:
        return redirect(
            url_for("puestos")
        )

    existente = Puesto.query.filter(
        Puesto.nombre == nombre,
        Puesto.id != puesto.id
    ).first()

    if existente:
        return redirect(
            url_for("puestos")
        )

    # Un puesto no puede ser su propio padre

    if puesto_padre_id == puesto.id:

        return redirect(
            url_for("puestos")
        )

    # ========================================================
    # VALIDAR CICLOS JERARQUICOS
    # ========================================================

    if puesto_padre_id:

        actual = Puesto.query.get(
            puesto_padre_id
        )

        visitados = set()

        while actual:

            if actual.id in visitados:
                break

            visitados.add(
                actual.id
            )

            if actual.id == puesto.id:

                return redirect(
                    url_for("puestos")
                )

            if not actual.puesto_padre_id:
                break

            actual = Puesto.query.get(
                actual.puesto_padre_id
            )

    puesto.nombre = nombre

    puesto.departamento_id = (
        departamento_id
    )

    puesto.puesto_padre_id = (
        puesto_padre_id
    )

    db.session.commit()

    return redirect(
        url_for("puestos")
    )


# ============================================================
# ELIMINAR PUESTO
# ============================================================

@app.route(
    "/puestos/eliminar/<int:id>"
)
def eliminar_puesto(id):

    puesto = Puesto.query.get_or_404(
        id
    )

    subordinados = Puesto.query.filter_by(
        puesto_padre_id=puesto.id
    ).count()

    if subordinados > 0:

        return redirect(
            url_for("puestos")
        )

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



# ============================================================
# DETALLE DE EVALUACIÓN
# ============================================================

@app.route("/evaluacion/ver/<int:evaluacion_id>")
def ver_evaluacion(evaluacion_id):

    evaluacion = Evaluacion.query.get_or_404(
        evaluacion_id
    )

    # Obtener todas las habilidades de la misma evaluación.
    # El folio identifica el conjunto completo.
    evaluaciones_relacionadas = Evaluacion.query.filter(
        Evaluacion.folio == evaluacion.folio
    ).order_by(
        Evaluacion.id
    ).all()

    # Compatibilidad con registros antiguos.
    if not evaluaciones_relacionadas:

        evaluaciones_relacionadas = [
            evaluacion
        ]

    return render_template(
        "evaluacion_detalle.html",
        evaluacion=evaluacion,
        evaluaciones=evaluaciones_relacionadas
    )


# ============================================================
# PDF DE EVIDENCIA DOCUMENTAL
# ============================================================

@app.route("/evaluacion/pdf/<int:evaluacion_id>")
def pdf_evaluacion(evaluacion_id):

    import io
    import os

    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        Image
    )

    evaluacion = Evaluacion.query.get_or_404(
        evaluacion_id
    )

    # ========================================================
    # RECUPERAR TODA LA EVALUACIÓN POR FOLIO
    # ========================================================

    evaluaciones = Evaluacion.query.filter(
        Evaluacion.folio == evaluacion.folio
    ).order_by(
        Evaluacion.id
    ).all()

    if not evaluaciones:

        evaluaciones = [
            evaluacion
        ]

    colaborador = evaluacion.colaborador

    # ========================================================
    # INFORMACIÓN GENERAL
    # ========================================================

    nombre_colaborador = (
        colaborador.nombre
        if colaborador
        else "Sin colaborador"
    )

    puesto = "—"

    if colaborador and colaborador.puesto:

        puesto = colaborador.puesto.nombre

    departamento = "—"

    if colaborador and colaborador.departamento:

        departamento = colaborador.departamento.nombre

    area = "—"

    if (
        colaborador
        and colaborador.departamento
        and colaborador.departamento.area
    ):

        area = colaborador.departamento.area.nombre

    fecha = (
        str(evaluacion.fecha_evaluacion)
        if evaluacion.fecha_evaluacion
        else "—"
    )

    evaluador = (
        evaluacion.evaluador
        if evaluacion.evaluador
        else "—"
    )

    rol_evaluador = (
        evaluacion.rol_evaluador
        if evaluacion.rol_evaluador
        else "—"
    )

    folio = (
        evaluacion.folio
        if evaluacion.folio
        else f"EVAL-{evaluacion.id:06d}"
    )

    # ========================================================
    # CREAR PDF EN MEMORIA
    # ========================================================

    memoria = io.BytesIO()

    documento = SimpleDocTemplate(
        memoria,
        pagesize=letter,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm
    )

    estilos = getSampleStyleSheet()

    titulo = ParagraphStyle(
        "TituloEvaluacion",
        parent=estilos["Title"],
        alignment=TA_CENTER,
        fontSize=17,
        leading=21,
        spaceAfter=10
    )

    subtitulo = ParagraphStyle(
        "SubtituloEvaluacion",
        parent=estilos["Heading2"],
        fontSize=11,
        leading=14,
        spaceBefore=8,
        spaceAfter=6
    )

    normal = ParagraphStyle(
        "NormalEvaluacion",
        parent=estilos["Normal"],
        fontSize=9,
        leading=12
    )

    centrado = ParagraphStyle(
        "CentradoEvaluacion",
        parent=normal,
        alignment=TA_CENTER
    )

    elementos = []

    # ========================================================
    # ENCABEZADO
    # ========================================================

    elementos.append(
        Paragraph(
            "EVALUACIÓN ILUO",
            titulo
        )
    )

    elementos.append(
        Paragraph(
            "EVIDENCIA DOCUMENTAL",
            subtitulo
        )
    )

    elementos.append(
        Paragraph(
            f"<b>Folio:</b> {folio}",
            normal
        )
    )

    elementos.append(
        Spacer(
            1,
            0.25 * cm
        )
    )

    # ========================================================
    # DATOS DEL COLABORADOR
    # ========================================================

    elementos.append(
        Paragraph(
            "DATOS DE LA EVALUACIÓN",
            subtitulo
        )
    )

    datos = [
        [
            Paragraph("<b>Colaborador</b>", normal),
            Paragraph(nombre_colaborador, normal)
        ],
        [
            Paragraph("<b>Puesto</b>", normal),
            Paragraph(puesto, normal)
        ],
        [
            Paragraph("<b>Departamento</b>", normal),
            Paragraph(departamento, normal)
        ],
        [
            Paragraph("<b>Área</b>", normal),
            Paragraph(area, normal)
        ],
        [
            Paragraph("<b>Fecha</b>", normal),
            Paragraph(fecha, normal)
        ],
        [
            Paragraph("<b>Evaluador</b>", normal),
            Paragraph(evaluador, normal)
        ],
        [
            Paragraph("<b>Rol del evaluador</b>", normal),
            Paragraph(rol_evaluador, normal)
        ]
    ]

    tabla_datos = Table(
        datos,
        colWidths=[
            5 * cm,
            12 * cm
        ]
    )

    tabla_datos.setStyle(
        TableStyle([
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),
            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.whitesmoke
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                6
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                6
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5
            )
        ])
    )

    elementos.append(
        tabla_datos
    )

    elementos.append(
        Spacer(
            1,
            0.35 * cm
        )
    )

    # ========================================================
    # HABILIDADES
    # ========================================================

    elementos.append(
        Paragraph(
            "RESULTADOS DE LA EVALUACIÓN",
            subtitulo
        )
    )

    filas = [
        [
            Paragraph("<b>Habilidad</b>", normal),
            Paragraph("<b>Nivel ILUO</b>", centrado)
        ]
    ]

    for registro in evaluaciones:

        habilidad = (
            registro.habilidad.nombre
            if registro.habilidad
            else "Sin habilidad"
        )

        filas.append(
            [
                Paragraph(
                    habilidad,
                    normal
                ),
                Paragraph(
                    registro.nivel,
                    centrado
                )
            ]
        )

    tabla_habilidades = Table(
        filas,
        colWidths=[
            12 * cm,
            5 * cm
        ],
        repeatRows=1
    )

    tabla_habilidades.setStyle(
        TableStyle([
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.whitesmoke
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),
            (
                "ALIGN",
                (1, 1),
                (1, -1),
                "CENTER"
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5
            )
        ])
    )

    elementos.append(
        tabla_habilidades
    )

    elementos.append(
        Spacer(
            1,
            0.35 * cm
        )
    )

    # ========================================================
    # COMENTARIO DE LA EVALUACIÓN
    # ========================================================

    comentario_general = (
        evaluacion.comentario
        if evaluacion.comentario
        else "Sin comentarios."
    )

    elementos.append(
        Paragraph(
            "COMENTARIOS",
            subtitulo
        )
    )

    elementos.append(
        Paragraph(
            comentario_general.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;"),
            normal
        )
    )

    elementos.append(
        Spacer(
            1,
            0.35 * cm
        )
    )

    # ========================================================
    # ESTADO DOCUMENTAL
    # ========================================================

    elementos.append(
        Paragraph(
            "VALIDACIÓN DOCUMENTAL",
            subtitulo
        )
    )

    # ========================================================
    # FIRMA DEL COLABORADOR
    # ========================================================

    if evaluacion.firma_archivo:

        ruta_firma = os.path.join(
            app.root_path,
            "static",
            evaluacion.firma_archivo
        )

        if os.path.exists(ruta_firma):

            firma_pdf = Image(
                ruta_firma,
                width=5 * cm,
                height=2.2 * cm
            )

        else:

            firma_pdf = Paragraph(
                "Firma registrada, pero no se encontró el archivo.",
                normal
            )

    else:

        firma_pdf = Paragraph(
            "Pendiente",
            normal
        )

    confirmacion = (
        "Confirmada"
        if evaluacion.confirmacion_colaborador
        else "Pendiente"
    )

    validacion = [
        [
            Paragraph("<b>Firma</b>", normal),
            firma_pdf
        ],
        [
            Paragraph("<b>Confirmación del colaborador</b>", normal),
            Paragraph(confirmacion, normal)
        ]
    ]

    tabla_validacion = Table(
        validacion,
        colWidths=[
            7 * cm,
            10 * cm
        ]
    )

    tabla_validacion.setStyle(
        TableStyle([
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.whitesmoke
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            )
        ])
    )

    elementos.append(
        tabla_validacion
    )

    elementos.append(
        Spacer(
            1,
            0.5 * cm
        )
    )

    # ========================================================
    # PIE DOCUMENTAL
    # ========================================================

    elementos.append(
        Paragraph(
            f"Documento generado por el Sistema de Matriz ILUO. "
            f"Folio: <b>{folio}</b>",
            normal
        )
    )

    elementos.append(
        Spacer(
            1,
            0.15 * cm
        )
    )

    elementos.append(
        Paragraph(
            "Este documento constituye evidencia documental "
            "de la evaluación registrada en el sistema.",
            normal
        )
    )

    documento.build(
        elementos
    )

    memoria.seek(0)

    nombre_archivo = (
        f"Evaluacion_{folio}.pdf"
    )

    return send_file(
        memoria,
        mimetype="application/pdf",
        as_attachment=False,
        download_name=nombre_archivo
    )



if __name__ == '__main__':
    app.run(debug=True)

























