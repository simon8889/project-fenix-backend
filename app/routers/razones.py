from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import SuccessResponse, ErrorResponse, RazonResponse
from app.crud import get_razones_data, get_estado
from typing import Union, List

router = APIRouter(prefix="/api", tags=["razones"])

@router.get("/razones", response_model=Union[SuccessResponse, ErrorResponse])
async def get_razones_desbloqueadas(db: Session = Depends(get_db)):
    """
    Retorna solo las razones desbloqueadas.
    
    Retorna:
    - Lista de razones desbloqueadas con id, texto, emoji, categoria, puntos_requeridos
    - Filtra razones.json por IDs en razones_desbloqueadas del estado
    """
    try:
        # Obtener estado para verificar razones desbloqueadas
        estado = get_estado(db)
        razones_desbloqueadas_ids = estado.razones_desbloqueadas or []
        
        # Si no hay razones desbloqueadas, retornar lista vacía
        if not razones_desbloqueadas_ids:
            return SuccessResponse(
                success=True,
                data=[],
                message="No hay razones desbloqueadas aún"
            )
        
        # Obtener datos de razones desde JSON
        todas_las_razones = get_razones_data()
        if not todas_las_razones:
            raise HTTPException(
                status_code=404,
                detail="No se pudieron cargar los datos de razones"
            )
        
        # Filtrar solo las razones desbloqueadas
        razones_desbloqueadas = []
        for razon in todas_las_razones:
            if razon["id"] in razones_desbloqueadas_ids:
                razon_response = RazonResponse(
                    id=razon["id"],
                    texto=razon["texto"],
                    emoji=razon["emoji"],
                    categoria=razon["categoria"],
                    puntos_requeridos=razon["puntos_requeridos"]
                )
                razones_desbloqueadas.append(razon_response.dict())
        
        # Ordenar por puntos_requeridos para mejor UX
        razones_desbloqueadas.sort(key=lambda x: x["puntos_requeridos"])
        
        return SuccessResponse(
            success=True,
            data=razones_desbloqueadas,
            message=f"Se encontraron {len(razones_desbloqueadas)} razones desbloqueadas"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener las razones: {str(e)}"
        )