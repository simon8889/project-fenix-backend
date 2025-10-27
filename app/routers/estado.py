from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import SuccessResponse, ErrorResponse, EstadoResponse, PuntoResponse
from app.crud import get_estado, procesar_dar_punto
from typing import Union

router = APIRouter(prefix="/api", tags=["estado"])

@router.get("/estado", response_model=Union[SuccessResponse, ErrorResponse])
async def get_estado_app(db: Session = Depends(get_db)):
    """
    Obtiene el estado completo de la aplicación.
    
    Retorna:
    - puntos_consideracion: Puntos acumulados
    - estrellas: Estrellas disponibles para canjear
    - razones_desbloqueadas: IDs de razones desbloqueadas
    - cartas_leidas: IDs de cartas ya leídas
    - premios_reclamados: Premios canjeados con timestamps
    """
    try:
        estado = get_estado(db)
        estado_data = EstadoResponse(
            puntos_consideracion=estado.puntos_consideracion,
            estrellas=estado.estrellas,
            razones_desbloqueadas=estado.razones_desbloqueadas or [],
            cartas_leidas=estado.cartas_leidas or [],
            premios_reclamados=estado.premios_reclamados or []
        )
        
        return SuccessResponse(
            success=True,
            data=estado_data.dict(),
            message="Estado obtenido exitosamente"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.post("/dar-punto", response_model=Union[SuccessResponse, ErrorResponse])
async def dar_punto_consideracion(db: Session = Depends(get_db)):
    """
    Incrementa los puntos de consideración en 1.
    Desbloquea razones nuevas basado en puntos_requeridos de cada razón.
    
    Retorna:
    - nuevo_total_puntos: Total de puntos después del incremento
    - razones_recien_desbloqueadas: Lista de razones que se acaban de desbloquear
    """
    try:
        resultado = procesar_dar_punto(db)
        
        punto_response = PuntoResponse(
            nuevo_total_puntos=resultado["nuevo_total_puntos"],
            razones_recien_desbloqueadas=resultado["razones_recien_desbloqueadas"]
        )
        
        return SuccessResponse(
            success=True,
            data=punto_response.dict(),
            message="Punto de consideración agregado exitosamente"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar el punto: {str(e)}"
        )