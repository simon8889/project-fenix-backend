from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models import EstadoApp
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import os

# =====================================
# OPERACIONES CRUD PARA ESTADO_APP
# =====================================

def get_estado(db: Session) -> Optional[EstadoApp]:
    """
    Obtiene el estado actual de la aplicación.
    Si no existe, crea uno nuevo con valores por defecto.
    """
    estado = db.query(EstadoApp).first()
    if not estado:
        estado = create_default_estado(db)
    return estado

def create_default_estado(db: Session) -> EstadoApp:
    """
    Crea un nuevo estado con valores por defecto.
    """
    estado = EstadoApp(
        puntos_consideracion=0,
        estrellas=0,
        razones_desbloqueadas=[],
        cartas_leidas=[],
        premios_reclamados=[]
    )
    db.add(estado)
    db.commit()
    db.refresh(estado)
    return estado

def increment_puntos(db: Session, incremento: int = 1) -> EstadoApp:
    """
    Incrementa los puntos de consideración y actualiza timestamp.
    """
    estado = get_estado(db)
    estado.puntos_consideracion += incremento
    estado.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(estado)
    return estado

def add_estrellas(db: Session, cantidad: int) -> EstadoApp:
    """
    Añade estrellas al total actual.
    """
    estado = get_estado(db)
    estado.estrellas += cantidad
    estado.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(estado)
    return estado

def subtract_estrellas(db: Session, cantidad: int) -> EstadoApp:
    """
    Resta estrellas del total actual.
    No permite valores negativos.
    """
    estado = get_estado(db)
    nueva_cantidad = max(0, estado.estrellas - cantidad)
    estado.estrellas = nueva_cantidad
    estado.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(estado)
    return estado

def add_razon_desbloqueada(db: Session, razon_id: int) -> EstadoApp:
    """
    Añade una razón a la lista de desbloqueadas si no existe ya.
    """
    from sqlalchemy.orm.attributes import flag_modified
    
    estado = get_estado(db)
    
    if estado.razones_desbloqueadas is None:
        estado.razones_desbloqueadas = []
    
    if razon_id not in estado.razones_desbloqueadas:
        estado.razones_desbloqueadas.append(razon_id)
        flag_modified(estado, "razones_desbloqueadas")  # Forzar detección de cambio
        estado.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(estado)
    
    return estado

def add_carta_leida(db: Session, carta_id: int) -> EstadoApp:
    """
    Marca una carta como leída si no lo está ya.
    """
    from sqlalchemy.orm.attributes import flag_modified
    
    estado = get_estado(db)
    
    if estado.cartas_leidas is None:
        estado.cartas_leidas = []
    
    if carta_id not in estado.cartas_leidas:
        estado.cartas_leidas.append(carta_id)
        flag_modified(estado, "cartas_leidas")  # Forzar detección de cambio
        estado.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(estado)
    
    return estado

def add_cancion_escuchada(db: Session, cancion_id: int) -> EstadoApp:
    """
    Marca una canción como escuchada si no lo está ya.
    """
    from sqlalchemy.orm.attributes import flag_modified
    
    estado = get_estado(db)
    
    if estado.canciones_escuchadas is None:
        estado.canciones_escuchadas = []
    
    if cancion_id not in estado.canciones_escuchadas:
        estado.canciones_escuchadas.append(cancion_id)
        flag_modified(estado, "canciones_escuchadas")  # Forzar detección de cambio
        estado.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(estado)
    
    return estado

def add_premio_reclamado(db: Session, premio_id: int) -> EstadoApp:
    """
    Añade un premio a la lista de reclamados con timestamp.
    """
    from sqlalchemy.orm.attributes import flag_modified
    
    estado = get_estado(db)
    
    if estado.premios_reclamados is None:
        estado.premios_reclamados = []
    
    premio_reclamado = {
        "premio_id": premio_id,
        "fecha_reclamado": datetime.utcnow().isoformat()
    }
    estado.premios_reclamados.append(premio_reclamado)
    flag_modified(estado, "premios_reclamados")  # Forzar detección de cambio
    estado.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(estado)
    return estado

def is_carta_leida(db: Session, carta_id: int) -> bool:
    """
    Verifica si una carta ya fue leída.
    """
    estado = get_estado(db)
    if not estado.cartas_leidas:
        return False
    return carta_id in estado.cartas_leidas

def is_cancion_escuchada(db: Session, cancion_id: int) -> bool:
    """
    Verifica si una canción ya fue escuchada.
    """
    estado = get_estado(db)
    if not estado.canciones_escuchadas:
        return False
    return cancion_id in estado.canciones_escuchadas

def is_premio_reclamado(db: Session, premio_id: int) -> bool:
    """
    Verifica si un premio ya fue reclamado.
    """
    estado = get_estado(db)
    if not estado.premios_reclamados:
        return False
    
    return any(
        premio["premio_id"] == premio_id 
        for premio in estado.premios_reclamados
    )

def get_estrellas_disponibles(db: Session) -> int:
    """
    Obtiene la cantidad de estrellas disponibles.
    """
    estado = get_estado(db)
    return estado.estrellas

def tiene_suficientes_estrellas(db: Session, cantidad_requerida: int) -> bool:
    """
    Verifica si hay suficientes estrellas para una transacción.
    """
    estrellas_actuales = get_estrellas_disponibles(db)
    return estrellas_actuales >= cantidad_requerida

# =====================================
# OPERACIONES CON ARCHIVOS JSON
# =====================================

def load_json_data(filename: str) -> List[Dict[str, Any]]:
    """
    Carga datos desde un archivo JSON en la carpeta data.
    """
    file_path = os.path.join("data", filename)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Archivo {file_path} no encontrado")
        return []
    except json.JSONDecodeError:
        print(f"Error al decodificar JSON en {file_path}")
        return []

def get_cartas_data() -> List[Dict[str, Any]]:
    """
    Obtiene los datos de todas las cartas desde el JSON.
    """
    return load_json_data("cartas.json")

def get_razones_data() -> List[Dict[str, Any]]:
    """
    Obtiene los datos de todas las razones desde el JSON.
    """
    return load_json_data("razones.json")

def get_premios_data() -> List[Dict[str, Any]]:
    """
    Obtiene los datos de todos los premios desde el JSON.
    """
    return load_json_data("premios.json")

def get_canciones_data() -> List[Dict[str, Any]]:
    """
    Obtiene los datos de todas las canciones desde el JSON.
    """
    return load_json_data("canciones.json")

def get_carta_by_id(carta_id: int) -> Optional[Dict[str, Any]]:
    """
    Obtiene una carta específica por su ID.
    """
    cartas = get_cartas_data()
    for carta in cartas:
        if carta["id"] == carta_id:
            return carta
    return None

def get_razon_by_id(razon_id: int) -> Optional[Dict[str, Any]]:
    """
    Obtiene una razón específica por su ID.
    """
    razones = get_razones_data()
    for razon in razones:
        if razon["id"] == razon_id:
            return razon
    return None

def get_premio_by_id(premio_id: int) -> Optional[Dict[str, Any]]:
    """
    Obtiene un premio específico por su ID.
    """
    premios = get_premios_data()
    for premio in premios:
        if premio["id"] == premio_id:
            return premio
    return None

def get_cancion_by_id(cancion_id: int) -> Optional[Dict[str, Any]]:
    """
    Obtiene una canción específica por su ID.
    """
    canciones = get_canciones_data()
    for cancion in canciones:
        if cancion["id"] == cancion_id:
            return cancion
    return None

# =====================================
# OPERACIONES DE LÓGICA DE NEGOCIO
# =====================================

def get_nuevas_razones_desbloqueadas(db: Session, puntos_actuales: int) -> List[Dict[str, Any]]:
    """
    Obtiene las razones que deben desbloquearse con la cantidad actual de puntos.
    Retorna solo las que NO estaban desbloqueadas antes.
    """
    estado = get_estado(db)
    razones_ya_desbloqueadas = estado.razones_desbloqueadas or []
    
    todas_las_razones = get_razones_data()
    nuevas_razones = []
    
    for razon in todas_las_razones:
        # Verificar si cumple los puntos requeridos y no está ya desbloqueada
        if (razon["puntos_requeridos"] <= puntos_actuales and 
            razon["id"] not in razones_ya_desbloqueadas):
            nuevas_razones.append(razon)
            # Añadir a la base de datos
            add_razon_desbloqueada(db, razon["id"])
    
    return nuevas_razones

def procesar_dar_punto(db: Session) -> Dict[str, Any]:
    """
    Procesa la acción de dar un punto de consideración.
    Incrementa puntos y desbloquea nuevas razones si corresponde.
    """
    # Incrementar puntos
    estado = increment_puntos(db, 1)
    
    # Obtener razones recién desbloqueadas
    nuevas_razones = get_nuevas_razones_desbloqueadas(db, estado.puntos_consideracion)
    
    return {
        "nuevo_total_puntos": estado.puntos_consideracion,
        "razones_recien_desbloqueadas": nuevas_razones
    }

def procesar_leer_carta(db: Session, carta_id: int) -> Dict[str, Any]:
    """
    Procesa la lectura de una carta.
    Marca como leída y otorga estrellas si no fue leída antes.
    """
    # Verificar si la carta existe
    carta = get_carta_by_id(carta_id)
    if not carta:
        raise ValueError(f"Carta con ID {carta_id} no encontrada")
    
    # Verificar si ya fue leída
    if is_carta_leida(db, carta_id):
        estado = get_estado(db)
        return {
            "nuevas_estrellas": estado.estrellas,
            "carta_id": carta_id,
            "mensaje": "Esta carta ya fue leída anteriormente"
        }
    
    # Marcar como leída y añadir estrellas
    add_carta_leida(db, carta_id)
    estado = add_estrellas(db, 1)
    
    return {
        "nuevas_estrellas": estado.estrellas,
        "carta_id": carta_id,
        "mensaje": "Ganaste 1 estrella"
    }

def procesar_reclamar_premio(db: Session, premio_id: int) -> Dict[str, Any]:
    """
    Procesa el reclamo de un premio.
    Valida estrellas suficientes y registra el reclamo.
    """
    # Verificar si el premio existe
    premio = get_premio_by_id(premio_id)
    if not premio:
        raise ValueError(f"Premio con ID {premio_id} no encontrado")
    
    # Verificar si ya fue reclamado
    if is_premio_reclamado(db, premio_id):
        raise ValueError("Este premio ya fue reclamado")
    
    # Verificar estrellas suficientes
    if not tiene_suficientes_estrellas(db, premio["costo"]):
        raise ValueError("No tienes suficientes estrellas para este premio")
    
    # Procesar el reclamo
    estado = subtract_estrellas(db, premio["costo"])
    add_premio_reclamado(db, premio_id)
    
    return {
        "estrellas_restantes": estado.estrellas,
        "premio": {
            "id": premio["id"],
            "nombre": premio["nombre"],
            "emoji": premio["emoji"]
        },
        "mensaje": f"¡Premio '{premio['nombre']}' reclamado exitosamente!"
    }

def procesar_escuchar_cancion(db: Session, cancion_id: int) -> Dict[str, Any]:
    """
    Procesa cuando se abre/escucha una canción.
    Marca como escuchada y otorga estrella si no fue escuchada antes.
    """
    # Verificar si la canción existe
    cancion = get_cancion_by_id(cancion_id)
    if not cancion:
        raise ValueError(f"Canción con ID {cancion_id} no encontrada")
    
    # Verificar si ya fue escuchada
    if is_cancion_escuchada(db, cancion_id):
        estado = get_estado(db)
        return {
            "nuevas_estrellas": estado.estrellas,
            "cancion_id": cancion_id,
            "mensaje": "Esta canción ya fue escuchada anteriormente"
        }
    
    # Marcar como escuchada y añadir estrella
    add_cancion_escuchada(db, cancion_id)
    estado = add_estrellas(db, 1)
    
    return {
        "nuevas_estrellas": estado.estrellas,
        "cancion_id": cancion_id,
        "mensaje": "Ganaste 1 estrella"
    }