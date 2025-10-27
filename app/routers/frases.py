from fastapi import APIRouter, HTTPException
from typing import List, Optional
import json
import os
import random

router = APIRouter(prefix="/api", tags=["frases"])

# Ruta al archivo de frases
FRASES_FILE = os.path.join("data", "frases.json")

def cargar_frases() -> List[dict]:
    """
    Carga las frases desde el archivo JSON.
    """
    try:
        if not os.path.exists(FRASES_FILE):
            return []
        
        with open(FRASES_FILE, 'r', encoding='utf-8') as f:
            frases = json.load(f)
            return frases
    except Exception as e:
        print(f"Error al cargar frases: {str(e)}")
        return []

@router.get("/frases")
async def get_frases(categoria: Optional[str] = None):
    """
    Obtiene todas las frases o filtra por categoría.
    
    Args:
        - **categoria** (opcional): Filtrar por categoría (romantica, chiste_bueno, chiste_malo, dato_curioso)
    
    Returns:
        - **success**: Indica si la operación fue exitosa
        - **data**: Lista de frases
        - **total**: Total de frases retornadas
    
    Cada frase contiene:
    - **id**: Identificador único
    - **texto**: Contenido de la frase
    - **categoria**: Tipo de frase (romantica, chiste_bueno, chiste_malo, dato_curioso)
    - **emoji**: Emoji representativo
    """
    try:
        frases = cargar_frases()
        
        # Filtrar por categoría si se especifica
        if categoria:
            frases = [f for f in frases if f.get("categoria") == categoria]
        
        return {
            "success": True,
            "data": frases,
            "total": len(frases)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener frases: {str(e)}"
        )

@router.get("/frases/aleatoria")
async def get_frase_aleatoria(categoria: Optional[str] = None):
    """
    Obtiene una frase aleatoria.
    
    Args:
        - **categoria** (opcional): Filtrar por categoría antes de seleccionar aleatoriamente
    
    Returns:
        - **success**: Indica si la operación fue exitosa
        - **data**: Frase aleatoria seleccionada
    
    Categorías disponibles:
    - **romantica**: Frases románticas y de amor
    - **chiste_bueno**: Chistes divertidos y buenos
    - **chiste_malo**: Chistes malos pero graciosos
    - **dato_curioso**: Datos curiosos sobre animales o ciencia
    """
    try:
        frases = cargar_frases()
        
        if not frases:
            raise HTTPException(
                status_code=404,
                detail="No hay frases disponibles"
            )
        
        # Filtrar por categoría si se especifica
        if categoria:
            frases = [f for f in frases if f.get("categoria") == categoria]
            
            if not frases:
                raise HTTPException(
                    status_code=404,
                    detail=f"No hay frases disponibles en la categoría '{categoria}'"
                )
        
        # Seleccionar una frase aleatoria
        frase_aleatoria = random.choice(frases)
        
        return {
            "success": True,
            "data": frase_aleatoria
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener frase aleatoria: {str(e)}"
        )

@router.get("/frases/{frase_id}")
async def get_frase(frase_id: int):
    """
    Obtiene una frase específica por su ID.
    
    Args:
        - **frase_id**: ID de la frase a obtener
    
    Returns:
        - **success**: Indica si la operación fue exitosa
        - **data**: Datos de la frase solicitada
    """
    try:
        frases = cargar_frases()
        
        frase = next((f for f in frases if f["id"] == frase_id), None)
        
        if not frase:
            raise HTTPException(
                status_code=404,
                detail=f"Frase con ID {frase_id} no encontrada"
            )
        
        return {
            "success": True,
            "data": frase
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener la frase: {str(e)}"
        )
