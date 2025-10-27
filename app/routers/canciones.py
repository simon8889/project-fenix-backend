from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud import add_estrellas
from typing import List
import json
import os

router = APIRouter(prefix="/api", tags=["canciones"])

# Ruta al archivo de canciones
CANCIONES_FILE = os.path.join("data", "canciones.json")

def cargar_canciones() -> List[dict]:
    """
    Carga las canciones desde el archivo JSON.
    """
    try:
        if not os.path.exists(CANCIONES_FILE):
            return []
        
        with open(CANCIONES_FILE, 'r', encoding='utf-8') as f:
            canciones = json.load(f)
            return canciones
    except Exception as e:
        print(f"Error al cargar canciones: {str(e)}")
        return []

@router.get("/canciones")
async def get_canciones():
    """
    Obtiene todas las canciones de la playlist especial.
    
    Returns:
        - **success**: Indica si la operación fue exitosa
        - **data**: Lista de canciones con nombre, artista, link y motivo
    
    Cada canción contiene:
    - **id**: Identificador único de la canción
    - **nombre**: Título de la canción
    - **artista**: Nombre del artista o grupo
    - **link**: URL de Spotify para escuchar la canción
    - **motivo**: Razón romántica de por qué esta canción es especial
    """
    try:
        canciones = cargar_canciones()
        
        return {
            "success": True,
            "data": canciones,
            "total": len(canciones)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener canciones: {str(e)}"
        )

@router.get("/canciones/{cancion_id}")
async def get_cancion(cancion_id: int):
    """
    Obtiene una canción específica por su ID.
    
    Args:
        - **cancion_id**: ID de la canción a obtener
    
    Returns:
        - **success**: Indica si la operación fue exitosa
        - **data**: Datos de la canción solicitada
    """
    try:
        canciones = cargar_canciones()
        
        cancion = next((c for c in canciones if c["id"] == cancion_id), None)
        
        if not cancion:
            raise HTTPException(
                status_code=404,
                detail=f"Canción con ID {cancion_id} no encontrada"
            )
        
        return {
            "success": True,
            "data": cancion
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener la canción: {str(e)}"
        )

@router.post("/escuchar-cancion")
async def escuchar_cancion(db: Session = Depends(get_db)):
    """
    Otorga 1 estrella cada vez que se hace clic en escuchar una canción.
    No importa si ya se escuchó antes, siempre da 1 estrella.
    
    Returns:
        - nuevas_estrellas: Total de estrellas después de escuchar
        - mensaje: Mensaje de confirmación
    """
    try:
        # Dar 1 estrella
        estado = add_estrellas(db, 1)
        
        return {
            "success": True,
            "data": {
                "nuevas_estrellas": estado.estrellas,
                "mensaje": "Ganaste 1 estrella"
            },
            "message": "Estrella otorgada exitosamente"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar la canción: {str(e)}"
        )
