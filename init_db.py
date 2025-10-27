#!/usr/bin/env python3
"""
Script de inicialización para resetear la base de datos de la app de reconquista romántica.

Este script:
1. Elimina la base de datos existente si existe
2. Crea nuevas tablas
3. Inserta un registro inicial en estado_app con valores por defecto
4. Valida que los archivos JSON existan y sean válidos

Uso:
    python init_db.py
"""

import os
import sys
import json
from pathlib import Path

# Agregar el directorio raíz al path para importar módulos
sys.path.append(str(Path(__file__).parent))

from app.database import engine, create_tables, drop_tables, SessionLocal
from app.models import EstadoApp
from app.crud import get_cartas_data, get_razones_data, get_premios_data

def validate_json_files():
    """
    Valida que todos los archivos JSON existan y sean válidos.
    """
    print("📁 Validando archivos JSON...")
    
    files_to_check = [
        ("data/cartas.json", "cartas", 30),
        ("data/razones.json", "razones", 20),
        ("data/premios.json", "premios", 6)
    ]
    
    all_valid = True
    
    for file_path, file_type, expected_count in files_to_check:
        if not os.path.exists(file_path):
            print(f"❌ Archivo {file_path} no encontrado")
            all_valid = False
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if len(data) != expected_count:
                print(f"⚠️  {file_type}: Se esperaban {expected_count} elementos, pero se encontraron {len(data)}")
            else:
                print(f"✅ {file_type}: {len(data)} elementos validados")
                
        except json.JSONDecodeError:
            print(f"❌ Error al decodificar JSON en {file_path}")
            all_valid = False
        except Exception as e:
            print(f"❌ Error con {file_path}: {str(e)}")
            all_valid = False
    
    return all_valid

def reset_database():
    """
    Resetea completamente la base de datos.
    """
    print("🗄️  Reseteando base de datos...")
    
    try:
        # Eliminar tablas existentes
        print("🧹 Eliminando tablas existentes...")
        drop_tables()
        
        # Crear nuevas tablas
        print("🏗️  Creando nuevas tablas...")
        create_tables()
        
        print("✅ Base de datos reseteada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error al resetear la base de datos: {str(e)}")
        return False

def create_initial_state():
    """
    Crea el registro inicial en la tabla estado_app.
    """
    print("🔧 Creando estado inicial...")
    
    try:
        db = SessionLocal()
        
        # Verificar si ya existe un estado
        existing_state = db.query(EstadoApp).first()
        if existing_state:
            print("⚠️  Ya existe un estado en la base de datos. Eliminando...")
            db.delete(existing_state)
            db.commit()
        
        # Crear nuevo estado con valores por defecto
        initial_state = EstadoApp(
            puntos_consideracion=0,
            estrellas=0,
            razones_desbloqueadas=[],
            cartas_leidas=[],
            canciones_escuchadas=[],
            premios_reclamados=[]
        )
        
        db.add(initial_state)
        db.commit()
        db.refresh(initial_state)
        
        print(f"✅ Estado inicial creado con ID: {initial_state.id}")
        print(f"   - Puntos de consideración: {initial_state.puntos_consideracion}")
        print(f"   - Estrellas: {initial_state.estrellas}")
        print(f"   - Razones desbloqueadas: {len(initial_state.razones_desbloqueadas)}")
        print(f"   - Cartas leídas: {len(initial_state.cartas_leidas)}")
        print(f"   - Canciones escuchadas: {len(initial_state.canciones_escuchadas)}")
        print(f"   - Premios reclamados: {len(initial_state.premios_reclamados)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al crear estado inicial: {str(e)}")
        return False
    finally:
        db.close()

def show_summary():
    """
    Muestra un resumen del estado actual del sistema.
    """
    print("\n📊 RESUMEN DEL SISTEMA")
    print("=" * 50)
    
    # Información de archivos JSON
    try:
        cartas = get_cartas_data()
        razones = get_razones_data()
        premios = get_premios_data()
        
        print(f"📄 Cartas disponibles: {len(cartas)}")
        print(f"💭 Razones disponibles: {len(razones)}")
        print(f"🎁 Premios disponibles: {len(premios)}")
        
        # Estadísticas de razones por categoría
        if razones:
            categorias = {}
            for razon in razones:
                cat = razon.get("categoria", "sin_categoria")
                categorias[cat] = categorias.get(cat, 0) + 1
            
            print(f"   Razones por categoría:")
            for categoria, count in categorias.items():
                print(f"   - {categoria}: {count}")
        
        # Estadísticas de premios por costo
        if premios:
            costos = [premio.get("costo", 0) for premio in premios]
            print(f"   Rango de costos de premios: {min(costos)} - {max(costos)} estrellas")
        
    except Exception as e:
        print(f"❌ Error al mostrar resumen: {str(e)}")
    
    print("\n🚀 Sistema listo para usar!")
    print("   Para iniciar el servidor: uvicorn app.main:app --reload")
    print("   Documentación: http://localhost:8000/docs")

def main():
    """
    Función principal del script.
    """
    print("🎭 INICIALIZADOR DE BASE DE DATOS")
    print("App de Reconquista Romántica 💕")
    print("=" * 50)
    
    # Verificar archivos JSON
    if not validate_json_files():
        print("\n❌ Error: Archivos JSON no válidos. Revisa los archivos en la carpeta 'data/'")
        return False
    
    # Resetear base de datos
    if not reset_database():
        print("\n❌ Error: No se pudo resetear la base de datos")
        return False
    
    # Crear estado inicial
    if not create_initial_state():
        print("\n❌ Error: No se pudo crear el estado inicial")
        return False
    
    # Mostrar resumen
    show_summary()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Proceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        sys.exit(1)