from datetime import date, datetime

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


# ============================================================
# AUDITORIA DE MODIFICACIONES DE COLABORADORES
# ============================================================

class ModificacionColaborador(db.Model):

    __tablename__ = 'modificacion_colaborador'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    colaborador_id = db.Column(
        db.Integer,
        db.ForeignKey('colaborador.id'),
        nullable=False
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey('usuario.id'),
        nullable=False
    )

    fecha_hora = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now
    )

    campo = db.Column(
        db.String(100),
        nullable=False
    )

    valor_anterior = db.Column(
        db.Text,
        nullable=True
    )

    valor_nuevo = db.Column(
        db.Text,
        nullable=True
    )

    motivo = db.Column(
        db.Text,
        nullable=False
    )

    colaborador = db.relationship(
        'Colaborador',
        backref=db.backref(
            'modificaciones',
            lazy=True
        )
    )

    usuario = db.relationship(
        'Usuario',
        backref=db.backref(
            'modificaciones_realizadas',
            lazy=True
        )
    )

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

    alcance = db.Column(
        db.String(20),
        nullable=True,
        default=None
    )

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
        foreign_keys=[area_id]
    )

    departamento = db.relationship(
        "Departamento",
        foreign_keys=[departamento_id]
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


class VisualizacionCurso(db.Model):

    __tablename__ = "visualizacion_curso"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    colaborador_id = db.Column(
        db.Integer,
        db.ForeignKey("colaborador.id"),
        nullable=False
    )

    curso_id = db.Column(
        db.Integer,
        db.ForeignKey("curso.id"),
        nullable=False
    )

    veces_visto = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    primera_vista = db.Column(
        db.DateTime,
        nullable=True
    )

    ultima_vista = db.Column(
        db.DateTime,
        nullable=True
    )

    colaborador = db.relationship(
        "Colaborador",
        backref="visualizaciones_cursos"
    )

    curso = db.relationship(
        "Curso",
        backref="visualizaciones"
    )


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

    alcance = db.Column(
        db.String(30),
        nullable=False,
        default="empresa"
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

# ============================================================
# RELACION PUESTO -> ROL
# ============================================================

class PuestoRol(db.Model):

    __tablename__ = "puesto_rol"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    puesto_id = db.Column(
        db.Integer,
        db.ForeignKey("puesto.id"),
        nullable=False,
        unique=True
    )

    rol_id = db.Column(
        db.Integer,
        db.ForeignKey("rol.id"),
        nullable=False
    )

    activo = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    puesto = db.relationship(
        "Puesto",
        foreign_keys=[puesto_id],
        backref="configuracion_rol"
    )

    rol = db.relationship(
        "Rol",
        foreign_keys=[rol_id],
        backref="puestos_asignados"
    )


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



# ============================================================
# ADMINISTRACION DE USUARIOS
# ============================================================

def rol_desde_colaborador(colaborador):

    if colaborador is None:
        return None

    puesto = colaborador.puesto

    if puesto is None:
        return "colaborador"

    puesto_rol = (
        PuestoRol.query
        .filter_by(
            puesto_id=puesto.id,
            activo=True
        )
        .first()
    )

    if puesto_rol is None:
        return "colaborador"

    rol = db.session.get(
        Rol,
        puesto_rol.rol_id
    )

    if rol is None:
        return "colaborador"

    return rol.nombre


@app.route(
    "/usuarios",
    methods=["GET"]
)
def administrar_usuarios():

    usuario = usuario_actual()

    if not usuario:
        return redirect(
            url_for("login")
        )

    if usuario.rol != "administrador":
        return (
            "Acceso no autorizado.",
            403
        )

    usuarios = (
        Usuario.query
        .order_by(
            Usuario.id
        )
        .all()
    )

    colaboradores = (
        Colaborador.query
        .filter_by(
            activo=True
        )
        .order_by(
            Colaborador.numero_empleado
        )
        .all()
    )

    return render_template(
        "usuarios.html",
        usuario=usuario,
        usuarios=usuarios,
        colaboradores=colaboradores,
        mensaje=request.args.get("mensaje"),
        error=request.args.get("error")
    )


@app.route(
    "/usuarios/crear",
    methods=["POST"]
)
def crear_usuario():

    usuario_actual_obj = usuario_actual()

    if not usuario_actual_obj:
        return redirect(
            url_for("login")
        )

    if usuario_actual_obj.rol != "administrador":
        return (
            "Acceso no autorizado.",
            403
        )

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

    colaborador_id = (
        request.form.get(
            "colaborador_id",
            ""
        )
        or ""
    ).strip()

    cuenta_admin = (
        request.form.get(
            "cuenta_admin",
            "normal"
        )
        or "normal"
    ).strip().lower()

    if not username:

        return redirect(
            url_for(
                "administrar_usuarios",
                error="El usuario es obligatorio."
            )
        )

    if len(password) < 8:

        return redirect(
            url_for(
                "administrar_usuarios",
                error="La contraseña debe tener al menos 8 caracteres."
            )
        )

    existente = (
        Usuario.query
        .filter_by(
            username=username
        )
        .first()
    )

    if existente is not None:

        return redirect(
            url_for(
                "administrar_usuarios",
                error="Ese usuario ya existe."
            )
        )

    colaborador = None

    if colaborador_id:

        try:

            colaborador_id_int = int(
                colaborador_id
            )

        except ValueError:

            return redirect(
                url_for(
                    "administrar_usuarios",
                    error="Colaborador no válido."
                )
            )

        colaborador = db.session.get(
            Colaborador,
            colaborador_id_int
        )

        if colaborador is None:

            return redirect(
                url_for(
                    "administrar_usuarios",
                    error="El colaborador no existe."
                )
            )

        cuenta_existente = (
            Usuario.query
            .filter_by(
                colaborador_id=colaborador.id
            )
            .first()
        )

        if cuenta_existente is not None:

            return redirect(
                url_for(
                    "administrar_usuarios",
                    error="Ese colaborador ya tiene una cuenta."
                )
            )

    if cuenta_admin == "admin":

        if colaborador is not None:

            return redirect(
                url_for(
                    "administrar_usuarios",
                    error="Una cuenta administradora no puede vincularse a un colaborador."
                )
            )

        rol = "administrador"

    else:

        if colaborador is None:

            return redirect(
                url_for(
                    "administrar_usuarios",
                    error="Un usuario normal debe vincularse a un colaborador."
                )
            )

        rol = rol_desde_colaborador(
            colaborador
        )

    from werkzeug.security import generate_password_hash

    nuevo = Usuario(
        username=username,
        password_hash=generate_password_hash(
            password
        ),
        rol=rol,
        colaborador_id=(
            colaborador.id
            if colaborador is not None
            else None
        ),
        activo=True
    )

    db.session.add(nuevo)
    db.session.commit()

    return redirect(
        url_for(
            "administrar_usuarios",
            mensaje="Usuario creado correctamente."
        )
    )


@app.route(
    "/usuarios/<int:usuario_id>/toggle",
    methods=["POST"]
)
def toggle_usuario(usuario_id):

    usuario_actual_obj = usuario_actual()

    if not usuario_actual_obj:
        return redirect(
            url_for("login")
        )

    if usuario_actual_obj.rol != "administrador":
        return (
            "Acceso no autorizado.",
            403
        )

    usuario = db.session.get(
        Usuario,
        usuario_id
    )

    if usuario is None:

        return redirect(
            url_for(
                "administrar_usuarios",
                error="Usuario no encontrado."
            )
        )

    if usuario.id == usuario_actual_obj.id:

        return redirect(
            url_for(
                "administrar_usuarios",
                error="No puedes desactivar tu propia cuenta."
            )
        )

    usuario.activo = not bool(
        usuario.activo
    )

    db.session.commit()

    estado = (
        "activado"
        if usuario.activo
        else "desactivado"
    )

    return redirect(
        url_for(
            "administrar_usuarios",
            mensaje=f"Usuario {estado} correctamente."
        )
    )


@app.route(
    "/usuarios/<int:usuario_id>/password",
    methods=["POST"]
)
def restablecer_password_usuario(usuario_id):

    usuario_actual_obj = usuario_actual()

    if not usuario_actual_obj:
        return redirect(
            url_for("login")
        )

    if usuario_actual_obj.rol != "administrador":
        return (
            "Acceso no autorizado.",
            403
        )

    usuario = db.session.get(
        Usuario,
        usuario_id
    )

    if usuario is None:

        return redirect(
            url_for(
                "administrar_usuarios",
                error="Usuario no encontrado."
            )
        )

    nueva_password = (
        request.form.get(
            "nueva_password",
            ""
        )
        or ""
    )

    if len(nueva_password) < 8:

        return redirect(
            url_for(
                "administrar_usuarios",
                error="La nueva contraseña debe tener al menos 8 caracteres."
            )
        )

    from werkzeug.security import generate_password_hash

    usuario.password_hash = (
        generate_password_hash(
            nueva_password
        )
    )

    db.session.commit()

    return redirect(
        url_for(
            "administrar_usuarios",
            mensaje="Contraseña restablecida correctamente."
        )
    )



@app.route(
    "/roles-permisos",
    methods=["GET", "POST"]
)

def roles_permisos():

    usuario = usuario_actual()

    es_admin = (
        usuario is not None
        and usuario.rol == "administrador"
    )

    puestos = (
        Puesto.query
        .order_by(
            Puesto.id
        )
        .all()
    )

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

    roles_por_nombre = {
        rol.nombre: rol
        for rol in roles
    }

    mapa_roles = {
        "gerente_general": "gerente_area",
        "gerente general": "gerente_area",
        "gerente de área": "gerente_area",
        "supervisor": "supervisor",
        "operador": "colaborador",
    }

    # =========================================================
    # GUARDAR TODO EL FORMULARIO
    # =========================================================

    if request.method == "POST":

        if not es_admin:

            return (
                "No autorizado",
                403
            )

        try:

            for puesto in puestos:

                campo_rol = (
                    f"puesto_rol_{puesto.id}"
                )

                # Solo procesar puestos que realmente
                # fueron enviados por el formulario.
                #
                # Los puestos ocultos no deben sobrescribir
                # los permisos del mismo rol.

                if campo_rol not in request.form:
                    continue


                categoria = (
                    request.form.get(
                        campo_rol,
                        "operador"
                    )
                    or "operador"
                ).strip().lower()

                # =================================================
                # NORMALIZACION DIRECTA DE LOS VALORES REALES
                # QUE ENVIA EL TEMPLATE
                # =================================================

                if categoria == "gerente_general":
                    rol_nombre = "gerente_area"

                elif categoria == "gerente_area":
                    rol_nombre = "gerente_area"

                elif categoria == "supervisor":
                    rol_nombre = "supervisor"

                elif categoria == "operador":
                    rol_nombre = "colaborador"

                elif categoria in {
                    "gerente de área",
                    "gerente general",
                    "gerente_area",
                    "supervisor",
                    "colaborador",
                }:

                    # Compatibilidad adicional
                    # con valores internos.

                    if categoria in {
                        "gerente de área",
                        "gerente general",
                        "gerente_area",
                    }:
                        rol_nombre = "gerente_area"

                    elif categoria == "colaborador":
                        rol_nombre = "colaborador"

                    else:
                        rol_nombre = "supervisor"

                else:

                    raise ValueError(
                        f"Rol no válido para el puesto "
                        f"{puesto.nombre}: {categoria}"
                    )

                rol = (
                    Rol.query
                    .filter_by(
                        nombre=rol_nombre,
                        activo=True
                    )
                    .first()
                )

                if rol is None:

                    raise ValueError(
                        f"No existe el rol interno "
                        f"{rol_nombre}"
                    )

                puesto_rol = (
                    PuestoRol.query
                    .filter_by(
                        puesto_id=puesto.id
                    )
                    .first()
                )

                if puesto_rol is None:

                    puesto_rol = PuestoRol(
                        puesto_id=puesto.id,
                        rol_id=rol.id,
                        activo=True
                    )

                    db.session.add(
                        puesto_rol
                    )

                else:

                    puesto_rol.rol_id = rol.id
                    puesto_rol.activo = True

                # -------------------------------------------------
                # PERMISOS DEL ROL
                # -------------------------------------------------

                for permiso in permisos:

                    campo_permiso = (
                        f"permiso_{puesto.id}_"
                        f"{permiso.id}"
                    )

                    campo_alcance = (
                        f"alcance_{puesto.id}_"
                        f"{permiso.id}"
                    )

                    permitido = (
                        campo_permiso in request.form
                    )

                    alcance = (
                        request.form.get(
                            campo_alcance,
                            "empresa"
                        )
                        or "empresa"
                    ).strip().lower()

                    if alcance not in {
                        "propio",
                        "departamento",
                        "area",
                        "empresa",
                    }:

                        alcance = "empresa"

                    rp = (
                        RolPermiso.query
                        .filter_by(
                            rol_id=rol.id,
                            permiso_id=permiso.id
                        )
                        .first()
                    )

                    if rp is None:

                        rp = RolPermiso(
                            rol_id=rol.id,
                            permiso_id=permiso.id,
                            permitido=permitido,
                            alcance=alcance
                        )

                        db.session.add(
                            rp
                        )

                    else:

                        rp.permitido = permitido
                        rp.alcance = alcance

            # -------------------------------------------------
            # REGLA DEFINIDA:
            # LÍDER DE ÁREA -> SUPERVISOR
            # -------------------------------------------------

            lider = (
                Puesto.query
                .filter_by(
                    nombre="Líder de Área"
                )
                .first()
            )

            supervisor = (
                Rol.query
                .filter_by(
                    nombre="supervisor",
                    activo=True
                )
                .first()
            )

            if (
                lider is not None
                and supervisor is not None
            ):

                pr_lider = (
                    PuestoRol.query
                    .filter_by(
                        puesto_id=lider.id
                    )
                    .first()
                )

                if pr_lider is None:

                    pr_lider = PuestoRol(
                        puesto_id=lider.id,
                        rol_id=supervisor.id,
                        activo=True
                    )

                    db.session.add(
                        pr_lider
                    )

                else:

                    pr_lider.rol_id = supervisor.id
                    pr_lider.activo = True

            db.session.commit()

            return redirect(
                url_for(
                    "roles_permisos",
                    guardado="ok"
                )
            )

        except Exception as exc:

            db.session.rollback()

            app.logger.exception(
                "Error guardando roles-permisos"
            )

            return (
                f"Error al guardar: {exc}",
                400
            )

    # =========================================================
    # PUESTO -> ROL PARA LA VISTA
    # =========================================================

    puesto_rol = {}

    relaciones = (
        PuestoRol.query
        .filter_by(
            activo=True
        )
        .all()
    )

    roles_por_id = {
        rol.id: rol
        for rol in roles
    }

    for relacion in relaciones:

        rol = roles_por_id.get(
            relacion.rol_id
        )

        puesto = db.session.get(
            Puesto,
            relacion.puesto_id
        )

        if (
            puesto is None
            or rol is None
        ):
            continue

        nombre_puesto = (
            puesto.nombre
            or ""
        ).strip().lower()

        if nombre_puesto == "gerente general":

            categoria = "gerente_general"

        elif rol.nombre == "gerente_area":

            categoria = "gerente_area"

        elif rol.nombre == "supervisor":

            categoria = "supervisor"

        else:

            categoria = "operador"

        puesto_rol[puesto.id] = {
            "rol_id": rol.id,
            "rol_nombre": rol.nombre,
            "categoria": categoria,
        }

    # =========================================================
    # MATRIZ PARA EL TEMPLATE EXISTENTE
    #
    # Se conserva el nombre "matriz" porque la plantilla actual
    # todavía lo utiliza internamente.
    # =========================================================

    matriz = {}

    for rol in roles:

        matriz[rol.id] = {}

        asignaciones = (
            RolPermiso.query
            .filter_by(
                rol_id=rol.id
            )
            .all()
        )

        for rp in asignaciones:

            matriz[rol.id][rp.permiso_id] = {
                "permitido": bool(
                    rp.permitido
                ),
                "alcance": (
                    rp.alcance
                    or "empresa"
                ),
            }

    guardado = (
        request.args.get(
            "guardado"
        )
        == "ok"
    )

    return render_template(
        "roles_permisos.html",
        usuario=usuario,
        es_admin=es_admin,
        puestos=puestos,
        areas=areas,
        departamentos=departamentos,
        roles=roles,
        permisos=permisos,
        puesto_rol=puesto_rol,
        matriz=matriz,
        guardado=guardado
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



# ============================================================
# SEGUIMIENTO RH
# ============================================================

@app.route(
    "/seguimiento",
    methods=["GET"]
)
def seguimiento():

    usuario = usuario_actual()

    if not usuario:
        return redirect(
            url_for("login")
        )

    roles_autorizados = {
        "administrador",
        "gerente_area",
        "gerente_operaciones",
        "supervisor",
        "rh"
    }

    if usuario.rol not in roles_autorizados:
        return (
            "Acceso no autorizado.",
            403
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

    colaborador_id = request.args.get(
        "colaborador_id",
        type=int
    )

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

    colaboradores = (
        Colaborador.query
        .filter_by(
            activo=True
        )
        .order_by(
            Colaborador.nombre
        )
        .all()
    )

    # ----------------------------------------------------------
    # Filtrar colaboradores
    # ----------------------------------------------------------

    colaboradores_filtrados = []

    for colaborador in colaboradores:

        departamento = (
            colaborador.departamento
        )

        puesto = (
            colaborador.puesto
        )

        area = (
            departamento.area
            if departamento
            else None
        )

        if area_id and (
            not area
            or area.id != area_id
        ):
            continue

        if departamento_id and (
            not departamento
            or departamento.id != departamento_id
        ):
            continue

        if puesto_id and (
            not puesto
            or puesto.id != puesto_id
        ):
            continue

        if colaborador_id and (
            colaborador.id != colaborador_id
        ):
            continue

        colaboradores_filtrados.append(
            colaborador
        )

    # ----------------------------------------------------------
    # Calcular seguimiento
    # ----------------------------------------------------------

    filas = []

    total_con_brecha = 0
    total_pendientes = 0
    suma_cumplimiento = 0

    for colaborador in colaboradores_filtrados:

        brechas = (
            calcular_brechas_colaborador(
                colaborador
            )
        )

        ultima_evaluacion = (
            Evaluacion.query
            .filter_by(
                colaborador_id=colaborador.id
            )
            .order_by(
                Evaluacion.fecha_evaluacion.desc(),
                Evaluacion.id.desc()
            )
            .first()
        )

        cumplimiento = (
            brechas.get(
                "porcentaje_cumplimiento",
                0
            )
            or 0
        )

        cantidad_brechas = (
            brechas.get(
                "brechas",
                0
            )
            or 0
        )

        cantidad_pendientes = (
            brechas.get(
                "pendientes",
                0
            )
            or 0
        )

        if cantidad_brechas > 0:
            total_con_brecha += 1

        total_pendientes += (
            cantidad_pendientes
        )

        suma_cumplimiento += float(
            cumplimiento
        )

        departamento = (
            colaborador.departamento
        )

        area = (
            departamento.area
            if departamento
            else None
        )

        filas.append({
            "colaborador": colaborador,
            "area": area,
            "ultima_evaluacion":
                (
                    ultima_evaluacion.fecha_evaluacion
                    if ultima_evaluacion
                    else None
                ),
            "cumplimiento":
                cumplimiento,
            "brechas":
                cantidad_brechas,
            "pendientes":
                cantidad_pendientes
        })

    total_colaboradores = len(
        filas
    )

    cumplimiento_promedio = (
        round(
            suma_cumplimiento
            /
            total_colaboradores,
            1
        )
        if total_colaboradores
        else 0
    )

    return render_template(
        "seguimiento.html",
        usuario=usuario,
        areas=areas,
        departamentos=departamentos,
        puestos=puestos,
        colaboradores_filtro=colaboradores_filtrados,
        filas=filas,
        area_seleccionada=area_id,
        departamento_seleccionado=departamento_id,
        puesto_seleccionado=puesto_id,
        colaborador_seleccionado=colaborador_id,
        total_colaboradores=
            total_colaboradores,
        total_con_brecha=
            total_con_brecha,
        total_pendientes=
            total_pendientes,
        cumplimiento_promedio=
            cumplimiento_promedio
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

    colaboradores = Colaborador.query.filter_by(
        activo=1
    ).count()
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

@app.route("/colaboradores/historial/<int:id>", methods=["GET"])
def historial_colaborador(id):

    if "usuario_id" not in session:
        return redirect(url_for("login"))


    colaborador = Colaborador.query.get_or_404(
        id
    )


    historial = ModificacionColaborador.query.filter_by(
        colaborador_id=colaborador.id
    ).order_by(
        ModificacionColaborador.fecha_hora.desc(),
        ModificacionColaborador.id.desc()
    ).all()


    # ========================================================
    # SOLO CAMBIOS REALES
    #
    # Se ignoran diferencias causadas unicamente por espacios
    # al inicio o al final.
    # ========================================================

    historial_real = []


    for registro in historial:

        valor_anterior = (
            ""
            if registro.valor_anterior is None
            else str(
                registro.valor_anterior
            ).strip()
        )


        valor_nuevo = (
            ""
            if registro.valor_nuevo is None
            else str(
                registro.valor_nuevo
            ).strip()
        )


        if valor_anterior != valor_nuevo:

            historial_real.append(
                registro
            )


    # ========================================================
    # AGRUPAR POR MOVIMIENTO
    # ========================================================

    movimientos = []

    grupos = {}


    for registro in historial_real:

        if registro.fecha_hora:

            fecha_grupo = registro.fecha_hora.replace(
                microsecond=0
            )

        else:

            fecha_grupo = None


        clave = (
            registro.usuario_id,
            fecha_grupo,
            registro.motivo or ""
        )


        if clave not in grupos:

            grupos[clave] = {

                "fecha_hora": registro.fecha_hora,

                "usuario_id": registro.usuario_id,

                "motivo": registro.motivo,

                "cambios": []

            }


            movimientos.append(
                grupos[clave]
            )


        grupos[clave]["cambios"].append(
            registro
        )


    # ========================================================
    # USUARIOS
    # ========================================================

    usuario_ids = sorted(
        {
            movimiento["usuario_id"]
            for movimiento in movimientos
            if movimiento["usuario_id"] is not None
        }
    )


    usuarios = {}


    if usuario_ids:

        usuarios_db = Usuario.query.filter(
            Usuario.id.in_(usuario_ids)
        ).all()


        usuarios = {

            usuario.id: usuario

            for usuario in usuarios_db

        }


    return render_template(
        "historial_colaborador.html",
        colaborador=colaborador,
        movimientos=movimientos,
        usuarios=usuarios
    )


@app.route("/colaboradores")
def colaboradores():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    filtro_numero_empleado = request.args.get(
        "numero_empleado",
        ""
    ).strip()

    filtro_area_id = request.args.get(
        "area_id",
        ""
    ).strip()

    filtro_departamento_id = request.args.get(
        "departamento_id",
        ""
    ).strip()

    filtro_puesto_id = request.args.get(
        "puesto_id",
        ""
    ).strip()

    areas = Area.query.order_by(
        Area.nombre.asc()
    ).all()

    departamentos = Departamento.query.order_by(
        Departamento.nombre.asc()
    ).all()

    puestos = Puesto.query.order_by(
        Puesto.nombre.asc()
    ).all()

    lista_colaboradores = Colaborador.query.filter_by(
        activo=1
    ).order_by(
        Colaborador.nombre.asc()
    ).all()


    # --------------------------------------------------------
    # FILTRO NO. EMPLEADO
    # --------------------------------------------------------

    if filtro_numero_empleado:

        texto_numero = filtro_numero_empleado.lower()

        lista_colaboradores = [
            colaborador
            for colaborador in lista_colaboradores
            if texto_numero in str(
                colaborador.numero_empleado or ""
            ).lower()
        ]


    # --------------------------------------------------------
    # FILTRO AREA
    # --------------------------------------------------------

    if filtro_area_id:

        try:

            area_id_num = int(
                filtro_area_id
            )

            departamentos_area = {
                departamento.id
                for departamento in departamentos
                if departamento.area_id == area_id_num
            }

            lista_colaboradores = [
                colaborador
                for colaborador in lista_colaboradores
                if colaborador.departamento_id in departamentos_area
            ]

        except (ValueError, TypeError):

            filtro_area_id = ""


    # --------------------------------------------------------
    # FILTRO DEPARTAMENTO
    # --------------------------------------------------------

    if filtro_departamento_id:

        try:

            departamento_id_num = int(
                filtro_departamento_id
            )

            lista_colaboradores = [
                colaborador
                for colaborador in lista_colaboradores
                if colaborador.departamento_id == departamento_id_num
            ]

        except (ValueError, TypeError):

            filtro_departamento_id = ""


    # --------------------------------------------------------
    # FILTRO PUESTO
    # --------------------------------------------------------

    if filtro_puesto_id:

        try:

            puesto_id_num = int(
                filtro_puesto_id
            )

            lista_colaboradores = [
                colaborador
                for colaborador in lista_colaboradores
                if colaborador.puesto_id == puesto_id_num
            ]

        except (ValueError, TypeError):

            filtro_puesto_id = ""


    return render_template(
        "colaboradores.html",
        colaboradores=lista_colaboradores,
        areas=areas,
        departamentos=departamentos,
        puestos=puestos,
        filtro_numero_empleado=filtro_numero_empleado,
        filtro_area_id=filtro_area_id,
        filtro_departamento_id=filtro_departamento_id,
        filtro_puesto_id=filtro_puesto_id
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

@app.route("/colaboradores/editar/<int:id>", methods=["GET", "POST"])
@app.route("/colaboradores/editar/<int:id>", methods=["GET", "POST"])
def editar_colaborador(id):

    colaborador = Colaborador.query.get_or_404(id)

    areas = Area.query.order_by(Area.nombre).all()
    departamentos = Departamento.query.order_by(Departamento.nombre).all()
    puestos = Puesto.query.order_by(Puesto.nombre).all()

    if request.method == 'POST':

        numero_empleado = request.form.get('numero_empleado', '').strip()
        nombre = request.form.get('nombre', '').strip()
        area_id = request.form.get('area_id', type=int)
        departamento_id = request.form.get('departamento_id', type=int)
        puesto_id = request.form.get('puesto_id', type=int)
        motivo = request.form.get('motivo_modificacion', '').strip()

        if not numero_empleado:
            return ('El número de empleado es obligatorio.', 400)

        if not nombre:
            return ('El nombre es obligatorio.', 400)

        if not area_id:
            return ('El área es obligatoria.', 400)

        if not departamento_id:
            return ('El departamento es obligatorio.', 400)

        if not puesto_id:
            return ('El puesto es obligatorio.', 400)

        if not motivo:
            return ('El motivo de la modificación es obligatorio.', 400)

        area = Area.query.filter_by(id=area_id).first()

        if not area:
            return ('El área seleccionada no existe.', 400)

        departamento = Departamento.query.filter_by(id=departamento_id).first()

        if not departamento:
            return ('El departamento seleccionado no existe.', 400)

        if departamento.area_id != area.id:
            return ('El departamento no pertenece al área seleccionada.', 400)

        puesto = Puesto.query.filter_by(id=puesto_id).first()

        if not puesto:
            return ('El puesto seleccionado no existe.', 400)

        if puesto.departamento_id != departamento.id:
            return ('El puesto no pertenece al departamento seleccionado.', 400)

        # =================================================
        # VALORES ANTERIORES
        # =================================================

        numero_anterior = colaborador.numero_empleado
        nombre_anterior = colaborador.nombre
        departamento_anterior = colaborador.departamento_id
        puesto_anterior = colaborador.puesto_id

        # =================================================
        # VALORES NUEVOS
        # =================================================

        cambios = []

        if numero_anterior != numero_empleado:

            cambios.append((
                'Número de empleado',
                numero_anterior,
                numero_empleado
            ))

        if nombre_anterior != nombre:

            cambios.append((
                'Nombre',
                nombre_anterior,
                nombre
            ))

        if departamento_anterior != departamento.id:

            cambios.append((
                'Departamento',
                colaborador.departamento.nombre
                if colaborador.departamento
                else 'Sin departamento',
                departamento.nombre
            ))

        if puesto_anterior != puesto.id:

            cambios.append((
                'Puesto',
                colaborador.puesto.nombre
                if colaborador.puesto
                else 'Sin puesto',
                puesto.nombre
            ))

        # =================================================
        # SI NO CAMBIO NADA
        # =================================================

        if not cambios:

            return (
                'No se detectaron cambios en el colaborador.',
                400
            )

        # =================================================
        # USUARIO DE SESION
        # =================================================

        usuario = usuario_actual()

        if not usuario:

            return (
                'La sesión del usuario no es válida.',
                401
            )

        # =================================================
        # APLICAR CAMBIOS
        # =================================================

        colaborador.numero_empleado = numero_empleado
        colaborador.nombre = nombre
        colaborador.departamento_id = departamento.id
        colaborador.puesto_id = puesto.id

        # =================================================
        # REGISTRAR AUDITORIA
        # =================================================

        for campo, valor_anterior, valor_nuevo in cambios:

            registro = ModificacionColaborador(
                colaborador_id=colaborador.id,
                usuario_id=usuario.id,
                campo=campo,
                valor_anterior=str(valor_anterior),
                valor_nuevo=str(valor_nuevo),
                motivo=motivo
            )

            db.session.add(
                registro
            )

        db.session.commit()

        return redirect(
            url_for('colaboradores')
        )

    return render_template(
        'editar_colaborador.html',
        colaborador=colaborador,
        areas=areas,
        departamentos=departamentos,
        puestos=puestos
    )

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
# ============================================================
# AREAS
# ============================================================

@app.route("/areas", methods=["GET", "POST"])
def areas():

    if request.method == "POST":

        nombre = request.form.get(
            "nombre",
            ""
        ).strip()

        if nombre:

            existente = Area.query.filter_by(
                nombre=nombre
            ).first()

            if not existente:

                nueva_area = Area(
                    nombre=nombre
                )

                db.session.add(
                    nueva_area
                )

                db.session.commit()

        return redirect(
            url_for("areas")
        )

    lista_areas = (
        Area.query
        .order_by(
            Area.nombre
        )
        .all()
    )

    return render_template(
        "areas.html",
        areas=lista_areas
    )

# HABILIDADES
# =========================

@app.route("/habilidades")
def habilidades():

    area_id = request.args.get("area_id", type=int)
    departamento_id = request.args.get("departamento_id", type=int)
    alcance = request.args.get("alcance")

    areas = Area.query.order_by(Area.nombre).all()
    departamentos = Departamento.query.order_by(Departamento.nombre).all()

    consulta = Habilidad.query

    if area_id:
        consulta = consulta.filter(Habilidad.area_id == area_id)

    if departamento_id:
        consulta = consulta.filter(Habilidad.departamento_id == departamento_id)

    if alcance in ("empresa", "area", "departamento"):
        consulta = consulta.filter(Habilidad.alcance == alcance)

    lista_habilidades = consulta.order_by(
        Habilidad.nombre
    ).all()

    return render_template(
        "habilidades.html",
        habilidades=lista_habilidades,
        areas=areas,
        departamentos=departamentos,
        area_seleccionada=area_id,
        departamento_seleccionado=departamento_id,
        alcance_seleccionado=alcance
    )


@app.route(
    "/habilidades/agregar",
    methods=["POST"]
)
def agregar_habilidad():

    nombre = (
        request.form.get("nombre") or ""
    ).strip()

    alcance = (
        request.form.get("alcance") or ""
    ).strip().lower()

    area_id = request.form.get(
        "area_id",
        type=int
    )

    departamento_id = request.form.get(
        "departamento_id",
        type=int
    )

    if not nombre:
        return redirect(
            url_for("habilidades")
        )

    if alcance not in (
        "empresa",
        "area",
        "departamento"
    ):
        return redirect(
            url_for("habilidades")
        )

    # Empresa: no lleva Área ni Departamento
    if alcance == "empresa":

        area_id = None
        departamento_id = None

    # Área: requiere Área y no lleva Departamento
    elif alcance == "area":

        if not area_id:
            return redirect(
                url_for("habilidades")
            )

        Area.query.get_or_404(area_id)

        departamento_id = None

    # Departamento: requiere Área + Departamento
    else:

        if not area_id or not departamento_id:
            return redirect(
                url_for("habilidades")
            )

        area = Area.query.get_or_404(
            area_id
        )

        departamento = Departamento.query.get_or_404(
            departamento_id
        )

        if departamento.area_id != area.id:
            return redirect(
                url_for("habilidades")
            )

    # Evitar habilidades duplicadas por nombre
    existente = Habilidad.query.filter(
        db.func.lower(Habilidad.nombre)
        == nombre.lower()
    ).first()

    if existente:
        return redirect(
            url_for("habilidades")
        )

    nueva_habilidad = Habilidad(
        nombre=nombre,
        alcance=alcance,
        area_id=area_id,
        departamento_id=departamento_id
    )

    db.session.add(
        nueva_habilidad
    )

    db.session.commit()

    return redirect(
        url_for("habilidades")
    )


@app.route(
    "/habilidades/editar/<int:id>",
    methods=["GET", "POST"]
)
def editar_habilidad(id):

    habilidad = Habilidad.query.get_or_404(id)

    areas = Area.query.order_by(
        Area.nombre
    ).all()

    departamentos = Departamento.query.order_by(
        Departamento.nombre
    ).all()

    if request.method == "POST":

        nombre = (
            request.form.get("nombre") or ""
        ).strip()

        alcance = (
            request.form.get("alcance") or ""
        ).strip().lower()

        area_id = request.form.get(
            "area_id",
            type=int
        )

        departamento_id = request.form.get(
            "departamento_id",
            type=int
        )

        if not nombre:
            return redirect(
                url_for("habilidades")
            )

        if alcance not in (
            "empresa",
            "area",
            "departamento"
        ):
            return redirect(
                url_for("habilidades")
            )

        if alcance == "empresa":

            area_id = None
            departamento_id = None

        elif alcance == "area":

            if not area_id:
                return redirect(
                    url_for("habilidades")
                )

            Area.query.get_or_404(
                area_id
            )

            departamento_id = None

        else:

            if not area_id or not departamento_id:
                return redirect(
                    url_for("habilidades")
                )

            area = Area.query.get_or_404(
                area_id
            )

            departamento = Departamento.query.get_or_404(
                departamento_id
            )

            if departamento.area_id != area.id:
                return redirect(
                    url_for("habilidades")
                )

        duplicada = Habilidad.query.filter(
            Habilidad.id != habilidad.id,
            db.func.lower(Habilidad.nombre)
            == nombre.lower()
        ).first()

        if duplicada:
            return redirect(
                url_for("habilidades")
            )

        habilidad.nombre = nombre
        habilidad.alcance = alcance
        habilidad.area_id = area_id
        habilidad.departamento_id = departamento_id

        db.session.commit()

        return redirect(
            url_for("habilidades")
        )

    return render_template(
        "editar_habilidad.html",
        habilidad=habilidad,
        areas=areas,
        departamentos=departamentos
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

    areas = (
        Area.query
        .order_by(Area.nombre)
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
        areas=areas,
        puestos=puestos,
        departamentos=departamentos,
        habilidades=habilidades,
        area_seleccionada=area_seleccionada,
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

# ============================================================
# DETALLE DE SEGUIMIENTO
# ============================================================

@app.route(
    "/seguimiento/detalle/<int:colaborador_id>"
)
def seguimiento_detalle(
    colaborador_id
):

    usuario = usuario_actual()

    if not usuario:
        return redirect(
            url_for("login")
        )

    roles_autorizados = {
        "administrador",
        "gerente_area",
        "gerente_operaciones",
        "supervisor",
        "rh"
    }

    if usuario.rol not in roles_autorizados:
        return (
            "Acceso no autorizado.",
            403
        )

    colaborador = db.session.get(
        Colaborador,
        colaborador_id
    )

    if colaborador is None:
        return (
            "Colaborador no encontrado.",
            404
        )

    resultado = calcular_brechas_colaborador(
        colaborador
    )

    detalles = []

    for detalle in resultado.get(
        "detalle",
        []
    ):

        cursos = (
            Curso.query
            .filter_by(
                habilidad_id=
                    detalle["habilidad_id"]
            )
            .order_by(
                Curso.orden,
                Curso.id
            )
            .all()
        )

        materiales = []

        for curso in cursos:

            vista = (
                VisualizacionCurso.query
                .filter_by(
                    colaborador_id=
                        colaborador.id,
                    curso_id=
                        curso.id
                )
                .first()
            )

            materiales.append({
                "curso": curso,
                "visto": (
                    vista is not None
                    and
                    (vista.veces_visto or 0) > 0
                ),
                "veces": (
                    vista.veces_visto
                    if vista
                    else 0
                ),
                "ultima_vista": (
                    vista.ultima_vista
                    if vista
                    else None
                )
            })

        detalles.append({
            "habilidad":
                detalle["habilidad"],
            "habilidad_id":
                detalle["habilidad_id"],
            "nivel_requerido":
                detalle["nivel_requerido"],
            "nivel_actual":
                detalle["nivel_actual"],
            "diferencia":
                detalle["diferencia"],
            "estado":
                detalle["estado"],
            "evaluacion":
                detalle["evaluacion"],
            "materiales":
                materiales
        })

    return render_template(
        "seguimiento_detalle.html",
        usuario=usuario,
        colaborador=colaborador,
        resultado=resultado,
        detalles=detalles
    )


# ============================================================
# VER EVALUACION DESDE SEGUIMIENTO
# ============================================================

@app.route(
    "/seguimiento/evaluacion/<int:colaborador_id>"
)
def seguimiento_evaluacion(
    colaborador_id
):

    usuario = usuario_actual()

    if not usuario:
        return redirect(
            url_for("login")
        )

    roles_autorizados = {
        "administrador",
        "gerente_area",
        "gerente_operaciones",
        "supervisor",
        "rh"
    }

    if usuario.rol not in roles_autorizados:
        return (
            "Acceso no autorizado.",
            403
        )

    colaborador = db.session.get(
        Colaborador,
        colaborador_id
    )

    if colaborador is None:
        return (
            "Colaborador no encontrado.",
            404
        )

    evaluacion = (
        Evaluacion.query
        .filter_by(
            colaborador_id=
                colaborador.id
        )
        .order_by(
            Evaluacion.fecha_evaluacion.desc(),
            Evaluacion.id.desc()
        )
        .first()
    )

    if evaluacion is None:
        return (
            "Este colaborador todavía no tiene una evaluación.",
            404
        )

    return redirect(
        url_for(
            "ver_evaluacion",
            evaluacion_id=
                evaluacion.id
        )
    )


# ============================================================
# ABRIR MATERIAL Y REGISTRAR VISUALIZACION
# ============================================================

@app.route(
    "/seguimiento/material/<int:colaborador_id>/<int:curso_id>"
)
def seguimiento_material(
    colaborador_id,
    curso_id
):

    usuario = usuario_actual()

    if not usuario:
        return redirect(
            url_for("login")
        )

    roles_autorizados = {
        "administrador",
        "gerente_area",
        "gerente_operaciones",
        "supervisor",
        "rh",
        "colaborador"
    }

    if usuario.rol not in roles_autorizados:
        return (
            "Acceso no autorizado.",
            403
        )

    colaborador = db.session.get(
        Colaborador,
        colaborador_id
    )

    curso = db.session.get(
        Curso,
        curso_id
    )

    if colaborador is None:
        return (
            "Colaborador no encontrado.",
            404
        )

    if curso is None:
        return (
            "Curso no encontrado.",
            404
        )

    # ========================================================
    # QUIEN ESTA ABRIENDO EL MATERIAL
    # ========================================================

    current_user_colaborador = None

    if usuario.colaborador_id:

        current_user_colaborador = (
            db.session.get(
                Colaborador,
                usuario.colaborador_id
            )
        )

    # ========================================================
    # REGLA:
    # ADMIN / RH / SUPERVISOR / GERENTE
    # PUEDEN CONSULTAR EL MATERIAL,
    # PERO NO REGISTRAN LA VISTA DEL COLABORADOR.
    # ========================================================

    debe_registrar_vista = False

    if (
        usuario.rol == "colaborador"
        and current_user_colaborador is not None
    ):

        # ====================================================
        # VALIDAR QUE EL MATERIAL CORRESPONDA AL PUESTO
        # DEL COLABORADOR QUE LO ESTA ABRIENDO.
        # ====================================================

        puesto_actual = (
            current_user_colaborador.puesto_id
        )

        habilidad_del_curso = (
            curso.habilidad_id
        )

        pertenece_al_puesto = (
            PuestoHabilidad.query
            .filter_by(
                puesto_id=puesto_actual,
                habilidad_id=habilidad_del_curso
            )
            .first()
            is not None
        )

        if pertenece_al_puesto:

            debe_registrar_vista = True

    # ========================================================
    # REGISTRAR VISTA SOLO DEL COLABORADOR REAL
    # ========================================================

    if debe_registrar_vista:

        colaborador_vista_id = (
            current_user_colaborador.id
        )

        vista = (
            VisualizacionCurso.query
            .filter_by(
                colaborador_id=
                    colaborador_vista_id,
                curso_id=
                    curso.id
            )
            .first()
        )

        ahora = datetime.now()

        if vista is None:

            vista = VisualizacionCurso(
                colaborador_id=
                    colaborador_vista_id,
                curso_id=
                    curso.id,
                veces_visto=1,
                primera_vista=ahora,
                ultima_vista=ahora
            )

            db.session.add(vista)

        else:

            vista.veces_visto = (
                vista.veces_visto or 0
            ) + 1

            vista.ultima_vista = ahora

        db.session.commit()

    # ========================================================
    # ABRIR MATERIAL
    # ========================================================

    if curso.archivo_pdf:

        nombre_archivo = os.path.basename(
            curso.archivo_pdf
        )

        return redirect(
            url_for(
                "curso_pdf",
                nombre_archivo=
                    nombre_archivo
            )
        )

    if curso.enlace:

        return redirect(
            curso.enlace
        )

    return redirect(
        url_for(
            "seguimiento_detalle",
            colaborador_id=
                colaborador.id
        )
    )


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


# ============================================================
# ADMINISTRACION DE PERMISOS Y ALCANCE
# ============================================================

@app.route(
    "/administracion/permisos",
    methods=["GET", "POST"]
)
def administracion_permisos():

    usuario = usuario_actual()


    if not usuario:

        return redirect(
            url_for("login")
        )


    if usuario.rol != "administrador":

        return (
            "Acceso no autorizado.",
            403
        )


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


    rol_id = request.args.get(
        "rol_id",
        type=int
    )


    if request.method == "POST":

        rol_id = request.form.get(
            "rol_id",
            type=int
        )


        rol_actual = (
            Rol.query
            .filter_by(
                id=rol_id,
                activo=True
            )
            .first()
        )


        if not rol_actual:

            return (
                "Rol no valido.",
                400
            )


        alcances_validos = {
            "propio",
            "puesto",
            "departamento",
            "area",
            "empresa"
        }


        for permiso in permisos:

            campo_permitido = (
                "permiso_"
                + str(permiso.id)
                + "_permitido"
            )


            campo_alcance = (
                "permiso_"
                + str(permiso.id)
                + "_alcance"
            )


            permitido = (
                request.form.get(
                    campo_permitido
                )
                == "1"
            )


            alcance = (
                request.form.get(
                    campo_alcance,
                    "empresa"
                )
                or "empresa"
            ).strip().lower()


            if alcance not in alcances_validos:

                alcance = "empresa"


            relacion = (
                RolPermiso.query
                .filter_by(
                    rol_id=rol_actual.id,
                    permiso_id=permiso.id
                )
                .first()
            )


            if relacion is None:

                relacion = RolPermiso(
                    rol_id=rol_actual.id,
                    permiso_id=permiso.id,
                    permitido=permitido,
                    alcance=alcance
                )

                db.session.add(
                    relacion
                )

            else:

                relacion.permitido = permitido
                relacion.alcance = alcance


        db.session.commit()


        return redirect(
            url_for(
                "administracion_permisos",
                rol_id=rol_actual.id,
                guardado=1
            )
        )


    if rol_id:

        rol_actual = (
            Rol.query
            .filter_by(
                id=rol_id,
                activo=True
            )
            .first()
        )

    else:

        rol_actual = (
            roles[0]
            if roles
            else None
        )


    relaciones = {}


    if rol_actual:

        relaciones_db = (
            RolPermiso.query
            .filter_by(
                rol_id=rol_actual.id
            )
            .all()
        )


        relaciones = {
            relacion.permiso_id: relacion
            for relacion in relaciones_db
        }


    guardado = request.args.get(
        "guardado",
        type=int
    )


    return render_template(
        "administracion_permisos.html",
        roles=roles,
        permisos=permisos,
        rol_actual=rol_actual,
        relaciones=relaciones,
        guardado=guardado
    )


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
    # ENCABEZADO CORPORATIVO
    # ========================================================

    ruta_logo = os.path.join(
        app.root_path,
        "static",
        "img",
        "LOGO OFICIAL EMBBA.png"
    )

    if os.path.exists(ruta_logo):

        from PIL import Image as PILImage

        imagen_original = PILImage.open(
            ruta_logo
        ).convert("RGBA")

        ancho, alto = imagen_original.size

        lado = min(
            ancho,
            alto
        )

        izquierda = (ancho - lado) // 2
        superior = (alto - lado) // 2

        imagen_cuadrada = imagen_original.crop(
            (
                izquierda,
                superior,
                izquierda + lado,
                superior + lado
            )
        )

        logo_memoria = io.BytesIO()

        imagen_cuadrada.save(
            logo_memoria,
            format="PNG"
        )

        logo_memoria.seek(0)

        logo_pdf = Image(
            logo_memoria,
            width=3.2 * cm,
            height=3.2 * cm
        )

        logo_pdf.hAlign = "CENTER"

        elementos.append(
            logo_pdf
        )

        elementos.append(
            Spacer(
                1,
                0.08 * cm
            )
        )

    elementos.append(
        Paragraph(
            "EVALUACIÓN DE HABILIDADES ILUO",
            titulo
        )
    )

    elementos.append(
        Paragraph(
            "EVIDENCIA DOCUMENTAL",
            subtitulo
        )
    )

    linea_membrete = Table(
        [[""]],
        colWidths=[17 * cm],
        rowHeights=[0.10 * cm]
    )

    linea_membrete.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                colors.HexColor("#E63B19")
            ),
            (
                "BOX",
                (0, 0),
                (-1, -1),
                0,
                colors.HexColor("#E63B19")
            )
        ])
    )

    elementos.append(
        linea_membrete
    )

    elementos.append(
        Spacer(
            1,
            0.18 * cm
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








































































