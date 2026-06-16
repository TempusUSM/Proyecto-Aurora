from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime

# ==== AUTH / LOGIN ====
class LoginRequest(BaseModel):
    rut: str = Field(..., example="12345678-9")


# ==== PERSONA ====
class PersonaBase(BaseModel):
    rut: str = Field(alias="RUT")
    nombres: str = Field(alias="Nombres")
    apellido_paterno: str = Field(alias="ApellidoPaterno")
    apellido_materno: str = Field(alias="ApellidoMaterno")
    comuna_id: int = Field(alias="ComunaId")
    telefono: Optional[str] = Field(alias="Telefono", default=None)
    correo: Optional[str] = Field(alias="Correo", default=None)
    direccion: Optional[str] = Field(alias="Direccion", default=None)
    fecha_nacimiento: Optional[date] = Field(alias="FechaNacimiento", default=None)
    genero: Optional[str] = Field(alias="Genero", default=None)
    estado: Optional[str] = Field(alias="Estado", default=None)

    class Config:
        from_attributes = True
        populate_by_name = True

class PersonaCreate(PersonaBase):
    pass

class Persona(PersonaBase):
    pass


# ==== ESTUDIANTE ====
class EstudianteBase(BaseModel):
    rut: str = Field(..., alias="RUT")
    apoderado_rut: Optional[str] = Field(None, alias="ApoderadoRUT")
    curso_id: Optional[int] = Field(None, alias="CursoId")
    puntos: Optional[int] = Field(0, alias="Puntos")
    promedio_general: Optional[int] = Field(0, alias="PromedioGeneral")
    # id del item aplicado (si existe en BD)
    skin_activa_id: Optional[int] = Field(None, alias="SkinActivaId")

    class Config:
        from_attributes = True
        populate_by_name = True

class EstudianteCreate(EstudianteBase):
    pass

class Estudiante(EstudianteBase):
    pass


# ==== ASIGNATURA ====
class AsignaturaBase(BaseModel):
    nombre: str = Field(..., alias="Nombre")

    class Config:
        from_attributes = True
        populate_by_name = True

class AsignaturaCreate(AsignaturaBase):
    pass

class Asignatura(AsignaturaBase):
    id: int = Field(..., alias="idAsignatura")


# ==== UNIDAD ====
class UnidadBase(BaseModel):
    numero: float = Field(..., alias="Numero")
    descripcion: str = Field(..., alias="Descripcion")
    asignatura_id: int = Field(..., alias="AsignaturaId")

    class Config:
        from_attributes = True
        populate_by_name = True

class UnidadCreate(UnidadBase):
    pass

class Unidad(UnidadBase):
    id: int = Field(..., alias="idUnidad")


# ==== SESION ====
class SesionBase(BaseModel):
    bitacora: Optional[str] = Field(None, alias="Bitacora")
    objetivo_aprendizaje: Optional[str] = Field(None, alias="ObjetivoAprendizaje")
    unidad_id: int = Field(..., alias="UnidadId")

    class Config:
        from_attributes = True
        populate_by_name = True

class SesionCreate(SesionBase):
    pass

class SesionResponse(SesionBase):
    id: int = Field(..., alias="idSesion")


# ==== EMOCION ====
class EmocionBase(BaseModel):
    tipo: str = Field(..., alias="Tipo")
    escala_max: int = Field(..., alias="EscalaMax")

    class Config:
        from_attributes = True
        populate_by_name = True

class EmocionCreate(EmocionBase):
    pass

class Emocion(EmocionBase):
    id: int = Field(..., alias="idEmocion")


# ==== REGISTRO EMOCIONAL (compat web + móvil) ====
# Campos snake_case con alias a columnas DB (CamelCase)
class RegistroEmocionalBase(BaseModel):
    estudiante_rut: str = Field(..., alias="EstudianteRUT")
    emocion_id: int = Field(..., alias="EmocionId")
    tipo: str = Field(..., alias="Tipo")                  # 'pre' | 'post'
    escala: int = Field(..., alias="Escala")
    contexto: Optional[str] = Field(None, alias="Contexto")
    resumen: Optional[str] = Field(None, alias="Resumen")
    fecha: Optional[datetime] = Field(None, alias="Fecha")
    sesion_id: int = Field(..., alias="SesionId")

    class Config:
        from_attributes = True
        populate_by_name = True

class RegistroEmocionalCreate(RegistroEmocionalBase):
    pass

class RegistroEmocional(RegistroEmocionalBase):
    id: int = Field(..., alias="id")


# ==== TEST ====
class TestBase(BaseModel):
    puntaje: int = Field(..., alias="Puntaje")
    descripcion: Optional[str] = Field(None, alias="Descripcion")
    sesion_id: int = Field(..., alias="SesionId")

    class Config:
        from_attributes = True
        populate_by_name = True

class TestCreate(TestBase):
    pass

class TestResponse(TestBase):
    id: int = Field(..., alias="idTest")


# ==== SECCION P ====
class SeccionPBase(BaseModel):
    foto: Optional[bytes] = Field(None, alias="Foto")
    descripcion: Optional[str] = Field(None, alias="Descripcion")

    class Config:
        from_attributes = True
        populate_by_name = True

class SeccionPCreate(SeccionPBase):
    pass

class SeccionP(SeccionPBase):
    id: int = Field(..., alias="idSeccionP")


# ==== PREGUNTA ====
class PreguntaBase(BaseModel):
    tipo: str = Field(..., alias="Tipo")
    puntaje: int = Field(..., alias="Puntaje")

    class Config:
        from_attributes = True
        populate_by_name = True

class PreguntaCreate(PreguntaBase):
    pass

class Pregunta(PreguntaBase):
    id: int = Field(..., alias="idPregunta")


# ==== PREGUNTA ALTERNATIVAS ====
class PAlternativasBase(BaseModel):
    id_pregunta: int = Field(..., alias="idPregunta")
    enunciado: str = Field(..., alias="Enunciado")
    pa: str = Field(..., alias="PA")
    pb: str = Field(..., alias="PB")
    pc: str = Field(..., alias="PC")
    pd: str = Field(..., alias="PD")
    correcta: str = Field(..., alias="Correcta")
    seccionp_id: int = Field(..., alias="SeccionPId")

    class Config:
        from_attributes = True
        populate_by_name = True

class PAlternativasCreate(PAlternativasBase):
    pass

class PAlternativas(PAlternativasBase):
    id: Optional[int] = None  # PK es idPregunta


# ==== PREGUNTA DESARROLLO ====
class PDesarrolloBase(BaseModel):
    id_pregunta: int = Field(..., alias="idPregunta")
    enunciado: str = Field(..., alias="Enunciado")
    respuesta_esperada: str = Field(..., alias="RespuestaEsperada")
    seccionp_id: int = Field(..., alias="SeccionPId")

    class Config:
        from_attributes = True
        populate_by_name = True

class PDesarrolloCreate(PDesarrolloBase):
    pass

class PDesarrollo(PDesarrolloBase):
    id: int = Field(..., alias="idPDesarrollo")


# ==== TEST PREGUNTA ====
class TestPreguntaBase(BaseModel):
    test_id: int = Field(..., alias="TestId")
    pregunta_id: int = Field(..., alias="PreguntaId")

    class Config:
        from_attributes = True
        populate_by_name = True

class TestPreguntaCreate(TestPreguntaBase):
    pass

class TestPregunta(TestPreguntaBase):
    pass


# ==== DESEMPEÑO ====
class DesempenoBase(BaseModel):
    estudiante_rut: str = Field(..., alias="EstudianteRUT")
    test_id: int = Field(..., alias="TestId")
    nota_test: int = Field(..., alias="NotaTest")
    desempenio: Optional[str] = Field(None, alias="Desempenio")
    fecha_evaluacion: date = Field(..., alias="FechaEvaluacion")

    class Config:
        from_attributes = True
        populate_by_name = True

class DesempenoCreate(DesempenoBase):
    pass

class Desempeno(DesempenoBase):
    pass


# ==== NOTAS ====
class NotasBase(BaseModel):
    estudiante_rut: str = Field(..., alias="EstudianteRUT")
    asignatura_id: int = Field(..., alias="AsignaturaId")
    nota: int = Field(..., alias="Nota")
    fecha_evaluacion: date = Field(..., alias="FechaEvaluacion")

    class Config:
        from_attributes = True
        populate_by_name = True

class NotasCreate(NotasBase):
    pass

class Notas(NotasBase):
    pass


# ==== ITEM ====
class ItemBase(BaseModel):
    nombre: str = Field(..., alias="Nombre")
    descripcion: Optional[str] = Field(None, alias="Descripcion")
    costo: int = Field(..., alias="Costo")
    imagen: Optional[str] = Field(None, alias="Imagen")  # ruta (si existe en BD)

    class Config:
        from_attributes = True
        populate_by_name = True

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int = Field(..., alias="idItem")


# ==== INVENTARIO ====
class InventarioBase(BaseModel):
    estudiante_rut: str = Field(..., alias="EstudianteRUT")
    item_id: int = Field(..., alias="ItemId")
    cantidad: int = Field(..., alias="Cantidad")

    class Config:
        from_attributes = True
        populate_by_name = True

class InventarioCreate(InventarioBase):
    pass

class Inventario(InventarioBase):
    pass


# ==== PAIS ====
class PaisBase(BaseModel):
    nombre: str = Field(..., alias="Nombre")

    class Config:
        from_attributes = True
        populate_by_name = True

class PaisCreate(PaisBase):
    pass

class Pais(PaisBase):
    id: int = Field(..., alias="idPais")


# ==== REGION ====
class RegionBase(BaseModel):
    nombre: str = Field(..., alias="Nombre")
    pais_id: int = Field(..., alias="PaisId")

    class Config:
        from_attributes = True
        populate_by_name = True

class RegionCreate(RegionBase):
    pass

class Region(RegionBase):
    id: int = Field(..., alias="idRegion")


# ==== PROVINCIA ====
class ProvinciaBase(BaseModel):
    nombre: str = Field(..., alias="Nombre")
    region_id: int = Field(..., alias="RegionId")

    class Config:
        from_attributes = True
        populate_by_name = True

class ProvinciaCreate(ProvinciaBase):
    pass

class Provincia(ProvinciaBase):
    id: int = Field(..., alias="idProvincia")


# ==== COMUNA ====
class ComunaBase(BaseModel):
    nombre: str = Field(..., alias="Nombre")
    provincia_id: int = Field(..., alias="ProvinciaId")

    class Config:
        from_attributes = True
        populate_by_name = True

class ComunaCreate(ComunaBase):
    pass

class Comuna(ComunaBase):
    id: int = Field(..., alias="idComuna")


# ==== COLEGIO ====
class ColegioBase(BaseModel):
    nombre: str = Field(..., alias="Nombre")
    ubicacion: Optional[str] = Field(None, alias="Ubicacion")
    telefono: Optional[str] = Field(None, alias="Telefono")
    comuna_id: int = Field(..., alias="ComunaId")

    class Config:
        from_attributes = True
        populate_by_name = True

class ColegioCreate(ColegioBase):
    pass

class Colegio(ColegioBase):
    id: int = Field(..., alias="idColegio")


# ==== CURSO ====
class CursoBase(BaseModel):
    grado: str = Field(..., alias="Grado")
    etapa: str = Field(..., alias="Etapa")
    letra: str = Field(..., alias="Letra")
    profesor_jefe_rut: str = Field(..., alias="ProfesorJefeRUT")

    class Config:
        from_attributes = True
        populate_by_name = True

class CursoCreate(CursoBase):
    pass

class Curso(CursoBase):
    id: int = Field(..., alias="idCurso")


# ==== CURSO UNIDAD ====
class CursoUnidadBase(BaseModel):
    curso_id: int = Field(..., alias="CursoId")
    unidad_id: int = Field(..., alias="UnidadId")

    class Config:
        from_attributes = True
        populate_by_name = True

class CursoUnidadCreate(CursoUnidadBase):
    pass

class CursoUnidad(CursoUnidadBase):
    pass


# ==== ROL ====
class RolBase(BaseModel):
    nombre: str = Field(..., alias="Nombre")

    class Config:
        from_attributes = True
        populate_by_name = True

class RolCreate(RolBase):
    pass

class Rol(RolBase):
    id: int = Field(..., alias="idRol")


# ==== PERSONA ROL ====
class PersonaRolBase(BaseModel):
    persona_rut: str = Field(..., alias="PersonaRUT")
    rol_id: int = Field(..., alias="RolId")
    colegio_id: int = Field(..., alias="ColegioId")

    class Config:
        from_attributes = True
        populate_by_name = True

class PersonaRolCreate(PersonaRolBase):
    pass

class PersonaRol(PersonaRolBase):
    pass


# ==== PROFESOR ====
class ProfesorBase(BaseModel):
    rut: str = Field(..., alias="RUT")
    especialidad: Optional[str] = Field(None, alias="Especialidad")
    titulo_profesional: Optional[str] = Field(None, alias="TituloProfesional")

    class Config:
        from_attributes = True
        populate_by_name = True

class ProfesorCreate(ProfesorBase):
    pass

class Profesor(ProfesorBase):
    pass


# ==== APODERADO ====
class ApoderadoBase(BaseModel):
    rut: str = Field(..., alias="RUT")
    parentesco: Optional[str] = Field(None, alias="Parentesco")

    class Config:
        from_attributes = True
        populate_by_name = True

class ApoderadoCreate(ApoderadoBase):
    pass

class Apoderado(ApoderadoBase):
    pass


# ==== MATERIAL ====
class MaterialBase(BaseModel):
    titulo: str                = Field(..., alias="Titulo")
    descripcion: Optional[str] = Field(None, alias="Descripcion")
    archivo_path: str          = Field(..., alias="ArchivoPath")
    curso_id: int              = Field(..., alias="CursoId")
    profesor_rut: str          = Field(..., alias="ProfesorRUT")
    subido_en: Optional[datetime] = Field(None, alias="SubidoEn")

    class Config:
        from_attributes = True
        populate_by_name = True

class MaterialCreate(MaterialBase):
    pass

class Material(MaterialBase):
    id: int = Field(..., alias="idMaterial")
