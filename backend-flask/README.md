# Backend Flask para la práctica

Este backend proporciona una API RESTful para gestionar juegos (games). Está pensado para usarse con la app frontend del proyecto.

Características:
- Flask + SQLAlchemy
- JWT (Flask-JWT-Extended) para autenticación
- Endpoints: listar, obtener, crear, actualizar y eliminar juegos
- Configurable por variable de entorno `DATABASE_URL` (por defecto usa SQLite local para desarrollo)
- Script de inicialización y tests unitarios que no dependen del frontend

Requisitos
- Python 3.8+
- PostgreSQL si quieres usar una BBDD real (aka setear `DATABASE_URL` a una URL de Postgres)

Instalación

Sin entorno virtual (usar pip global):

```bash
python3 -m pip install --upgrade pip
pip3 install -r requirements.txt
```

Con entorno virtual (recomendado):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Configurar la base de datos

Por defecto la app usa SQLite local (`sqlite:///data.db`). Para usar PostgreSQL exporta:

```bash
export DATABASE_URL=postgresql://user:password@host:5432/dbname
export FLASK_APP=app.py
export FLASK_ENV=development
```

Inicializar la base de datos:

```bash
python manage.py init-db
```

Ejecutar el servidor de desarrollo:

```bash
flask run --host=0.0.0.0 --port=5000
```

Ejecutar tests (usa una base SQLite en memoria):

```bash
python run_tests.py
```

Notas
- Para desarrollo esta API habilita CORS para permitir que el frontend (Vite) haga peticiones a `http://localhost:5000`.
- Para producción usa una base de datos PostgreSQL real y configura las variables de entorno.
