# Proyecto: Videogames + Backend Flask

Este repositorio contiene dos partes principales:
- `frontend-videogames/`: aplicación Vue 3 (Vite) que muestra una lista de juegos y permite añadirlos.
- `backend-flask/`: API en Flask que gestiona los juegos con PostgreSQL/SQLite y autenticación JWT.

Instrucciones rápidas (sin usar `.venv`)

1) Instalar dependencias (sistema global de Python)

```bash
cd backend-flask
# Si NO quieres usar el archivo `requirements.txt` (por ejemplo para evitar compilar psycopg2)
# instala un subconjunto mínimo compatible con SQLite y desarrollo local:
python3 -m pip install --upgrade pip
# Instala sólo lo necesario para ejecutar el servidor con SQLite (no PostgreSQL):
pip3 install Flask Flask-JWT-Extended Flask-SQLAlchemy Flask-Cors

# Nota para macOS: si `pip3 install -r requirements.txt` falla compilando `psycopg2-binary`,
# omite ese paquete o instala PostgreSQL y las herramientas de compilación necesarias.
# Para desarrollo local con la base de datos SQLite no necesitas psycopg2.
```

---

Si quieres usar PostgreSQL (recomendado para la entrega), sigue estos pasos mínimos:

Preparar una base de datos local (ejemplo con Homebrew):

```bash
# instala y arranca Postgres (si no lo tienes)
brew install postgresql
brew services start postgresql

# crea un usuario/DB (usa tu usuario o crea uno nuevo)
createuser -s $(whoami) || true
createdb videogames_db
```

Instala el driver PostgreSQL y dependencias de la app (recomendado `psycopg` v3):

```bash
pip3 install psycopg[binary] Flask Flask-JWT-Extended Flask-SQLAlchemy Flask-Cors
```

Exporta la URL de la base de datos y crea las tablas:

```bash
export DATABASE_URL=postgresql://$(whoami)@localhost:5432/videogames_db
python3 manage.py init-db
```

Arranca la app:

```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
```

2) Inicializar base de datos (por defecto SQLite `data.db`)

```bash
python manage.py init-db
```

3) Ejecutar servidor backend

```bash
# export DATABASE_URL=postgresql://user:pass@host:5432/dbname  # opcional
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
```

4) Ejecutar frontend (otra terminal)

```bash
cd ../frontend-videogames
npm install
npm run dev
```

5) Probar flujo

- Abrir `http://localhost:5173` (o la url indicada por Vite).
- Si necesitas crear un usuario para obtener token:
  - POST a `http://localhost:5000/auth/register` con `{username,password}`
  - POST a `http://localhost:5000/auth/login` con `{username,password}` y guardar `access_token` en localStorage (la UI de login hace esto automáticamente).
- Añadir juegos usando el formulario (requiere login para POST `/games`).

Notas
- Ejecutar pip globalmente puede requerir privilegios y no es recomendable para producción. Se recomienda usar un entorno virtual en entornos reales.
- Si deseas usar PostgreSQL, configura `DATABASE_URL` antes de inicializar la BBDD.