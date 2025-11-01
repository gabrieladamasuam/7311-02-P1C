# Proyecto: Videogames + Backend Flask

Este repositorio contiene dos partes principales:
- `frontend-videogames/`: aplicación Vue 3 (Vite) que muestra una lista de juegos y permite añadirlos.
- `backend-flask/`: API en Flask que gestiona los juegos con PostgreSQL y autenticación JWT.

Instrucciones rápidas (sin usar `.venv`)

1) Instalar dependencias (sistema global de Python)

```bash
cd backend-flask
```

Este repositorio contiene dos partes principales:

- `frontend-videogames/`: aplicación Vue 3 (Vite) que muestra una lista de juegos y permite autenticarse, añadir, editar y borrar juegos desde la UI.
- `backend-flask/`: API REST en Flask que gestiona usuarios y juegos con SQLAlchemy y JWT.

Este README describe cómo ejecutar el proyecto en desarrollo, qué variables de entorno configurar y cómo probar las rutas principales.

---

Requisitos principales
- Node.js + npm (para el frontend)
- Python 3.8+ (para el backend)
- PostgreSQL (la aplicación requiere PostgreSQL; el backend intentará crear la base de datos indicada por `DATABASE_URL` si tiene privilegios).

# Proyecto: Videogames + Backend Flask

Este repositorio contiene dos partes principales:

- `frontend-videogames/`: aplicación Vue 3 (Vite) que muestra una lista de juegos y permite autenticarse, añadir, editar y borrar juegos desde la UI.
- `backend-flask/`: API REST en Flask que gestiona usuarios y juegos con SQLAlchemy y JWT.

Este README explica cómo ejecutar el proyecto en desarrollo usando exclusivamente PostgreSQL (sin SQLite). El entorno de desarrollo debe usar el usuario de base de datos `postgres` con contraseña `1234` tal y como solicitas.

---

Requisitos principales
- Node.js + npm (para el frontend)
- Python 3.8+ (para el backend)
- PostgreSQL (la aplicación requiere PostgreSQL; el backend intentará crear la base de datos indicada por `DATABASE_URL` si tiene privilegios).

Nota importante sobre la base de datos
- Este proyecto debe usar únicamente PostgreSQL. El README y los pasos siguientes asumen que quieres que la base de datos `videogames_db` exista y esté propiedad del rol `postgres` cuya contraseña debe ser `1234`.
- Si existe un role llamado `gabrieladamas`, las instrucciones incluyen cómo eliminarlo para evitar que la aplicación intente conectarse con ese usuario.

Configuración recomendada (entorno zsh)

Exporta estas variables antes de arrancar o inicializar la base de datos:

```bash
# usuario/contraseña que debe usarse para la app
export PGUSER=postgres
export PGPASSWORD=1234

# URL completa (opcional — si lo prefieres puedes usar PGUSER/PGPASSWORD)
export DATABASE_URL="postgresql://postgres:1234@localhost:5432/videogames_db"
```

Instalar dependencias (backend)

Es recomendable usar un entorno virtual para Python:

```bash
cd backend-flask
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

Inicializar la base de datos y crear el admin

Ejecuta (con las variables de entorno anteriores exportadas):

```bash
python3 setup_db.py init-db
python3 setup_db.py create-admin
```

Si la base de datos o roles existentes impiden la creación, usa los comandos psql descritos más abajo.

Arrancar la API

```bash
export FLASK_APP=api.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5001
```

Frontend (Vue + Vite)

```bash
cd frontend-videogames
npm install
npm run dev
```

El frontend usa la variable `VITE_API_URL` para conectar con la API. Por ejemplo crea `frontend-videogames/.env` con:

```text
VITE_API_URL=http://localhost:5001
```

Comandos útiles de administración de Postgres (ejecutar en terminal zsh)

-- El siguiente bloque de comandos intenta dejar el sistema tal como pides: eliminar el role `gabrieladamas` si existe, asegurar que `postgres` tiene contraseña `1234`, eliminar y recrear la base de datos `videogames_db` propiedad de `postgres`.

```bash
# Ajusta si tu instalación requiere sudo o acceso distinto; exporta PGPASSWORD=1234 antes si vas a usar el usuario postgres con contraseña
export PGPASSWORD=1234

# Opcional: ver versión de psql
psql --version

# 1) Asegurar que existe/actualizar el role 'postgres' y su contraseña
psql -U postgres -c "DO $$ BEGIN IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'postgres') THEN CREATE ROLE postgres WITH LOGIN SUPERUSER PASSWORD '1234'; ELSE ALTER ROLE postgres WITH PASSWORD '1234' LOGIN SUPERUSER; END IF; END $$;"

# 2) Eliminar el role del usuario local si existe (evita que la app se conecte con ese usuario)
psql -U postgres -c "DROP ROLE IF EXISTS gabrieladamas;"

# 3) Eliminar la base de datos antigua y crearla de nuevo a nombre de postgres
psql -U postgres -c "DROP DATABASE IF EXISTS videogames_db;"
psql -U postgres -c "CREATE DATABASE videogames_db OWNER postgres;"

# 4) (Opcional) otorgar privilegios adicionales si los necesitas
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE videogames_db TO postgres;"
```

Si alguno de los comandos psql falla por autenticación, asegúrate de que el servicio Postgres está en ejecución y de haber exportado `PGPASSWORD=1234` o usa `brew services start postgresql` si instalaste Postgres con Homebrew.

Endpoints relevantes (backend)
- POST /auth/register — crear usuario (body: {username, password})
- POST /auth/login — obtener access_token (body: {username, password})
- GET /games — listar juegos (paginado: ?limit=&skip=)
- POST /games — crear juego (JWT requerido y usuario debe ser admin)
- PUT /games/:id — actualizar (admin)
- DELETE /games/:id — eliminar (admin)

Credenciales de ejemplo
- Admin por defecto: `username=admin`, `password=1234` (si ejecutaste `python3 setup_db.py create-admin`).

Notas finales
- El backend intenta crear la base de datos indicada en `DATABASE_URL` si tiene privilegios para hacerlo. Las instrucciones anteriores estandarizan el entorno para usar el rol `postgres` con contraseña `1234`.
- Si quieres que yo ejecute los comandos psql desde aquí para eliminar el role `gabrieladamas` y recrear la base de datos, dime y lo intento; te mostraré la salida y errores si aparecen.

---

Fechas/autor

- Actualizado por petición del usuario (2025-10-28)