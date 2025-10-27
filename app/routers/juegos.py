from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import SuccessResponse, ErrorResponse, CompletarJuegoResponse
from app.crud import add_estrellas, get_estado
from typing import Union

router = APIRouter(prefix="/api", tags=["juegos"])

@router.post("/completar-juego", response_model=Union[SuccessResponse, ErrorResponse])
async def completar_juego_bonus(db: Session = Depends(get_db)):
    """
    Otorga bonus de 15 estrellas por completar un juego.
    
    Retorna:
    - nuevas_estrellas: Total de estrellas después del bonus
    - mensaje: Mensaje de confirmación
    
    Este endpoint puede ser llamado cada vez que el usuario
    complete algún juego o actividad en el frontend.
    """
    try:
        # Añadir 15 estrellas como bonus
        estado = add_estrellas(db, 15)
        
        completar_response = CompletarJuegoResponse(
            nuevas_estrellas=estado.estrellas,
            mensaje="Ganaste 15 estrellas por jugar"
        )
        
        return SuccessResponse(
            success=True,
            data=completar_response.dict(),
            message="Bonus de juego otorgado exitosamente"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar el bonus del juego: {str(e)}"
        )