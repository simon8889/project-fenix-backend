#!/usr/bin/env python3
"""
Script de migración para agregar la columna canciones_escuchadas.

Este script agrega la nueva columna sin borrar los datos existentes.

Uso:
    python migrate_add_canciones.py
"""

import sqlite3
import sys
import os
from pathlib import Path

# Ruta a la base de datos
DB_PATH = "database.db"

def migrate():
    """
    Agrega la columna canciones_escuchadas a la tabla estado_app.
    """
    print("🔧 Iniciando migración...")
    print(f"📁 Base de datos: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Error: No se encuentra la base de datos en {DB_PATH}")
        return False
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(estado_app)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'canciones_escuchadas' in columns:
            print("⚠️  La columna 'canciones_escuchadas' ya existe en la base de datos")
            print("✅ No es necesario realizar la migración")
            conn.close()
            return True
        
        print("📊 Columnas actuales:", columns)
        print("\n➕ Agregando columna 'canciones_escuchadas'...")
        
        # Agregar la nueva columna
        cursor.execute("""
            ALTER TABLE estado_app 
            ADD COLUMN canciones_escuchadas TEXT DEFAULT '[]'
        """)
        
        conn.commit()
        
        # Verificar que se agregó correctamente
        cursor.execute("PRAGMA table_info(estado_app)")
        columns_after = [col[1] for col in cursor.fetchall()]
        
        if 'canciones_escuchadas' in columns_after:
            print("✅ Columna agregada exitosamente")
            print(f"📊 Columnas actualizadas: {columns_after}")
            
            # Mostrar estado actual
            cursor.execute("SELECT * FROM estado_app LIMIT 1")
            row = cursor.fetchone()
            if row:
                print("\n📈 Estado actual de la base de datos:")
                cursor.execute("PRAGMA table_info(estado_app)")
                column_names = [col[1] for col in cursor.fetchall()]
                for i, col_name in enumerate(column_names):
                    print(f"   {col_name}: {row[i]}")
            
            conn.close()
            return True
        else:
            print("❌ Error: La columna no se agregó correctamente")
            conn.close()
            return False
            
    except sqlite3.Error as e:
        print(f"❌ Error de SQLite: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def main():
    """
    Función principal del script.
    """
    print("=" * 60)
    print("  MIGRACIÓN: Agregar campo canciones_escuchadas")
    print("  App de Reconquista Romántica 💕")
    print("=" * 60)
    print()
    
    success = migrate()
    
    if success:
        print("\n🎉 ¡Migración completada exitosamente!")
        print("✅ Ahora puedes iniciar el servidor sin problemas")
        print("\n💡 Para iniciar el servidor:")
        print("   uvicorn app.main:app --reload")
    else:
        print("\n❌ La migración falló")
        print("💡 Si el problema persiste, puedes resetear la base de datos:")
        print("   python init_db.py")
        print("   ⚠️  ADVERTENCIA: Esto borrará todos los datos")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Proceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
