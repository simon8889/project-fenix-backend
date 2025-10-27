from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import SuccessResponse, ErrorResponse, PremioResponse, ReclamarPremioRequest, ReclamarPremioResponse
from app.crud import get_premios_data, get_estado, procesar_reclamar_premio
from typing import Union, List

router = APIRouter(prefix="/api", tags=["premios"])

@router.get("/premios", response_model=Union[SuccessResponse, ErrorResponse])
async def get_todos_los_premios(db: Session = Depends(get_db)):
    """
    Retorna todos los premios con estado.
    
    Retorna:
    - Lista de premios con id, nombre, costo, emoji, disponible, reclamado (boolean)
    - Marca 'reclamado' si el ID está en premios_reclamados del estado
    """
    try:
        # Obtener datos de premios desde JSON
        premios_data = get_premios_data()
        if not premios_data:
            raise HTTPException(
                status_code=404,
                detail="No se pudieron cargar los datos de premios"
            )
        
        # Obtener estado para verificar premios reclamados
        estado = get_estado(db)
        premios_reclamados = estado.premios_reclamados or []
        premios_reclamados_ids = [premio["premio_id"] for premio in premios_reclamados]
        
        # Construir respuesta con metadata
        premios_response = []
        for premio in premios_data:
            premio_response = PremioResponse(
                id=premio["id"],
                nombre=premio["nombre"],
                costo=premio["costo"],
                emoji=premio["emoji"],
                disponible=premio.get("disponible", True),
                reclamado=premio["id"] in premios_reclamados_ids
            )
            premios_response.append(premio_response.dict())
        
        # Ordenar por costo para mejor UX
        premios_response.sort(key=lambda x: x["costo"])
        
        return SuccessResponse(
            success=True,
            data=premios_response,
            message=f"Se encontraron {len(premios_response)} premios"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los premios: {str(e)}"
        )

@router.post("/reclamar-premio", response_model=Union[SuccessResponse, ErrorResponse])
async def reclamar_premio(
    request: ReclamarPremioRequest,
    db: Session = Depends(get_db)
):
    """
    Reclama un premio canjeando estrellas.
    
    Body:
    - premio_id: ID del premio a reclamar
    
    Validaciones:
    - Verifica que tenga suficientes estrellas
    - Verifica que el premio exista y no haya sido reclamado
    
    Retorna:
    - estrellas_restantes: Estrellas restantes después del canje
    - premio: Información del premio reclamado
    - mensaje: Mensaje de confirmación
    
    Errores:
    - 400 si no tiene suficientes estrellas
    - 400 si el premio no existe o ya fue reclamado
    """
    try:
        resultado = procesar_reclamar_premio(db, request.premio_id)
        
        reclamar_response = ReclamarPremioResponse(
            estrellas_restantes=resultado["estrellas_restantes"],
            premio=resultado["premio"],
            mensaje=resultado["mensaje"]
        )
        
        return SuccessResponse(
            success=True,
            data=reclamar_response.dict(),
            message="Premio reclamado exitosamente"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al reclamar el premio: {str(e)}"
        )