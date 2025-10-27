from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime

# =====================================
# SCHEMAS DE RESPONSE (OUTPUT)
# =====================================

class EstadoResponse(BaseModel):
    """Schema para la respuesta del estado de la app"""
    puntos_consideracion: int = Field(..., description="Puntos de consideración acumulados")
    estrellas: int = Field(..., description="Estrellas disponibles para canjear")
    razones_desbloqueadas: List[int] = Field(default=[], description="IDs de razones desbloqueadas")
    cartas_leidas: List[int] = Field(default=[], description="IDs de cartas ya leídas")
    premios_reclamados: List[Dict[str, Any]] = Field(default=[], description="Premios reclamados con timestamps")

class PuntoResponse(BaseModel):
    """Schema para la respuesta al dar un punto"""
    nuevo_total_puntos: int = Field(..., description="Nuevo total de puntos de consideración")
    razones_recien_desbloqueadas: List[Dict[str, Any]] = Field(default=[], description="Razones recién desbloqueadas")

class CartaResponse(BaseModel):
    """Schema para una carta individual"""
    id: int = Field(..., description="ID único de la carta")
    titulo: str = Field(..., description="Título de la carta")
    contenido: str = Field(..., description="Contenido de la carta")
    leida: bool = Field(..., description="Si la carta ya fue leída")
    disponible: bool = Field(default=True, description="Si la carta está disponible")

class LeerCartaResponse(BaseModel):
    """Schema para la respuesta al leer una carta"""
    nuevas_estrellas: int = Field(..., description="Total de estrellas después de leer")
    carta_id: int = Field(..., description="ID de la carta leída")
    mensaje: str = Field(default="Ganaste 10 estrellas", description="Mensaje de confirmación")

class RazonResponse(BaseModel):
    """Schema para una razón individual"""
    id: int = Field(..., description="ID único de la razón")
    texto: str = Field(..., description="Texto de la razón")
    emoji: str = Field(..., description="Emoji representativo")
    categoria: str = Field(..., description="Categoría de la razón")
    puntos_requeridos: int = Field(..., description="Puntos necesarios para desbloquear")

class PremioResponse(BaseModel):
    """Schema para un premio individual"""
    id: int = Field(..., description="ID único del premio")
    nombre: str = Field(..., description="Nombre del premio")
    costo: int = Field(..., description="Costo en estrellas")
    emoji: str = Field(..., description="Emoji representativo")
    disponible: bool = Field(default=True, description="Si el premio está disponible")
    reclamado: bool = Field(..., description="Si el premio ya fue reclamado")

class ReclamarPremioResponse(BaseModel):
    """Schema para la respuesta al reclamar un premio"""
    estrellas_restantes: int = Field(..., description="Estrellas restantes después del canje")
    premio: Dict[str, Any] = Field(..., description="Información del premio reclamado")
    mensaje: str = Field(..., description="Mensaje de confirmación")

class CompletarJuegoResponse(BaseModel):
    """Schema para la respuesta al completar un juego"""
    nuevas_estrellas: int = Field(..., description="Total de estrellas después del bonus")
    mensaje: str = Field(default="Ganaste 15 estrellas por jugar", description="Mensaje de confirmación")

# =====================================
# SCHEMAS DE REQUEST (INPUT)
# =====================================

class ReclamarPremioRequest(BaseModel):
    """Schema para la solicitud de reclamar un premio"""
    premio_id: int = Field(..., description="ID del premio a reclamar", gt=0)

    @validator('premio_id')
    def validate_premio_id(cls, v):
        if v <= 0:
            raise ValueError('El ID del premio debe ser mayor a 0')
        return v

# =====================================
# SCHEMAS DE RESPONSE ESTÁNDAR
# =====================================

class SuccessResponse(BaseModel):
    """Schema estándar para respuestas exitosas"""
    success: bool = Field(True, description="Indica si la operación fue exitosa")
    data: Optional[Any] = Field(None, description="Datos de la respuesta")
    message: Optional[str] = Field(None, description="Mensaje opcional")

class ErrorResponse(BaseModel):
    """Schema estándar para respuestas de error"""
    success: bool = Field(False, description="Indica que la operación falló")
    detail: str = Field(..., description="Detalle del error")
    error_code: Optional[str] = Field(None, description="Código de error opcional")

# =====================================
# SCHEMAS AUXILIARES
# =====================================

class CartaData(BaseModel):
    """Schema para datos de carta desde JSON"""
    id: int
    titulo: str
    contenido: str

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class RazonData(BaseModel):
    """Schema para datos de razón desde JSON"""
    id: int
    puntos_requeridos: int
    categoria: str
    texto: str
    emoji: str

class PremioData(BaseModel):
    """Schema para datos de premio desde JSON"""
    id: int
    nombre: str
    costo: int
    emoji: str
    disponible: bool = True

# =====================================
# FUNCIONES DE VALIDACIÓN
# =====================================

def validate_carta_id(carta_id: int, cartas_data: List[Dict]) -> bool:
    """Valida que el ID de carta existe en los datos"""
    return any(carta['id'] == carta_id for carta in cartas_data)

def validate_premio_id(premio_id: int, premios_data: List[Dict]) -> bool:
    """Valida que el ID de premio existe en los datos"""
    return any(premio['id'] == premio_id for premio in premios_data)