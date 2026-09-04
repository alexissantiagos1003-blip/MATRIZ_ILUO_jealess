from datetime import date

from flask import Flask, render_template, request, redirect, url_for, send_from_directory, send_file, session
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename
import uuid
app = Flask(__name__)

app.config["SECRET_KEY"] = "c22afc3d9b2a9ac6f3c7a6ee8f845725ae2665a1e697cb98f1205da561a3cd51"


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

    area_id = db.Column(
        db.Integer,
        db.ForeignKey("area.id"),
        nullable=True
    )
    departamento_id = db.Column(
        db.Integer,
        db.ForeignKey("departamento.id"),
        nullable=True
    )

    area = db.relationship(
        "Area",
        backref="puestos"
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



# =========================================================
# TABLA: RELACIONES JERARQUICAS / MATRICIALES DE PUESTOS
# =========================================================

class PuestoRelacion(db.Model):

    __tablename__ = "puesto_relacion"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    puesto_padre_id = db.Column(
        db.Integer,
        db.ForeignKey("puesto.id"),
        nullable=False
    )

    puesto_hijo_id = db.Column(
        db.Integer,
        db.ForeignKey("puesto.id"),
        nullable=False
    )

    tipo_relacion = db.Column(
        db.String(30),
        nullable=False,
        default="directa"
    )

    puesto_padre = db.relationship(
        "Puesto",
        foreign_keys=[puesto_padre_id],
        backref="relaciones_como_padre"
    )

    puesto_hijo = db.relationship(
        "Puesto",
        foreign_keys=[puesto_hijo_id],
        backref="relaciones_como_hijo"
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

    nivel_requerido = db.Column(
        db.String(1),
        nullable=True,
        default="O"
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


# =========================================================
# API RELACIONES MULTIPLES DE PUESTOS
# =========================================================


# =========================================================
# DOMINIO Y BRECHAS
# =========================================================


# ============================================================
# USUARIOS Y AUTENTICACION
# ============================================================

class Usuario(db.Model):

    __tablename__ = "usuario"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(80),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    rol = db.Column(
        db.String(50),
        nullable=False,
        default="colaborador"
    )

    colaborador_id = db.Column(
        db.Integer,
        db.ForeignKey("colaborador.id"),
        nullable=True
    )

    activo = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    colaborador = db.relationship(
        "Colaborador",
        foreign_keys=[colaborador_id],
        backref=db.backref(
            "usuario_cuenta",
            uselist=False
        )
    )



# ============================================================
# LOGIN MATRIZ ILUO
# ============================================================

from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)



# ============================================================
# CATALOGO DE ROLES
# ============================================================

class Rol(db.Model):

    __tablename__ = "rol"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nombre = db.Column(
        db.String(80),
        unique=True,
        nullable=False
    )

    descripcion = db.Column(
        db.Text,
        nullable=True
    )

    activo = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )


# ============================================================
# CATALOGO DE PERMISOS
# ============================================================

class Permiso(db.Model):

    __tablename__ = "permiso"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    codigo = db.Column(
        db.String(80),
        unique=True,
        nullable=False
    )

    nombre = db.Column(
        db.String(120),
        nullable=False
    )

    descripcion = db.Column(
        db.Text,
        nullable=True
    )

    activo = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )


# ============================================================
# ASIGNACION DE PERMISOS A ROLES
# ============================================================

class RolPermiso(db.Model):

    __tablename__ = "rol_permiso"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    rol_id = db.Column(
        db.Integer,
        db.ForeignKey("rol.id"),
        nullable=False
    )

    permiso_id = db.Column(
        db.Integer,
        db.ForeignKey("permiso.id"),
        nullable=False
    )

    permitido = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    rol = db.relationship(
        "Rol",
        foreign_keys=[rol_id],
        backref="asignaciones_permisos"
    )

    permiso = db.relationship(
        "Permiso",
        foreign_keys=[permiso_id],
        backref="asignaciones_roles"
    )


# ============================================================
# ADMINISTRACION DE ROLES Y PERMISOS
# ============================================================


# ============================================================

# ============================================================
# MOTOR CENTRAL DE AUTORIZACION ILUO
# ============================================================

def usuario_actual():

    usuario_id = session.get(
        "usuario_id"
    )

    if not usuario_id:

        return None


    return (
        Usuario.query
        .filter_by(
            id=usuario_id,
            activo=True
        )
        .first()
    )


def tiene_permiso(
    usuario,
    codigo_permiso
):

    if not usuario:

        return False


    if not usuario.activo:

        return False


    rol = (
        Rol.query
        .filter_by(
            nombre=usuario.rol,
            activo=True
        )
        .first()
    )


    if not rol:

        return False


    permiso = (
        Permiso.query
        .filter_by(
            codigo=codigo_permiso,
            activo=True
        )
        .first()
    )


    if not permiso:

        return False


    asignacion = (
        RolPermiso.query
        .filter_by(
            rol_id=rol.id,
            permiso_id=permiso.id
        )
        .first()
    )


    if not asignacion:

        return False


    return bool(
        asignacion.permitido
    )


def misma_area(
    usuario,
    puesto
):

    if not usuario:

        return False


    if not usuario.colaborador:

        return False


    if not puesto:

        return False


    colaborador_actual = usuario.colaborador


    departamento_usuario = (
        colaborador_actual.departamento
    )


    if not departamento_usuario:

        return False


    area_usuario = (
        departamento_usuario.area
    )


    if not area_usuario:

        return False


    area_puesto = (
        puesto.area
    )


    if not area_puesto:

        return False


    return (
        area_usuario.id
        ==
        area_puesto.id
    )


def puede_actuar_sobre_puesto(
    usuario,
    puesto
):

    if not usuario:

        return False


    if not puesto:

        return False


    # --------------------------------------------------------
    # ADMINISTRADOR
    # --------------------------------------------------------

    if usuario.rol == "administrador":

        return True


    # --------------------------------------------------------
    # GERENTE DE OPERACIONES
    # Toda el AREA OPERACIONES
    # --------------------------------------------------------

    if usuario.rol == "gerente_operaciones":

        if not puesto.area:

            return False


        return (
            puesto.area.nombre
            .strip()
            .lower()
            ==
            "operaciones"
        )


    # --------------------------------------------------------
    # GERENTE DE AREA
    # Toda su area
    # --------------------------------------------------------

    if usuario.rol == "gerente_area":

        return misma_area(
            usuario,
            puesto
        )


    # --------------------------------------------------------
    # SUPERVISOR
    # Solo puestos con relacion autorizada
    # --------------------------------------------------------

    if usuario.rol == "supervisor":

        if not usuario.colaborador:

            return False


        puesto_supervisor = (
            usuario.colaborador.puesto
        )


        if not puesto_supervisor:

            return False


        if (
            puesto_supervisor.id
            ==
            puesto.id
        ):

            return False


        relacion = (
            PuestoRelacion.query
            .filter_by(
                puesto_padre_id=puesto_supervisor.id,
                puesto_hijo_id=puesto.id
            )
            .first()
        )


        return bool(
            relacion
        )


    # --------------------------------------------------------
    # RH
    # Puede actuar sobre el ámbito empresarial.
    # Los permisos "editar" se controlan aparte.
    # --------------------------------------------------------

    if usuario.rol == "rh":

        return True


    # --------------------------------------------------------
    # COLABORADOR
    # Solo sobre su propio puesto
    # --------------------------------------------------------

    if usuario.rol == "colaborador":

        if not usuario.colaborador:

            return False


        return (
            usuario.colaborador.puesto_id
            ==
            puesto.id
        )


    return False


def puede_actuar_sobre_colaborador(
    usuario,
    colaborador
):

    if not usuario:

        return False


    if not colaborador:

        return False


    # --------------------------------------------------------
    # ADMINISTRADOR
    # --------------------------------------------------------

    if usuario.rol == "administrador":

        return True


    # --------------------------------------------------------
    # RH
    # --------------------------------------------------------

    if usuario.rol == "rh":

        return True


    # --------------------------------------------------------
    # COLABORADOR
    # --------------------------------------------------------

    if usuario.rol == "colaborador":

        return (
            usuario.colaborador_id
            ==
            colaborador.id
        )


    # --------------------------------------------------------
    # GERENTES / SUPERVISORES
    # --------------------------------------------------------

    puesto_colaborador = (
        colaborador.puesto
    )


    if not puesto_colaborador:

        return False


    return puede_actuar_sobre_puesto(
        usuario,
        puesto_colaborador
    )


def autorizado(
    usuario,
    permiso,
    puesto=None,
    colaborador=None
):

    if not tiene_permiso(
        usuario,
        permiso
    ):

        return False


    if colaborador is not None:

        return puede_actuar_sobre_colaborador(
            usuario,
            colaborador
        )


    if puesto is not None:

        return puede_actuar_sobre_puesto(
            usuario,
            puesto
        )


    return True



# ============================================================
# PERFIL DE USUARIO
# ============================================================


# ============================================================
# CAMBIAR CONTRASEÑA
# ============================================================


# ============================================================
# CONTEXTO GLOBAL DEL USUARIO ILUO
# ============================================================

@app.context_processor
def contexto_usuario():

    return {
        "usuario_sesion": usuario_actual()
    }



# ============================================================
# PROTECCION DE RESPUESTAS AUTENTICADAS
# ============================================================

@app.after_request
def proteger_respuesta_autenticada(respuesta):

    if usuario_actual():

        respuesta.headers["Cache-Control"] = (
            "no-store, no-cache, must-revalidate, "
            "max-age=0, private"
        )

        respuesta.headers["Pragma"] = "no-cache"

        respuesta.headers["Expires"] = "0"


    return respuesta


@app.route(
    "/cambiar-contrasena",
    methods=["GET", "POST"]
)
def cambiar_contrasena():

    usuario = usuario_actual()


    if not usuario:

        return redirect(
            url_for("login")
        )


    if request.method == "POST":

        password_actual = (
            request.form.get(
                "password_actual",
                ""
            )
        )


        password_nueva = (
            request.form.get(
                "password_nueva",
                ""
            )
        )


        password_confirmacion = (
            request.form.get(
                "password_confirmacion",
                ""
            )
        )


        # ----------------------------------------------------
        # VERIFICAR CONTRASEÑA ACTUAL
        # ----------------------------------------------------

        if not check_password_hash(
            usuario.password_hash,
            password_actual
        ):

            return render_template(
                "cambiar_contrasena.html",
                usuario=usuario,
                error="La contraseña actual no es correcta."
            )


        # ----------------------------------------------------
        # VALIDAR NUEVA CONTRASEÑA
        # ----------------------------------------------------

        if not password_nueva:

            return render_template(
                "cambiar_contrasena.html",
                usuario=usuario,
                error="La nueva contraseña no puede estar vacía."
            )


        if len(password_nueva) < 8:

            return render_template(
                "cambiar_contrasena.html",
                usuario=usuario,
                error="La nueva contraseña debe tener al menos 8 caracteres."
            )


        if password_nueva != password_confirmacion:

            return render_template(
                "cambiar_contrasena.html",
                usuario=usuario,
                error="Las contraseñas nuevas no coinciden."
            )


        if password_nueva == password_actual:

            return render_template(
                "cambiar_contrasena.html",
                usuario=usuario,
                error="La nueva contraseña debe ser diferente a la actual."
            )


        # ----------------------------------------------------
        # GUARDAR
        # ----------------------------------------------------

        usuario.password_hash = (
            generate_password_hash(
                password_nueva
            )
        )


        db.session.commit()


        return render_template(
            "cambiar_contrasena.html",
            usuario=usuario,
            exito="Contraseña actualizada correctamente."
        )


    return render_template(
        "cambiar_contrasena.html",
        usuario=usuario
    )



@app.route("/perfil")
def perfil():

    usuario = usuario_actual()


    if not usuario:

        return redirect(
            url_for("login")
        )


    colaborador = usuario.colaborador


    puesto = None
    departamento = None
    area = None


    if colaborador:

        puesto = (
            colaborador.puesto
        )


        departamento = (
            colaborador.departamento
        )


        if departamento:

            area = (
                departamento.area
            )


    return render_template(
        "perfil.html",
        usuario=usuario,
        colaborador=colaborador,
        puesto=puesto,
        departamento=departamento,
        area=area
    )


@app.route(
    "/roles-permisos",
    methods=["GET", "POST"]
)
def roles_permisos():

    roles = (
        Rol.query
        .filter_by(
            activo=True
        )
        .order_by(
            Rol.id
        )
        .all()
    )


    permisos = (
        Permiso.query
        .filter_by(
            activo=True
        )
        .order_by(
            Permiso.id
        )
        .all()
    )


    if request.method == "POST":

        for rol in roles:

            for permiso in permisos:

                asignacion = (
                    RolPermiso.query
                    .filter_by(
                        rol_id=rol.id,
                        permiso_id=permiso.id
                    )
                    .first()
                )


                if not asignacion:

                    asignacion = RolPermiso(
                        rol_id=rol.id,
                        permiso_id=permiso.id,
                        permitido=False
                    )

                    db.session.add(
                        asignacion
                    )


                nombre_checkbox = (
                    f"permiso_{rol.id}_{permiso.id}"
                )


                asignacion.permitido = (
                    nombre_checkbox
                    in request.form
                )


        db.session.commit()


        return redirect(
            url_for(
                "roles_permisos"
            )
        )


    matriz = {}


    for rol in roles:

        matriz[rol.id] = {}


        for permiso in permisos:

            asignacion = (
                RolPermiso.query
                .filter_by(
                    rol_id=rol.id,
                    permiso_id=permiso.id
                )
                .first()
            )


            matriz[rol.id][permiso.id] = (
                asignacion.permitido
                if asignacion
                else False
            )


    return render_template(
        "roles_permisos.html",
        roles=roles,
        permisos=permisos,
        matriz=matriz
    )


@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        username = (
            request.form.get(
                "username",
                ""
            )
            or ""
        ).strip()

        password = (
            request.form.get(
                "password",
                ""
            )
            or ""
        )


        usuario = (
            Usuario.query
            .filter_by(
                username=username,
                activo=True
            )
            .first()
        )


        if (
            usuario
            and check_password_hash(
                usuario.password_hash,
                password
            )
        ):

            session["usuario_id"] = (
                usuario.id
            )

            return redirect(
                url_for("inicio_principal")
            )


        return render_template(
            "login.html",
            error="Usuario o contraseña incorrectos."
        )


    return render_template(
        "login.html"
    )


@app.route(
    "/logout"
)
def logout():

    session.pop(
        "usuario_id",
        None
    )

    return redirect(
        url_for("login")
    )


@app.route("/dominio-brechas")
def dominio_brechas():

    # ---------------------------------------------------------
    # FILTROS
    # ---------------------------------------------------------

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

    colaborador_id = request.args.get(
        "colaborador_id",
        type=int
    )


    # ---------------------------------------------------------
    # CATALOGOS
    # ---------------------------------------------------------

    areas = (
        Area.query
        .order_by(
            Area.nombre
        )
        .all()
    )

    departamentos = (
        Departamento.query
        .order_by(
            Departamento.nombre
        )
        .all()
    )

    puestos = (
        Puesto.query
        .order_by(
            Puesto.nombre
        )
        .all()
    )


    # ---------------------------------------------------------
    # FILTRAR DEPARTAMENTOS POR AREA
    # ---------------------------------------------------------

    departamentos_visibles = departamentos

    if area_id:

        departamentos_visibles = [
            departamento

            for departamento
            in departamentos

            if (
                departamento.area_id
                ==
                area_id
            )
        ]


    # ---------------------------------------------------------
    # FILTRAR PUESTOS
    # ---------------------------------------------------------

    puestos_visibles = puestos


    if departamento_id:

        puestos_visibles = [
            puesto

            for puesto
            in puestos

            if (
                puesto.departamento_id
                ==
                departamento_id
            )
        ]

    elif area_id:

        puestos_visibles = [
            puesto

            for puesto
            in puestos

            if (
                puesto.area
                and
                puesto.area.id
                ==
                area_id
            )
        ]


    # ---------------------------------------------------------
    # COLABORADORES
    # ---------------------------------------------------------

    colaboradores = (
        Colaborador.query
        .filter_by(
            activo=1
        )
        .order_by(
            Colaborador.nombre
        )
        .all()
    )


    # ---------------------------------------------------------
    # FILTRAR COLABORADORES POR AREA
    # ---------------------------------------------------------

    if area_id:

        colaboradores = [

            colaborador

            for colaborador
            in colaboradores

            if (
                colaborador.puesto
                and
                colaborador.puesto.area
                and
                colaborador.puesto.area.id
                ==
                area_id
            )

        ]


    # ---------------------------------------------------------
    # FILTRAR COLABORADORES POR DEPARTAMENTO
    # ---------------------------------------------------------

    if departamento_id:

        colaboradores = [

            colaborador

            for colaborador
            in colaboradores

            if (
                colaborador.puesto
                and
                colaborador.puesto.departamento_id
                ==
                departamento_id
            )

        ]


    # ---------------------------------------------------------
    # FILTRAR COLABORADORES POR PUESTO
    # ---------------------------------------------------------

    if puesto_id:

        colaboradores = [

            colaborador

            for colaborador
            in colaboradores

            if (
                colaborador.puesto_id
                ==
                puesto_id
            )

        ]


    # ---------------------------------------------------------
    # COLABORADOR SELECCIONADO
    # ---------------------------------------------------------

    colaborador_actual = None

    matriz_brechas = []

    resumen = {

        "total": 0,

        "sin_brecha": 0,

        "brechas": 0,

        "pendientes": 0,

        "cumplimiento": 0

    }


    if colaborador_id:

        colaborador_actual = (
            db.session.get(
                Colaborador,
                colaborador_id
            )
        )


    # ---------------------------------------------------------
    # MATRIZ
    # ---------------------------------------------------------

    if colaborador_actual:

        resultado = (
            calcular_brechas_colaborador(
                colaborador_actual
            )
        )


        resumen = {

            "total":
                resultado[
                    "total_habilidades"
                ],

            "sin_brecha":
                resultado[
                    "sin_brecha"
                ],

            "brechas":
                resultado[
                    "brechas"
                ],

            "pendientes":
                resultado[
                    "pendientes"
                ],

            "cumplimiento":
                resultado[
                    "porcentaje_cumplimiento"
                ]

        }


        for detalle in (
            resultado["detalle"]
        ):


            cursos = []


            try:

                cursos = (
                    Curso.query
                    .filter(
                        Curso.habilidad_id
                        ==
                        detalle[
                            "habilidad_id"
                        ]
                    )
                    .order_by(
                        Curso.nombre
                    )
                    .all()
                )

            except Exception:

                cursos = []


            matriz_brechas.append({

                "habilidad":
                    detalle[
                        "habilidad"
                    ],

                "habilidad_id":
                    detalle[
                        "habilidad_id"
                    ],

                "requerido":
                    detalle[
                        "nivel_requerido"
                    ],

                "actual":
                    detalle[
                        "nivel_actual"
                    ],

                "diferencia":
                    detalle[
                        "diferencia"
                    ],

                "estado":
                    detalle[
                        "estado"
                    ],

                "cursos":
                    cursos

            })


    # ---------------------------------------------------------
    # RENDER
    # ---------------------------------------------------------

    return render_template(

        "dominio_brechas.html",

        areas=areas,

        departamentos=
            departamentos_visibles,

        departamentos_todos=
            departamentos,

        puestos=
            puestos_visibles,

        puestos_todos=
            puestos,

        colaboradores=
            colaboradores,

        area_id=
            area_id,

        departamento_id=
            departamento_id,

        puesto_id=
            puesto_id,

        colaborador_id=
            colaborador_id,

        colaborador_actual=
            colaborador_actual,

        matriz_brechas=
            matriz_brechas,

        resumen=
            resumen

    )


@app.route(
    "/puestos/<int:puesto_id>/relaciones",
    methods=["POST"]
)
def agregar_relacion_puesto(puesto_id):

    puesto_hijo = Puesto.query.get_or_404(
        puesto_id
    )

    padre_id = request.form.get(
        "puesto_padre_id",
        type=int
    )

    tipo_relacion = (
        request.form.get(
            "tipo_relacion",
            "directa"
        )
        or "directa"
    ).strip().lower()

    if not padre_id:
        return redirect(
            url_for("puestos")
        )

    if padre_id == puesto_id:

        return redirect(
            url_for("puestos")
        )

    if tipo_relacion not in {
        "directa",
        "matricial"
    }:

        tipo_relacion = "directa"


    puesto_padre = (
        Puesto.query.get(padre_id)
    )


    if not puesto_padre:

        return redirect(
            url_for("puestos")
        )


    existente = (
        PuestoRelacion.query
        .filter_by(
            puesto_padre_id=padre_id,
            puesto_hijo_id=puesto_id
        )
        .first()
    )


    if existente:

        existente.tipo_relacion = (
            tipo_relacion
        )

    else:

        db.session.add(
            PuestoRelacion(
                puesto_padre_id=padre_id,
                puesto_hijo_id=puesto_id,
                tipo_relacion=tipo_relacion
            )
        )


    db.session.commit()

    return redirect(
        url_for("puestos")
    )


@app.route(
    "/puestos/<int:puesto_id>/relaciones/<int:relacion_id>/eliminar",
    methods=["POST"]
)
def eliminar_relacion_puesto(
    puesto_id,
    relacion_id
):

    relacion = (
        PuestoRelacion.query
        .filter_by(
            id=relacion_id,
            puesto_hijo_id=puesto_id
        )
        .first()
    )


    if not relacion:

        return redirect(
            url_for("puestos")
        )


    db.session.delete(
        relacion
    )

    db.session.commit()

    return redirect(
        url_for("puestos")
    )


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


# ============================================================
# MOTOR DE CALCULO ILUO PARA DASHBOARD
# ============================================================

VALORES_ILUO = {
    "I": 25,
    "L": 50,
    "U": 75,
    "O": 100
}


def obtener_estado_dominio(porcentaje):

    if porcentaje < 70:
        return {
            "estado": "Requiere atención",
            "color": "rojo"
        }

    elif porcentaje < 85:
        return {
            "estado": "En desarrollo",
            "color": "amarillo"
        }

    else:
        return {
            "estado": "Buen dominio",
            "color": "verde"
        }



# =========================================================
# MOTOR CENTRAL DE BRECHAS ILUO
# =========================================================

ORDEN_ILUO = {
    "I": 1,
    "L": 2,
    "U": 3,
    "O": 4
}


def calcular_brechas_colaborador(
    colaborador
):

    puesto = colaborador.puesto

    resultado = {

        "colaborador": colaborador,

        "puesto": puesto,

        "total_habilidades": 0,

        "sin_brecha": 0,

        "brechas": 0,

        "pendientes": 0,

        "porcentaje_cumplimiento": 0,

        "detalle": []

    }


    if not puesto:

        return resultado


    requeridas = (
        PuestoHabilidad.query
        .filter_by(
            puesto_id=puesto.id
        )
        .order_by(
            PuestoHabilidad.habilidad_id
        )
        .all()
    )


    resultado["total_habilidades"] = (
        len(requeridas)
    )


    if not requeridas:

        return resultado


    for requerida in requeridas:

        habilidad = (
            requerida.habilidad
        )


        nivel_requerido = (
            requerida.nivel_requerido
            or "O"
        )


        evaluacion = (
            Evaluacion.query
            .filter_by(
                colaborador_id=colaborador.id,
                habilidad_id=habilidad.id
            )
            .order_by(
                Evaluacion.fecha_evaluacion.desc(),
                Evaluacion.id.desc()
            )
            .first()
        )


        nivel_actual = (
            evaluacion.nivel
            if evaluacion
            else None
        )


        valor_requerido = (
            ORDEN_ILUO.get(
                nivel_requerido
            )
        )


        valor_actual = (
            ORDEN_ILUO.get(
                nivel_actual
            )
            if nivel_actual
            else None
        )


        # ----------------------------------------------------
        # SIN EVALUACION
        # ----------------------------------------------------

        if valor_actual is None:

            estado = "pendiente"

            diferencia = None

            resultado["pendientes"] += 1


        else:

            diferencia = (
                valor_requerido
                -
                valor_actual
            )


            if diferencia <= 0:

                estado = "sin_brecha"

                resultado["sin_brecha"] += 1

            else:

                estado = "brecha"

                resultado["brechas"] += 1


        resultado["detalle"].append({

            "habilidad":
                habilidad,

            "habilidad_id":
                habilidad.id,

            "nivel_requerido":
                nivel_requerido,

            "nivel_actual":
                nivel_actual,

            "valor_requerido":
                valor_requerido,

            "valor_actual":
                valor_actual,

            "diferencia":
                diferencia,

            "estado":
                estado,

            "evaluacion":
                evaluacion

        })


    total = (
        resultado["total_habilidades"]
    )


    if total > 0:

        resultado[
            "porcentaje_cumplimiento"
        ] = round(
            (
                resultado["sin_brecha"]
                /
                total
            ) * 100,
            1
        )


    return resultado


def calcular_dominio_evaluaciones(evaluaciones):

    if not evaluaciones:

        return {
            "porcentaje": 0,
            "estado": "Sin evaluaciones",
            "color": "gris",
            "total": 0,
            "niveles": {
                "I": 0,
                "L": 0,
                "U": 0,
                "O": 0
            }
        }

    niveles = {
        "I": 0,
        "L": 0,
        "U": 0,
        "O": 0
    }

    total_valido = 0
    suma = 0

    for evaluacion in evaluaciones:

        nivel = evaluacion.nivel

        if nivel in VALORES_ILUO:

            niveles[nivel] += 1

            suma += VALORES_ILUO[nivel]

            total_valido += 1

    if total_valido == 0:

        return {
            "porcentaje": 0,
            "estado": "Sin evaluaciones",
            "color": "gris",
            "total": 0,
            "niveles": niveles
        }

    porcentaje = round(
        suma / total_valido,
        1
    )

    estado = obtener_estado_dominio(porcentaje)

    return {
        "porcentaje": porcentaje,
        "estado": estado["estado"],
        "color": estado["color"],
        "total": total_valido,
        "niveles": niveles
    }


# INICIO
# =========================

# ============================================================
# PAGINA DE INICIO
# ============================================================

@app.route("/")
def inicio_principal():

    colaboradores = Colaborador.query.count()
    habilidades = Habilidad.query.count()
    evaluaciones = Evaluacion.query.count()

    return render_template(
        "index.html",
        colaboradores=colaboradores,
        habilidades=habilidades,
        evaluaciones=evaluaciones
    )


# ============================================================
# DASHBOARD
# ============================================================
# ============================================================
# COLABORADORES
# ============================================================

@app.route("/colaboradores")
def colaboradores():

    lista_colaboradores = (
        Colaborador.query
        .filter_by(activo=1)
        .order_by(Colaborador.nombre)
        .all()
    )

    puestos = (
        Puesto.query
        .order_by(Puesto.nombre)
        .all()
    )

    departamentos = (
        Departamento.query
        .order_by(Departamento.nombre)
        .all()
    )

    return render_template(
        "colaboradores.html",
        colaboradores=lista_colaboradores,
        puestos=puestos,
        departamentos=departamentos
    )

@app.route("/dashboard")
def dashboard():

    # ========================================================
    # FILTROS
    # ========================================================

    area_id = request.args.get("area_id", type=int)
    departamento_id = request.args.get("departamento_id", type=int)

    areas = Area.query.order_by(
        Area.nombre
    ).all()

    # Si no se selecciona area, usar la primera disponible
    if area_id is None and areas:
        area_id = areas[0].id

    area_seleccionada = None

    if area_id:
        area_seleccionada = Area.query.get(area_id)

    # ========================================================
    # DEPARTAMENTOS DE LA AREA
    # ========================================================

    if area_seleccionada:

        departamentos = Departamento.query.filter_by(
            area_id=area_seleccionada.id
        ).order_by(
            Departamento.nombre
        ).all()

    else:

        departamentos = []

    departamento_seleccionado = None

    if departamento_id:

        departamento_seleccionado = Departamento.query.filter_by(
            id=departamento_id,
            area_id=area_id
        ).first()

    # ========================================================
    # COLABORADORES ACTIVOS
    # ========================================================

    colaboradores_base = Colaborador.query.filter_by(
        activo=True
    ).all()

    colaboradores_filtrados = []

    for colaborador in colaboradores_base:

        departamento = colaborador.departamento

        if not departamento:
            continue

        if area_seleccionada:

            if departamento.area_id != area_seleccionada.id:
                continue

        if departamento_seleccionado:

            if colaborador.departamento_id != departamento_seleccionado.id:
                continue

        colaboradores_filtrados.append(
            colaborador
        )

    # ========================================================
    # EVALUACIONES
    # ========================================================

    evaluaciones = Evaluacion.query.all()

    colaborador_ids = {
        colaborador.id
        for colaborador in colaboradores_filtrados
    }

    evaluaciones_filtradas = [

        evaluacion

        for evaluacion in evaluaciones

        if evaluacion.colaborador_id in colaborador_ids

        and evaluacion.nivel in VALORES_ILUO
    ]

    # ========================================================
    # MOTOR ILUO
    # ========================================================

    resumen = calcular_dominio_evaluaciones(
        evaluaciones_filtradas
    )

    porcentaje = resumen["porcentaje"]
    estado = resumen["estado"]
    color = resumen["color"]

    niveles = resumen["niveles"]

    total_evaluaciones = resumen["total"]

    # ========================================================
    # DISTRIBUCION PORCENTUAL
    # ========================================================

    niveles_porcentaje = {
        "I": 0,
        "L": 0,
        "U": 0,
        "O": 0
    }

    if total_evaluaciones > 0:

        for nivel in niveles_porcentaje:

            niveles_porcentaje[nivel] = round(
                niveles[nivel]
                / total_evaluaciones
                * 100,
                1
            )

    # ========================================================
    # MAPAS DE DATOS
    # ========================================================

    habilidades = Habilidad.query.all()

    habilidades_map = {
        habilidad.id: habilidad.nombre
        for habilidad in habilidades
    }

    colaboradores_map = {
        colaborador.id: colaborador
        for colaborador in colaboradores_base
    }

    # ========================================================
    # NECESIDADES DE CAPACITACION
    # I + L
    # ========================================================

    necesidades = {}

    for evaluacion in evaluaciones_filtradas:

        if evaluacion.nivel not in ("I", "L"):
            continue

        habilidad_id = evaluacion.habilidad_id

        nombre = habilidades_map.get(
            habilidad_id,
            "Habilidad sin nombre"
        )

        if nombre not in necesidades:

            necesidades[nombre] = {
                "nombre": nombre,
                "total": 0,
                "I": 0,
                "L": 0,
                "departamentos": set()
            }

        necesidades[nombre]["total"] += 1

        necesidades[nombre][evaluacion.nivel] += 1

        colaborador = colaboradores_map.get(
            evaluacion.colaborador_id
        )

        if colaborador and colaborador.departamento:

            necesidades[nombre]["departamentos"].add(
                colaborador.departamento.nombre
            )

    necesidades_lista = list(
        necesidades.values()
    )

    necesidades_lista.sort(
        key=lambda x: x["total"],
        reverse=True
    )

    # ========================================================
    # FORTALEZAS / ESPECIALIZACION
    # U + O
    # ========================================================

    fortalezas = {}

    for evaluacion in evaluaciones_filtradas:

        if evaluacion.nivel not in ("U", "O"):
            continue

        habilidad_id = evaluacion.habilidad_id

        nombre = habilidades_map.get(
            habilidad_id,
            "Habilidad sin nombre"
        )

        if nombre not in fortalezas:

            fortalezas[nombre] = {
                "nombre": nombre,
                "total": 0,
                "U": 0,
                "O": 0,
                "departamentos": set()
            }

        fortalezas[nombre]["total"] += 1

        fortalezas[nombre][evaluacion.nivel] += 1

        colaborador = colaboradores_map.get(
            evaluacion.colaborador_id
        )

        if colaborador and colaborador.departamento:

            fortalezas[nombre]["departamentos"].add(
                colaborador.departamento.nombre
            )

    fortalezas_lista = list(
        fortalezas.values()
    )

    fortalezas_lista.sort(
        key=lambda x: x["total"],
        reverse=True
    )

    # ========================================================
    # CONVERTIR SET A LIST PARA JINJA
    # ========================================================

    for item in necesidades_lista:

        item["departamentos"] = sorted(
            item["departamentos"]
        )

    for item in fortalezas_lista:

        item["departamentos"] = sorted(
            item["departamentos"]
        )

    # ========================================================
    # NECESIDADES POR DEPARTAMENTO
    # ========================================================

    necesidades_departamentos = {}

    for departamento in departamentos:

        registros = [

            evaluacion

            for evaluacion in evaluaciones

            if evaluacion.nivel in ("I", "L")

            and evaluacion.colaborador_id in {

                colaborador.id

                for colaborador in colaboradores_base

                if colaborador.activo
                and colaborador.departamento_id == departamento.id
            }
        ]

        conteo = {}

        for evaluacion in registros:

            nombre = habilidades_map.get(
                evaluacion.habilidad_id,
                "Habilidad sin nombre"
            )

            conteo[nombre] = conteo.get(
                nombre,
                0
            ) + 1

        lista = [

            {
                "nombre": nombre,
                "total": total
            }

            for nombre, total in conteo.items()
        ]

        lista.sort(
            key=lambda x: x["total"],
            reverse=True
        )

        necesidades_departamentos[
            departamento.id
        ] = lista[:5]

    # ========================================================
    # FORTALEZAS POR DEPARTAMENTO
    # ========================================================

    fortalezas_departamentos = {}

    for departamento in departamentos:

        registros = [

            evaluacion

            for evaluacion in evaluaciones

            if evaluacion.nivel in ("U", "O")

            and evaluacion.colaborador_id in {

                colaborador.id

                for colaborador in colaboradores_base

                if colaborador.activo
                and colaborador.departamento_id == departamento.id
            }
        ]

        conteo = {}

        for evaluacion in registros:

            nombre = habilidades_map.get(
                evaluacion.habilidad_id,
                "Habilidad sin nombre"
            )

            conteo[nombre] = conteo.get(
                nombre,
                0
            ) + 1

        lista = [

            {
                "nombre": nombre,
                "total": total
            }

            for nombre, total in conteo.items()
        ]

        lista.sort(
            key=lambda x: x["total"],
            reverse=True
        )

        fortalezas_departamentos[
            departamento.id
        ] = lista[:5]

    # ========================================================
    # RENDER
    # ========================================================

    return render_template(

        "dashboard.html",

        areas=areas,

        area_seleccionada=area_seleccionada,

        departamentos=departamentos,

        departamento_seleccionado=departamento_seleccionado,

        colaboradores=colaboradores_filtrados,

        habilidades=habilidades,

        evaluaciones=total_evaluaciones,

        niveles=niveles,

        niveles_porcentaje=niveles_porcentaje,

        porcentaje=porcentaje,

        estado=estado,

        color=color,

        necesidades=necesidades_lista,

        fortalezas=fortalezas_lista,

        necesidades_departamentos=necesidades_departamentos,

        fortalezas_departamentos=fortalezas_departamentos
    )


# ========================================================@app.route("/colaboradores")
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
        "numero_empleado",
        ""
    ).strip()

    nombre = request.form.get(
        "nombre",
        ""
    ).strip()

    area_id = request.form.get(
        "area_id",
        type=int
    )

    departamento_id = request.form.get(
        "departamento_id",
        type=int
    )

    puesto_id = request.form.get(
        "puesto_id",
        type=int
    )

    # ========================================================
    # VALIDACIONES
    # ========================================================

    if not numero_empleado:

        return (
            "El número de empleado es obligatorio.",
            400
        )

    if not nombre:

        return (
            "El nombre del colaborador es obligatorio.",
            400
        )

    if not area_id:

        return (
            "El área es obligatoria.",
            400
        )

    if not departamento_id:

        return (
            "El departamento es obligatorio.",
            400
        )

    if not puesto_id:

        return (
            "El puesto es obligatorio.",
            400
        )

    # ========================================================
    # VALIDAR AREA
    # ========================================================

    area = Area.query.filter_by(
        id=area_id
    ).first()

    if not area:

        return (
            "El área seleccionada no existe.",
            400
        )

    # ========================================================
    # VALIDAR DEPARTAMENTO
    # ========================================================

    departamento = Departamento.query.filter_by(
        id=departamento_id
    ).first()

    if not departamento:

        return (
            "El departamento seleccionado no existe.",
            400
        )

    if departamento.area_id != area.id:

        return (
            "El departamento no pertenece al área seleccionada.",
            400
        )

    # ========================================================
    # VALIDAR PUESTO
    # ========================================================

    puesto = Puesto.query.filter_by(
        id=puesto_id
    ).first()

    if not puesto:

        return (
            "El puesto seleccionado no existe.",
            400
        )

    if puesto.departamento_id != departamento.id:

        return (
            "El puesto no pertenece al departamento seleccionado.",
            400
        )

    # ========================================================
    # CREAR COLABORADOR
    # ========================================================

    nuevo_colaborador = Colaborador(
        numero_empleado=numero_empleado,
        nombre=nombre,
        departamento_id=departamento.id,
        puesto_id=puesto.id,
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

    puestos = (
        Puesto.query
        .order_by(Puesto.nombre)
        .all()
    )

    departamentos = (
        Departamento.query
        .order_by(Departamento.nombre)
        .all()
    )

    habilidades = (
        Habilidad.query
        .order_by(Habilidad.nombre)
        .all()
    )

    departamento_seleccionado = request.args.get(
        "departamento_id",
        type=int
    )

    puesto_seleccionado = request.args.get(
        "puesto_id",
        type=int
    )


    # ========================================================
    # GUARDAR HABILIDADES DE UN PUESTO
    # ========================================================

    if request.method == "POST":

        puesto_id = request.form.get(
            "puesto_id",
            type=int
        )

        puesto = Puesto.query.get_or_404(
            puesto_id
        )


        habilidades_seleccionadas = (
            request.form.getlist(
                "habilidades"
            )
        )


        # ----------------------------------------------------
        # Eliminar solamente las asignaciones de este puesto
        # ----------------------------------------------------

        PuestoHabilidad.query.filter_by(
            puesto_id=puesto_id
        ).delete(
            synchronize_session=False
        )


        # ----------------------------------------------------
        # Crear las nuevas asignaciones
        #
        # Regla oficial del proyecto:
        # TODA habilidad requerida por un puesto = O
        # ----------------------------------------------------

        departamento_id = (
            puesto.departamento_id
        )


        for habilidad_id in habilidades_seleccionadas:

            try:

                habilidad_id = int(
                    habilidad_id
                )

            except (
                TypeError,
                ValueError
            ):

                continue


            habilidad = (
                Habilidad.query.get(
                    habilidad_id
                )
            )


            if not habilidad:
                continue


            db.session.add(
                PuestoHabilidad(
                    departamento_id=departamento_id,
                    puesto_id=puesto.id,
                    habilidad_id=habilidad.id,
                    nivel_requerido="O"
                )
            )


        db.session.commit()


        return redirect(
            url_for(
                "puesto_habilidades",
                puesto_id=puesto_id
            )
        )


    # ========================================================
    # CARGAR ASIGNACIONES ACTUALES
    # ========================================================

    asignaciones = []

    habilidades_asignadas = set()


    if puesto_seleccionado:

        asignaciones = (
            PuestoHabilidad.query
            .filter_by(
                puesto_id=puesto_seleccionado
            )
            .order_by(
                PuestoHabilidad.habilidad_id
            )
            .all()
        )


        habilidades_asignadas = {
            asignacion.habilidad_id
            for asignacion in asignaciones
        }


    # ========================================================
    # MOSTRAR
    # ========================================================

    return render_template(
        "puesto_habilidades.html",
        puestos=puestos,
        departamentos=departamentos,
        habilidades=habilidades,
        departamento_seleccionado=departamento_seleccionado,
        puesto_seleccionado=puesto_seleccionado,
        habilidades_asignadas=habilidades_asignadas,
        asignaciones=asignaciones
    )


@app.route("/evaluaciones")
def evaluaciones():

    usuario = usuario_actual()


    if not usuario:

        return redirect(
            url_for("login")
        )


    # ========================================================
    # COLABORADORES ACTIVOS AUTORIZADOS
    # ========================================================

    colaboradores_todos = (
        Colaborador.query
        .filter_by(
            activo=1
        )
        .order_by(
            Colaborador.nombre
        )
        .all()
    )


    lista_colaboradores = [
        colaborador
        for colaborador in colaboradores_todos
        if autorizado(
            usuario,
            "evaluar",
            colaborador=colaborador
        )
    ]


    # ========================================================
    # FILTROS
    # ========================================================

    colaborador_seleccionado = request.args.get(
        "colaborador_id",
        type=int
    )


    area_seleccionada = request.args.get(
        "area_id",
        type=int
    )


    # ========================================================
    # DATOS INICIALES
    # ========================================================

    colaborador_actual = None

    habilidades = []

    asignaciones = []

    evaluaciones_guardadas = {}

    evaluaciones_detalle = {}

    brechas = None


    # ========================================================
    # COLABORADOR SELECCIONADO
    # ========================================================

    if colaborador_seleccionado:

        colaborador_actual = (
            Colaborador.query
            .filter_by(
                id=colaborador_seleccionado,
                activo=1
            )
            .first()
        )


        if not colaborador_actual:

            return (
                "Colaborador no encontrado.",
                404
            )


        # ----------------------------------------------------
        # AUTORIZACION REAL
        # ----------------------------------------------------

        if not autorizado(
            usuario,
            "evaluar",
            colaborador=colaborador_actual
        ):

            return (
                "No tiene autorización para evaluar este colaborador.",
                403
            )


        # ====================================================
        # HABILIDADES DEL PUESTO
        # ====================================================

        asignaciones = (
            PuestoHabilidad.query
            .filter_by(
                puesto_id=colaborador_actual.puesto_id
            )
            .order_by(
                PuestoHabilidad.habilidad_id
            )
            .all()
        )


        habilidades = [
            asignacion.habilidad
            for asignacion in asignaciones
        ]


        # ====================================================
        # EVALUACIONES EXISTENTES
        # ====================================================

        registros = (
            Evaluacion.query
            .filter_by(
                colaborador_id=colaborador_actual.id
            )
            .order_by(
                Evaluacion.id.desc()
            )
            .all()
        )


        # ====================================================
        # NIVEL ACTUAL
        # ====================================================

        for registro in registros:

            if (
                registro.habilidad_id
                not in evaluaciones_guardadas
            ):

                evaluaciones_guardadas[
                    registro.habilidad_id
                ] = registro.nivel


                evaluaciones_detalle[
                    registro.habilidad_id
                ] = {

                    "id":
                        registro.id,

                    "nivel":
                        registro.nivel,

                    "evaluador":
                        registro.evaluador,

                    "rol_evaluador":
                        registro.rol_evaluador,

                    "fecha_evaluacion":
                        registro.fecha_evaluacion,

                    "comentario":
                        registro.comentario
                }


        # ====================================================
        # BRECHAS
        # ====================================================

        brechas = (
            calcular_brechas_colaborador(
                colaborador_actual
            )
        )


    # ========================================================
    # MOSTRAR
    # ========================================================

    return render_template(
        "evaluaciones.html",

        colaboradores=
            lista_colaboradores,

        colaborador_seleccionado=
            colaborador_seleccionado,

        area_seleccionada=
            area_seleccionada,

        colaborador_actual=
            colaborador_actual,

        habilidades=
            habilidades,

        asignaciones=
            asignaciones,

        evaluaciones=
            evaluaciones_guardadas,

        evaluaciones_detalle=
            evaluaciones_detalle,

        brechas=
            brechas,

        fecha_actual=date.today(),
        usuario_actual=
            usuario
    )

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

    usuario = usuario_actual()


    if not usuario:

        return redirect(
            url_for("login")
        )


    colaborador_id = request.form.get(
        "colaborador_id",
        type=int
    )


    if not colaborador_id:

        return (
            "Colaborador no especificado.",
            400
        )


    colaborador = (
        Colaborador.query
        .filter_by(
            id=colaborador_id,
            activo=1
        )
        .first()
    )


    if not colaborador:

        return (
            "Colaborador no encontrado.",
            404
        )


    if not autorizado(
        usuario,
        "evaluar",
        colaborador=colaborador
    ):

        return (
            "No tiene autorización para evaluar este colaborador.",
            403
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

    evaluador = (
        usuario.colaborador.nombre
        if usuario.colaborador
        else usuario.username
    )


    rol_evaluador = (
        usuario.rol
    )

    comentario = request.form.get(
        "comentario",
        ""
    ).strip()

    # =========================
    # =========================
    # FECHA AUTOMATICA
    # =========================

    # La fecha de la evaluacion la determina
    # exclusivamente el servidor.

    fecha_evaluacion = None

    fecha_objeto = date.today()

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
            "evaluaciones"
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































































