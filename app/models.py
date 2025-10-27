from sqlalchemy import Column, Integer, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from app.database import Base

class EstadoApp(Base):
    """
    Modelo para almacenar el estado general de la aplicación.
    
    Tabla principal que mantiene el progreso del usuario incluyendo:
    - Puntos de consideración acumulados
    - Estrellas para canjear premios
    - Razones desbloqueadas por puntos
    - Cartas leídas por el usuario
    - Premios ya reclamados con timestamps
    """
    __tablename__ = "estado_app"

    id = Column(Integer, primary_key=True, index=True)
    
    # Sistema de puntos y estrellas
    puntos_consideracion = Column(Integer, default=0, nullable=False)
    estrellas = Column(Integer, default=0, nullable=False)
    
    # Arrays JSON para tracking de progreso
    razones_desbloqueadas = Column(JSON, default=list, nullable=False)  # [1, 2, 3, ...]
    cartas_leidas = Column(JSON, default=list, nullable=False)          # [1, 2, 3, ...]
    canciones_escuchadas = Column(JSON, default=list, nullable=False)   # [1, 2, 3, ...]
    premios_reclamados = Column(JSON, default=list, nullable=False)     # [{"premio_id": 1, "fecha_reclamado": "2024-..."}, ...]
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<EstadoApp(id={self.id}, puntos={self.puntos_consideracion}, estrellas={self.estrellas})>"

    @classmethod
    def get_default_estado(cls):
        """
        Retorna un diccionario con los valores por defecto para un nuevo estado.
        """
        return {
            "puntos_consideracion": 0,
            "estrellas": 0,
            "razones_desbloqueadas": [],
            "cartas_leidas": [],
            "canciones_escuchadas": [],
            "premios_reclamados": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

    def to_dict(self):
        """
        Convierte el modelo a diccionario para responses de la API.
        """
        return {
            "id": self.id,
            "puntos_consideracion": self.puntos_consideracion,
            "estrellas": self.estrellas,
            "razones_desbloqueadas": self.razones_desbloqueadas or [],
            "cartas_leidas": self.cartas_leidas or [],
            "canciones_escuchadas": self.canciones_escuchadas or [],
            "premios_reclamados": self.premios_reclamados or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def add_razon_desbloqueada(self, razon_id: int):
        """
        Añade una razón a la lista de desbloqueadas si no existe ya.
        """
        if self.razones_desbloqueadas is None:
            self.razones_desbloqueadas = []
        
        if razon_id not in self.razones_desbloqueadas:
            self.razones_desbloqueadas.append(razon_id)

    def add_carta_leida(self, carta_id: int):
        """
        Añade una carta a la lista de leídas si no existe ya.
        """
        if self.cartas_leidas is None:
            self.cartas_leidas = []
        
        if carta_id not in self.cartas_leidas:
            self.cartas_leidas.append(carta_id)

    def add_cancion_escuchada(self, cancion_id: int):
        """
        Añade una canción a la lista de escuchadas si no existe ya.
        """
        if self.canciones_escuchadas is None:
            self.canciones_escuchadas = []
        
        if cancion_id not in self.canciones_escuchadas:
            self.canciones_escuchadas.append(cancion_id)

    def add_premio_reclamado(self, premio_id: int):
        """
        Añade un premio a la lista de reclamados con timestamp.
        """
        if self.premios_reclamados is None:
            self.premios_reclamados = []
        
        premio_reclamado = {
            "premio_id": premio_id,
            "fecha_reclamado": datetime.utcnow().isoformat()
        }
        self.premios_reclamados.append(premio_reclamado)

    def is_premio_reclamado(self, premio_id: int) -> bool:
        """
        Verifica si un premio ya fue reclamado.
        """
        if not self.premios_reclamados:
            return False
        
        return any(
            premio["premio_id"] == premio_id 
            for premio in self.premios_reclamados
        )