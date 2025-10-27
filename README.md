# Backend - App de Reconquista Romántica 💕

API backend desarrollada con FastAPI para una aplicación de reconquista romántica que incluye sistema de puntos, cartas románticas, premios y razones para volver.

## 🚀 Características

- **Sistema de Puntos**: Acumula puntos de consideración
- **Cartas Románticas**: 30 cartas con contenido personalizado
- **Razones para Volver**: Sistema de desbloqueo por puntos
- **Premios**: Sistema de canje con estrellas
- **Juegos Interactivos**: Bonus de estrellas por participar

## 📋 Requisitos

- Python 3.8+
- SQLite (incluido en Python)

## 🛠️ Instalación

1. **Clona el repositorio y navega al backend:**
   ```bash
   cd backend
   ```

2. **Crea un entorno virtual:**
   ```bash
   python -m venv venv
   
   # En Windows:
   venv\Scripts\activate
   
   # En macOS/Linux:
   source venv/bin/activate
   ```

3. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura las variables de entorno:**
   ```bash
   cp .env.example .env
   # Edita .env si necesitas cambiar alguna configuración
   ```

5. **Inicializa la base de datos (opcional):**
   ```bash
   python init_db.py
   ```

## 🚀 Ejecución

**Servidor de desarrollo:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Servidor de producción:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

La API estará disponible en:
- **Servidor**: http://localhost:8000
- **Documentación**: http://localhost:8000/docs
- **Redoc**: http://localhost:8000/redoc

## 📚 Endpoints

### Estado de la App
- `GET /api/estado` - Obtiene el estado completo de la aplicación

### Sistema de Puntos
- `POST /api/dar-punto` - Incrementa puntos de consideración

### Cartas Románticas
- `GET /api/cartas` - Lista todas las cartas con estado
- `POST /api/leer-carta/{carta_id}` - Marca carta como leída y otorga estrellas

### Razones para Volver
- `GET /api/razones` - Lista razones desbloqueadas

### Sistema de Premios
- `GET /api/premios` - Lista todos los premios con estado
- `POST /api/reclamar-premio` - Canjea un premio por estrellas

### Juegos
- `POST /api/completar-juego` - Otorga bonus por jugar

## 🗂️ Estructura del Proyecto

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Servidor FastAPI principal
│   ├── database.py          # Configuración de SQLAlchemy
│   ├── models.py            # Modelos de base de datos
│   ├── schemas.py           # Schemas de Pydantic
│   ├── crud.py              # Operaciones CRUD
│   └── routers/
│       ├── __init__.py
│       ├── estado.py        # Endpoints de estado
│       ├── cartas.py        # Endpoints de cartas
│       ├── razones.py       # Endpoints de razones
│       ├── premios.py       # Endpoints de premios
│       └── juegos.py        # Endpoints de juegos
├── data/
│   ├── cartas.json          # 30 cartas románticas
│   ├── razones.json         # 20 razones categorizadas
│   └── premios.json         # 6 premios canjeables
├── requirements.txt         # Dependencias de Python
├── .env                     # Variables de entorno
├── .env.example            # Ejemplo de configuración
├── init_db.py              # Script de inicialización
└── README.md               # Este archivo
```

## 🎯 Modelos de Datos

### EstadoApp
- `puntos_consideracion`: Puntos acumulados
- `estrellas`: Estrellas para canjear premios
- `razones_desbloqueadas`: IDs de razones disponibles
- `cartas_leidas`: IDs de cartas ya leídas
- `premios_reclamados`: Premios canjeados con timestamps

## 🔧 Scripts Útiles

**Resetear base de datos:**
```bash
python init_db.py
```

**Verificar estado de la app:**
```bash
curl http://localhost:8000/api/estado
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

## 🎨 Frontend

Este backend está diseñado para funcionar con el frontend React. Asegúrate de que el frontend apunte a `http://localhost:8000` para las llamadas a la API.

## 📞 Soporte

Para problemas o preguntas, abre un issue en el repositorio.

---

Hecho con ❤️ para ayudar en la reconquista romántica