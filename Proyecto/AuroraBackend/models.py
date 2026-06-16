from sqlalchemy import (

    Column, String, Integer, SmallInteger, Date, DateTime, Text, ForeignKey, Enum as SqlEnum, DECIMAL, BLOB, text, ForeignKey, Enum as SqlEnum, DECIMAL, BLOB

)
from sqlalchemy.orm import relationship, declarative_base, synonym
import enum

Base = declarative_base()


# Enums
class GeneroEnum(str, enum.Enum):
    Masculino = "Masculino"
    Femenino  = "Femenino"
    Otro      = "Otro"

class EstadoEnum(str, enum.Enum):
    Activo   = "Activo"
    Inactivo = "Inactivo"

class TipoPreguntaEnum(str, enum.Enum):
    Alternativa = "Alternativa"
    Desarrollo  = "Desarrollo"

class TipoEmocionEnum(str, enum.Enum):
    pre  = "pre"
    post = "post"

# ---------- GEOGRAFÍA (respetando tablas/keys de main) ----------------------
class Pais(Base):
    __tablename__ = "pais"
    idPais = Column(SmallInteger, primary_key=True)
    Nombre = Column(String(50), nullable=False)

class Region(Base):
    __tablename__ = "region"
    idRegion = Column(SmallInteger, primary_key=True)
    Nombre = Column(String(50))
    PaisId = Column(SmallInteger, ForeignKey("pais.idPais"), nullable=False)

class Provincia(Base):
    __tablename__ = "provincia"
    idProvincia = Column(SmallInteger, primary_key=True)
    Nombre = Column(String(50))
    RegionId = Column(SmallInteger, ForeignKey("region.idRegion"), nullable=False)

class Comuna(Base):
    __tablename__ = "comuna"
    idComuna = Column(SmallInteger, primary_key=True)
    Nombre = Column(String(50))
    ProvinciaId = Column(SmallInteger, ForeignKey("provincia.idProvincia"), nullable=False)

class Colegio(Base):
    __tablename__ = "colegio"
    idColegio = Column(SmallInteger, primary_key=True)
    Nombre    = Column(String(100), nullable=False)
    Ubicacion = Column(String(100))
    Telefono  = Column(String(20))
    ComunaId  = Column(SmallInteger, ForeignKey("comuna.idComuna"), nullable=False)

# ---------- PERSONAS ---------------------------------------------------------
class Persona(Base):
    __tablename__ = "persona"
    RUT = Column(String(12), primary_key=True)
    Nombres = Column(String(45), nullable=False)
    ApellidoPaterno = Column(String(45), nullable=False)
    ApellidoMaterno = Column(String(45), nullable=False)
    ComunaId = Column(SmallInteger, nullable=False)
    Telefono = Column(String(20))
    Correo = Column(String(100))
    Direccion = Column(String(100))
    FechaNacimiento = Column(Date)
    Genero = Column(SqlEnum(GeneroEnum))
    Estado = Column(SqlEnum(EstadoEnum))

class Rol(Base):
    __tablename__ = "rol"
    idRol = Column(SmallInteger, primary_key=True)
    Nombre = Column(String(20), unique=True, nullable=False)

class PersonaRol(Base):
    __tablename__ = "personarol"
    PersonaRUT = Column(String(12), ForeignKey("persona.RUT"), primary_key=True)
    RolId = Column(SmallInteger, ForeignKey("rol.idRol"), primary_key=True)
    ColegioId = Column(SmallInteger, ForeignKey("colegio.idColegio"), primary_key=True)

class Profesor(Base):
    __tablename__ = "profesor"
    RUT = Column(String(12), ForeignKey("persona.RUT"), primary_key=True)
    Especialidad = Column(String(100))
    TituloProfesional = Column(String(100))
    persona = relationship("Persona", foreign_keys=[RUT])

class Apoderado(Base):
    __tablename__ = "apoderado"
    RUT = Column(String(12), ForeignKey("persona.RUT"), primary_key=True)
    Parentesco = Column(String(50))

# ---------- ACADEMIA ---------------------------------------------------------
class Curso(Base):
    __tablename__ = "curso"
    idCurso = Column(SmallInteger, primary_key=True)
    Grado = Column(String(10))
    Etapa = Column(String(20))
    Letra = Column(String(1))
    ProfesorJefeRUT = Column(String(12), ForeignKey("profesor.RUT"), nullable=False)

class CursoUnidad(Base):
    __tablename__ = "curso_has_unidad"
    CursoId = Column(SmallInteger, ForeignKey("curso.idCurso"), primary_key=True)
    UnidadId = Column(SmallInteger, ForeignKey("unidad.idUnidad"), primary_key=True)

class Estudiante(Base):
    __tablename__ = "estudiante"
    RUT = Column(String(12), ForeignKey("persona.RUT"), primary_key=True)
    ApoderadoRUT = Column(String(12), ForeignKey("persona.RUT"))
    CursoId = Column(SmallInteger, ForeignKey("curso.idCurso"), nullable=False)
    Puntos = Column(SmallInteger)
    PromedioGeneral = Column(SmallInteger)
    # skin activa (main)
    SkinActivaId = Column(SmallInteger, ForeignKey("item.idItem"), nullable=True)

    # relaciones (main)
    skin_activa = relationship("Item", foreign_keys=[SkinActivaId], uselist=False)
    persona = relationship("Persona", foreign_keys=[RUT])

    # ---- alias snake_case para móvil ----
    rut               = synonym("RUT")
    apoderado_rut     = synonym("ApoderadoRUT")
    curso_id          = synonym("CursoId")
    puntos            = synonym("Puntos")
    promedio_general  = synonym("PromedioGeneral")
    skin_activa_item_id = synonym("SkinActivaId")

    # relación inversa con inventario (útil en móvil)
    inventory = relationship("Inventario", back_populates="estudiante", cascade="all, delete-orphan")

class Asignatura(Base):
    __tablename__ = "asignatura"
    idAsignatura = Column(SmallInteger, primary_key=True)
    Nombre       = Column(String(50))

class Unidad(Base):
    __tablename__ = "unidad"
    idUnidad = Column(SmallInteger, primary_key=True)
    Numero = Column(DECIMAL(3,1))
    Descripcion = Column(String(100))
    AsignaturaId = Column(SmallInteger, ForeignKey("asignatura.idAsignatura"), nullable=False)

    # relaciones
    sesiones = relationship("Sesion", back_populates="unidad")

    # alias snake_case (móvil)
    id            = synonym("idUnidad")
    numero        = synonym("Numero")
    descripcion   = synonym("Descripcion")
    asignatura_id = synonym("AsignaturaId")

class Sesion(Base):
    __tablename__ = "sesion"
    idSesion            = Column(Integer, primary_key=True)
    Bitacora            = Column(String(100))
    ObjetivoAprendizaje = Column(String(150))
    UnidadId            = Column(SmallInteger, ForeignKey("unidad.idUnidad"), nullable=False)

    # alias snake_case (móvil)
    id                   = synonym("idSesion")
    bitacora             = synonym("Bitacora")
    objetivo_aprendizaje = synonym("ObjetivoAprendizaje")
    unidad_id            = synonym("UnidadId")

    # relaciones
    unidad             = relationship("Unidad", back_populates="sesiones")
    tests              = relationship("Test", back_populates="sesion")
    registrosEmocional = relationship("RegistroEmocional", back_populates="sesion")

class Test(Base):
    __tablename__ = "test"
    idTest      = Column(SmallInteger, primary_key=True)
    Puntaje     = Column(SmallInteger, nullable=False)
    Descripcion = Column(String(100))
    SesionId    = Column(Integer, ForeignKey("sesion.idSesion"), nullable=False)

    # alias snake_case (móvil)
    id          = synonym("idTest")
    puntaje     = synonym("Puntaje")
    descripcion = synonym("Descripcion")
    sesion_id   = synonym("SesionId")

    # relaciones
    sesion    = relationship("Sesion", back_populates="tests")
    preguntas = relationship(
        "Pregunta",
        secondary="test_has_pregunta",
        back_populates="tests",
        lazy="joined"
    )

class Pregunta(Base):
    __tablename__ = "pregunta"
    idPregunta = Column(SmallInteger, primary_key=True)
    Tipo       = Column(SqlEnum(TipoPreguntaEnum), nullable=False)
    Puntaje    = Column(SmallInteger, nullable=False)

    # alias snake_case
    id      = synonym("idPregunta")
    tipo    = synonym("Tipo")
    puntaje = synonym("Puntaje")

    # relaciones
    tests        = relationship(
        "Test",
        secondary="test_has_pregunta",
        back_populates="preguntas"
    )
    alternativas = relationship("PAlternativas", uselist=False, back_populates="pregunta", lazy="joined")
    desarrollo   = relationship("PDesarrollo",  uselist=False, back_populates="pregunta", lazy="joined")


class SeccionP(Base):
    __tablename__ = "seccion_p"
    idSeccionP  = Column(Integer, primary_key=True, autoincrement=True)
    Foto        = Column(BLOB)
    Descripcion = Column(String(100))

class PAlternativas(Base):
    __tablename__ = "p_alternativas"
    idPregunta = Column(SmallInteger, ForeignKey("pregunta.idPregunta"), primary_key=True)
    Enunciado  = Column(String(100))
    PA         = Column(String(45))
    PB         = Column(String(45))
    PC         = Column(String(45))
    PD         = Column(String(45))
    Correcta   = Column(String(45))
    SeccionPId = Column(Integer, ForeignKey("seccion_p.idSeccionP"), nullable=False)

    # alias snake_case (móvil)
    enunciado    = synonym("Enunciado")
    p_a          = synonym("PA")
    p_b          = synonym("PB")
    p_c          = synonym("PC")
    p_d          = synonym("PD")
    correcta     = synonym("Correcta")
    seccion_p_id = synonym("SeccionPId")

    # relación inversa
    pregunta = relationship("Pregunta", back_populates="alternativas")

class PDesarrollo(Base):
    __tablename__ = "p_desarrollo"
    idPDesarrollo     = Column(Integer, primary_key=True, autoincrement=True)
    idPregunta        = Column(SmallInteger, ForeignKey("pregunta.idPregunta"), nullable=False)
    Enunciado         = Column(String(100), nullable=False)
    RespuestaEsperada = Column(Text, nullable=False)
    SeccionPId        = Column(Integer, ForeignKey("seccion_p.idSeccionP"), nullable=False)

    # alias snake_case (móvil)
    enunciado          = synonym("Enunciado")
    respuesta_esperada = synonym("RespuestaEsperada")
    seccion_p_id       = synonym("SeccionPId")

    # relación inversa
    pregunta = relationship("Pregunta", back_populates="desarrollo")

class TestPregunta(Base):
    __tablename__ = "test_has_pregunta"
    TestId     = Column(SmallInteger, ForeignKey("test.idTest"), primary_key=True)
    PreguntaId = Column(SmallInteger, ForeignKey("pregunta.idPregunta"), primary_key=True)

    # alias para móvil
    test_id     = synonym("TestId")
    pregunta_id = synonym("PreguntaId")

class Desempeno(Base):
    __tablename__ = "desempeno"
    EstudianteRUT = Column(String(12), ForeignKey("estudiante.RUT"), primary_key=True)
    TestId = Column(SmallInteger, ForeignKey("test.idTest"), primary_key=True)
    NotaTest = Column(SmallInteger, nullable=False)
    Desempenio = Column(String(50))
    FechaEvaluacion = Column(Date, nullable=False)

    # alias móvil
    nota_test        = synonym("NotaTest")
    fecha_evaluacion = synonym("FechaEvaluacion")

class Notas(Base):
    __tablename__ = "notas"
    EstudianteRUT = Column(String(12), ForeignKey("estudiante.RUT"), primary_key=True)
    AsignaturaId = Column(SmallInteger, ForeignKey("asignatura.idAsignatura"), primary_key=True)
    Nota = Column(SmallInteger, nullable=False)
    FechaEvaluacion = Column(Date, nullable=False)

    # alias móvil
    asignatura_id    = synonym("AsignaturaId")
    nota             = synonym("Nota")
    fecha_evaluacion = synonym("FechaEvaluacion")

class Item(Base):
    __tablename__ = "item"
    idItem = Column(SmallInteger, primary_key=True)
    Nombre = Column(String(50))
    Descripcion = Column(String(100))
    Costo = Column(Integer, nullable=False)
    Imagen = Column(String(255))  # ruta (main)

    # alias móviles
    id          = synonym("idItem")
    nombre      = synonym("Nombre")
    descripcion = synonym("Descripcion")
    costo       = synonym("Costo")
    # mapear asset_ref de móvil a Imagen de BD (sin tocar el esquema)
    asset_ref   = synonym("Imagen")

    inventarios = relationship("Inventario", back_populates="item")

class Inventario(Base):
    __tablename__ = "inventario"
    EstudianteRUT = Column(String(12), ForeignKey("estudiante.RUT"), primary_key=True)
    ItemId = Column(SmallInteger, ForeignKey("item.idItem"), primary_key=True)
    Cantidad = Column(SmallInteger, default=1)

    # alias móviles
    item_id  = synonym("ItemId")
    cantidad = synonym("Cantidad")

    # relaciones útiles
    estudiante = relationship("Estudiante", back_populates="inventory")
    item = relationship("Item", back_populates="inventarios")

class Emocion(Base):
    __tablename__ = "emocion"
    idEmocion = Column(Integer, primary_key=True, autoincrement=True)
    Tipo      = Column(String(50))
    EscalaMax = Column(SmallInteger)

    # alias móviles
    id         = synonym("idEmocion")
    tipo       = synonym("Tipo")
    escala_max = synonym("EscalaMax")

class RegistroEmocional(Base):
    __tablename__ = "estudiante_has_emocion"
    id = Column(Integer, primary_key=True, autoincrement=True)
    EstudianteRUT = Column(String(12), ForeignKey("estudiante.RUT"), nullable=False)
    EmocionId = Column(Integer, ForeignKey("emocion.idEmocion"), nullable=False)
    Tipo = Column(SqlEnum(TipoEmocionEnum), nullable=False)
    Escala = Column(SmallInteger, nullable=False)
    Contexto = Column(Text, nullable=True)
    Resumen = Column(Text, nullable=True)
    Fecha = Column(DateTime, nullable=False)
    SesionId = Column(Integer, ForeignKey("sesion.idSesion"), nullable=False)

    # alias móviles
    estudiante_rut = synonym("EstudianteRUT")
    emocion_id     = synonym("EmocionId")
    tipo           = synonym("Tipo")
    escala         = synonym("Escala")
    contexto       = synonym("Contexto")
    resumen        = synonym("Resumen")
    fecha          = synonym("Fecha")
    sesion_id      = synonym("SesionId")

    sesion = relationship("Sesion", back_populates="registrosEmocional")

# ---------- MATERIALES (main) -----------------------------------------------
class Material(Base):
    __tablename__ = "material"
    idMaterial   = Column(Integer, primary_key=True, autoincrement=True)
    Titulo       = Column(String(255), nullable=False)
    Descripcion  = Column(Text, nullable=True)
    ArchivoPath  = Column(String(512), nullable=False)
    CursoId      = Column(SmallInteger, ForeignKey("curso.idCurso"), nullable=False)
    ProfesorRUT  = Column(String(12), ForeignKey("profesor.RUT"), nullable=False)
    SubidoEn     = Column(DateTime, nullable=False)

    curso    = relationship("Curso", lazy="joined")
    profesor = relationship("Profesor", lazy="joined")


class AnalisisDesempeno(Base):
    __tablename__ = "analisis_desempeno"
    id = Column(Integer, primary_key=True, autoincrement=True)
    rut_estudiante = Column(String(12), ForeignKey("estudiante.RUT", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    id_unidad = Column(SmallInteger, ForeignKey("unidad.idUnidad", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    promedio_emocion = Column(DECIMAL(3,2))
    promedio_nota = Column(DECIMAL(4,2))
    interpretacion_ia = Column(Text)
    fecha_analisis = Column(DateTime, server_default="CURRENT_TIMESTAMP")

    estudiante = relationship("Estudiante", backref="analisis_desempeno")
    unidad = relationship("Unidad", backref="analisis_desempeno")


class RegistroIA(Base):
    __tablename__ = "registro_ia"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rut_estudiante = Column(String(12), ForeignKey("estudiante.RUT", ondelete="CASCADE"), nullable=False)
    sesion_id = Column(Integer, ForeignKey("sesion.idSesion", ondelete="CASCADE"), nullable=True)

    remitente = Column(SqlEnum("estudiante", "aurora"), nullable=False)
    mensaje = Column(Text, nullable=False)
    contexto = Column(String(100), nullable=True)
    fecha_hora = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    estudiante = relationship("Estudiante", backref="registros_ia")
    sesion = relationship("Sesion", backref="registros_ia")


class ChequeoEmocional(Base):
    __tablename__ = "chequeo_emocional"
    id = Column(Integer, primary_key=True, autoincrement=True)
    rut_estudiante = Column(String(12), ForeignKey("estudiante.RUT", ondelete="CASCADE"), nullable=False)
    emocion_id = Column(Integer, ForeignKey("emocion.idEmocion", ondelete="CASCADE"), nullable=False)
    escala = Column(SmallInteger, nullable=False)
    comentario = Column(Text, nullable=True)
    fecha = Column(DateTime, server_default="CURRENT_TIMESTAMP")

    estudiante = relationship("Estudiante", backref="chequeos_emocionales")
    emocion = relationship("Emocion", backref="chequeos_emocionales")


if __name__ == "__main__":
    from database import engine
    Base.metadata.create_all(bind=engine)
