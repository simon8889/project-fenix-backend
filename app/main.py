from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import json
from dotenv import load_dotenv

# Importar routers
from app.routers import estado, cartas, razones, premios, juegos, canciones, frases

# Importar configuración de base de datos
from app.database import create_tables, get_db
from app.crud import get_estado, create_default_estado

# Cargar variables de entorno
load_dotenv()

# Crear instancia de FastAPI
app = FastAPI(
    title="API de Reconquista Romántica 💕",
    description="""
    API backend para una aplicación de reconquista romántica que incluye:
    
    - **Sistema de Puntos**: Acumula puntos de consideración
    - **Cartas Románticas**: 30 cartas con contenido personalizado  
    - **Razones para Volver**: Sistema de desbloqueo por puntos
    - **Premios**: Sistema de canje con estrellas
    - **Juegos Interactivos**: Bonus de estrellas por participar
    
    Desarrollado con FastAPI y SQLAlchemy.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in origins],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Incluir routers con prefijo /api
app.include_router(estado.router)
app.include_router(cartas.router)
app.include_router(razones.router)
app.include_router(premios.router)
app.include_router(juegos.router)
app.include_router(canciones.router)
app.include_router(frases.router)

# =====================================
# EVENTOS DE INICIALIZACIÓN
# =====================================

@app.on_event("startup")
async def startup_event():
    """
    Evento que se ejecuta al iniciar la aplicación.
    - Crea las tablas de base de datos si no existen
    - Inicializa un registro de estado por defecto si no existe
    - Valida que los archivos JSON existan
    """
    try:
        print("🚀 Iniciando aplicación...")
        
        # Crear tablas de base de datos
        print("📊 Creando tablas de base de datos...")
        create_tables()
        
        # Inicializar estado por defecto si no existe
        print("🔧 Verificando estado inicial...")
        db = next(get_db())
        try:
            estado = get_estado(db)
            if not estado:
                estado = create_default_estado(db)
                print("✅ Estado inicial creado")
            else:
                print(f"✅ Estado existente encontrado: {estado.puntos_consideracion} puntos, {estado.estrellas} estrellas")
        finally:
            db.close()
        
        # Validar archivos JSON
        print("📁 Validando archivos de datos...")
        json_files = [
            ("data/cartas.json", "cartas"),
            ("data/razones.json", "razones"),
            ("data/premios.json", "premios"),
            ("data/canciones.json", "canciones"),
            ("data/frases.json", "frases")
        ]
        
        for file_path, file_type in json_files:
            if not os.path.exists(file_path):
                print(f"⚠️  Archivo {file_path} no encontrado")
            else:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        print(f"✅ {file_type}: {len(data)} elementos cargados")
                except json.JSONDecodeError:
                    print(f"❌ Error al leer {file_path}")
                except Exception as e:
                    print(f"❌ Error con {file_path}: {str(e)}")
        
        print("🎉 Aplicación iniciada correctamente!")
        print("📖 Documentación disponible en: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"❌ Error durante la inicialización: {str(e)}")
        raise

# =====================================
# ENDPOINTS PRINCIPALES
# =====================================

@app.get("/", tags=["root"])
async def root():
    """
    Endpoint raíz que proporciona información básica de la API.
    """
    return {
        "message": "API de Reconquista Romántica 💕",
        "version": "1.0.0",
        "status": "active",
        "docs": "/docs",
        "endpoints": {
            "estado": "/api/estado",
            "dar_punto": "/api/dar-punto",
            "cartas": "/api/cartas",
            "leer_carta": "/api/leer-carta/{carta_id}",
            "razones": "/api/razones", 
            "premios": "/api/premios",
            "reclamar_premio": "/api/reclamar-premio",
            "completar_juego": "/api/completar-juego",
            "canciones": "/api/canciones",
            "frases": "/api/frases",
            "frase_aleatoria": "/api/frases/aleatoria"
        }
    }

@app.get("/health", tags=["health"])
async def health_check():
    """
    Endpoint de health check para verificar que la API está funcionando.
    """
    try:
        # Verificar conexión a base de datos
        db = next(get_db())
        try:
            estado = get_estado(db)
            db_status = "connected"
        except Exception:
            db_status = "error"
        finally:
            db.close()
        
        # Verificar archivos JSON
        json_status = {}
        json_files = ["data/cartas.json", "data/razones.json", "data/premios.json", "data/canciones.json", "data/frases.json"]
        
        for file_path in json_files:
            filename = os.path.basename(file_path)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    json_status[filename] = len(data)
            except Exception:
                json_status[filename] = "error"
        
        return {
            "status": "healthy",
            "database": db_status,
            "data_files": json_status,
            "timestamp": "2024-01-01T00:00:00Z"  # En producción usarías datetime.utcnow()
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": "2024-01-01T00:00:00Z"
            }
        )

# =====================================
# MANEJO DE ERRORES GLOBALES
# =====================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """
    Manejador personalizado para errores 404.
    """
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "detail": "Endpoint no encontrado",
            "message": "Verifica la URL y el método HTTP",
            "available_endpoints": "/docs"
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """
    Manejador personalizado para errores internos del servidor.
    """
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "detail": "Error interno del servidor",
            "message": "Contacta al administrador si el problema persiste"
        }
    )

# =====================================
# CONFIGURACIÓN PARA DESARROLLO
# =====================================

if __name__ == "__main__":
    import uvicorn
    
    # Configuración desde variables de entorno
    host = os.getenv("HOST", "localhost")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "true").lower() == "true"
    
    print(f"🚀 Iniciando servidor en http://{host}:{port}")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug,
        access_log=debug
    )