#!/usr/bin/env python3
"""
Script para forzar el desbloqueo de razones basado en los puntos actuales.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from app.database import SessionLocal
from app.crud import get_estado, get_razones_data, add_razon_desbloqueada

def desbloquear_razones_pendientes():
    """
    Revisa los puntos actuales y desbloquea todas las razones que deberían estar desbloqueadas.
    """
    print("🔧 Verificando razones pendientes de desbloqueo...")
    
    db = SessionLocal()
    try:
        # Obtener estado actual
        estado = get_estado(db)
        puntos_actuales = estado.puntos_consideracion
        razones_ya_desbloqueadas = estado.razones_desbloqueadas or []
        
        print(f"📊 Puntos de Sanación actuales: {puntos_actuales}")
        print(f"📋 Razones ya desbloqueadas: {razones_ya_desbloqueadas}")
        
        # Obtener todas las razones
        todas_las_razones = get_razones_data()
        print(f"📁 Total de razones en el sistema: {len(todas_las_razones)}")
        
        # Encontrar razones que deberían estar desbloqueadas
        razones_a_desbloquear = []
        for razon in todas_las_razones:
            if (razon["puntos_requeridos"] <= puntos_actuales and 
                razon["id"] not in razones_ya_desbloqueadas):
                razones_a_desbloquear.append(razon)
        
        if not razones_a_desbloquear:
            print("✅ No hay razones pendientes de desbloquear")
            print(f"   Con {puntos_actuales} puntos, ya tienes todas las razones disponibles desbloqueadas")
            return
        
        print(f"\n🆕 Razones que se van a desbloquear: {len(razones_a_desbloquear)}")
        print("=" * 60)
        
        for razon in razones_a_desbloquear:
            print(f"   Razón #{razon['id']}: {razon['texto'][:50]}...")
            print(f"   Puntos requeridos: {razon['puntos_requeridos']}")
            print(f"   Categoría: {razon['categoria']} {razon['emoji']}")
            print()
            
            # Desbloquear la razón
            add_razon_desbloqueada(db, razon['id'])
        
        # Verificar el resultado
        estado_actualizado = get_estado(db)
        razones_desbloqueadas_final = estado_actualizado.razones_desbloqueadas or []
        
        print("=" * 60)
        print(f"✅ {len(razones_a_desbloquear)} razones desbloqueadas exitosamente!")
        print(f"📊 Razones desbloqueadas ahora: {razones_desbloqueadas_final}")
        print(f"📈 Total: {len(razones_desbloqueadas_final)}/20 razones")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("  🔓 DESBLOQUEO DE RAZONES PENDIENTES")
    print("=" * 60)
    print()
    
    desbloquear_razones_pendientes()
    
    print()
    print("=" * 60)
    print("🎉 Proceso completado!")
    print("   Ahora puedes ver las razones en el frontend")
    print("=" * 60)
