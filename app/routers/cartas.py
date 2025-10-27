from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import SuccessResponse, ErrorResponse, CartaResponse, LeerCartaResponse
from app.crud import get_cartas_data, get_estado, procesar_leer_carta
from typing import Union, List

router = APIRouter(prefix="/api", tags=["cartas"])

@router.get("/cartas", response_model=Union[SuccessResponse, ErrorResponse])
async def get_todas_las_cartas(db: Session = Depends(get_db)):
    """
    Retorna todas las 30 cartas con metadata.
    
    Retorna:
    - Lista de cartas con id, titulo, contenido, leida (boolean), disponible (boolean)
    - Marca 'leida' si el ID está en cartas_leidas del estado
    - Todas las cartas siempre están disponibles (sin lógica de fechas)
    """
    try:
        # Obtener datos de cartas desde JSON
        cartas_data = get_cartas_data()
        if not cartas_data:
            raise HTTPException(
                status_code=404,
                detail="No se pudieron cargar los datos de cartas"
            )
        
        # Obtener estado para verificar cartas leídas
        estado = get_estado(db)
        cartas_leidas = estado.cartas_leidas or []
        
        # Construir respuesta con metadata
        cartas_response = []
        for carta in cartas_data:
            carta_response = CartaResponse(
                id=carta["id"],
                titulo=carta["titulo"],
                contenido=carta["contenido"],
                leida=carta["id"] in cartas_leidas,
                disponible=True  # Todas las cartas siempre disponibles
            )
            cartas_response.append(carta_response.dict())
        
        return SuccessResponse(
            success=True,
            data=cartas_response,
            message=f"Se encontraron {len(cartas_response)} cartas"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener las cartas: {str(e)}"
        )

@router.post("/leer-carta/{carta_id}", response_model=Union[SuccessResponse, ErrorResponse])
async def leer_carta(
    carta_id: int = Path(..., description="ID de la carta a leer", gt=0),
    db: Session = Depends(get_db)
):
    """
    Marca una carta como leída y otorga 1 estrella.
    
    Parámetros:
    - carta_id: ID de la carta a marcar como leída
    
    Retorna:
    - nuevas_estrellas: Total de estrellas después de leer
    - carta_id: ID de la carta leída
    - mensaje: Mensaje de confirmación
    
    Validaciones:
    - Verifica que carta_id exista en cartas.json
    - Si ya fue leída, no otorga estrellas adicionales
    """
    try:
        resultado = procesar_leer_carta(db, carta_id)
        
        leer_carta_response = LeerCartaResponse(
            nuevas_estrellas=resultado["nuevas_estrellas"],
            carta_id=resultado["carta_id"],
            mensaje=resultado["mensaje"]
        )
        
        return SuccessResponse(
            success=True,
            data=leer_carta_response.dict(),
            message="Carta procesada exitosamente"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar la carta: {str(e)}"
        )