# Proyecto: Videogames (Frontend Vue 3) + Backend Flask

Este repositorio contiene dos partes principales:

- `frontend-videogames/`: aplicación Vue 3 (Vite) que muestra una lista de juegos y permite autenticarse, añadir, editar y borrar juegos desde la UI.
- `backend-flask/`: API REST en Flask que gestiona usuarios y juegos con SQLAlchemy y JWT y guarda datos en PostgreSQL.

Este documento explica en detalle los pasos para:

- Primera vez que preparas la base de datos (crear roles/DB, inicializar tablas, crear admin, cargar datos seed).
- Pasos habituales para arrancar la API y la web cuando la base de datos ya existe.
- Solución de problemas comunes cuando "no se conecta a la base de datos".

Todas las instrucciones están pensadas para macOS con zsh (ajusta comandos si usas otro shell).

## Resumen rápido

- Requisitos: Node.js + npm, Python 3.8+, PostgreSQL en localhost (puerto 5432 por defecto).
- El backend lee la URL de conexión desde la variable de entorno `DATABASE_URL`. Si no está definida, usa por defecto:

	`postgresql://postgres:1234@localhost:5432/videogames_db`

	Esto asume el role `postgres` con contraseña `1234`. Si tu instalación usa otras credenciales, exporta `DATABASE_URL` con los valores correctos (ver más abajo).

## Sección A — Primera instalación (crear DB por primera vez)

1) Preparar el entorno Python (recomendado: virtualenv)

```bash
cd backend-flask
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

2) Asegurarte de que PostgreSQL está en ejecución en tu máquina y en qué puerto

```bash
# Verifica que hay un servicio escuchando en 5432
pg_isready -q -h localhost -p 5432 || echo "Postgres no responde en localhost:5432"

# Si usas Homebrew y no está arrancado:
# brew services start postgresql
```

3) Exportar variables de entorno (opcional pero recomendado)

Si quieres usar las credenciales incluidas por defecto en este repo, exporta:

```bash
export PGUSER=postgres
export PGPASSWORD=1234
export DATABASE_URL="postgresql://postgres:1234@localhost:5432/videogames_db"
# Para el backend en desarrollo (opcional)
export FLASK_APP=api.py
export FLASK_ENV=development
```

Si no quieres usar `postgres:1234`, adapta `DATABASE_URL` al usuario/contraseña que prefieras.

4) (Opcional) Crear/asegurar rol y base de datos con psql

Estos comandos asumen que `psql -U postgres` funciona (usa `PGPASSWORD` o autenticación por socket según tu instalación):

```bash
# Asegura que el role 'postgres' existe y tiene la contraseña dada
psql -U postgres -c "DO $$ BEGIN IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'postgres') THEN CREATE ROLE postgres WITH LOGIN SUPERUSER PASSWORD '1234'; ELSE ALTER ROLE postgres WITH PASSWORD '1234' LOGIN SUPERUSER; END IF; END $$;"

# Crear / recrear la base de datos
psql -U postgres -c "DROP DATABASE IF EXISTS videogames_db;"
psql -U postgres -c "CREATE DATABASE videogames_db OWNER postgres;"
```

5) Iniciar la API (primera vez también puedes dejar que la propia app intente crear la DB si tu role tiene permisos)

Antes de iniciar la API, es conveniente crear las tablas y el admin con los comandos proporcionados:

```bash
# Desde backend-flask/ y con el .venv activado
python3 setup_db.py init-db
python3 setup_db.py create-admin
python3 setup_db.py load-games    # opcional: carga datos de seed desde data/games.json
```

Si `init-db` falla con error de conexión, vuelve a comprobar `DATABASE_URL`, que Postgres esté en ejecución y que el usuario/contraseña sean correctos.

6) Arrancar la API

```bash
flask run --host=0.0.0.0 --port=5001
```

La app por defecto en `api.py` imprimirá información al arrancar, y el código contiene una función `ensure_db_exists()` que intenta crear la base de datos indicada por `DATABASE_URL` conectándose al DB `postgres` (si el usuario tiene permisos para hacerlo).

## Sección B — Cuando la base de datos ya está creada (arranques diarios de desarrollo)

1) Backend (desde `backend-flask/`)

```bash
source .venv/bin/activate   # activar virtualenv si lo usas
export DATABASE_URL="postgresql://postgres:1234@localhost:5432/videogames_db"  # ajusta si hace falta
flask run --host=0.0.0.0 --port=5001
```

2) Frontend (desde `frontend-videogames/`)

```bash
cd ../frontend-videogames
npm install   # solo la primera vez
```

Crear o ajustar `.env` en la carpeta `frontend-videogames/` con la dirección de la API:

```
VITE_API_URL=http://localhost:5001
```

Arrancar el dev server de Vite:

```bash
npm run dev
```

Abre `http://localhost:5173` (o el puerto que Vite muestre) para ver la UI.

## Sección C — Por qué "no se conecta a la base de datos" (diagnóstico rápido)

Si la API muestra errores al conectar con la base de datos, las causas más comunes son:

- Credenciales incorrectas: el `DATABASE_URL` no coincide con un usuario/contraseña válidos.
- Postgres no está en ejecución o escucha en otro puerto (ej: 5434). Comprueba con `pg_isready` o `lsof -i :5432`.
- La base de datos indicada no existe y el usuario no tiene permisos para crearla (el script intenta crearla usando el role `postgres` si puede).
- El servicio usa autenticación por socket y no por contraseña; en ese caso `psql -U postgres` puede funcionar sin `PGPASSWORD`.
- Error de permisos/roles: el role que usas no tiene privilegios para crear tablas o conectarse.

Comandos útiles para depurar (ejecutar en zsh):

```bash
# ¿Está postgres aceptando conexiones en localhost:5432?
pg_isready -h localhost -p 5432 && echo "Postgres OK" || echo "Postgres no responde"

# ¿Qué proceso escucha en el puerto 5432?
lsof -iTCP:5432 -sTCP:LISTEN

# Probar conexión directa con psql (te pedirá contraseña si hace falta)
psql "${DATABASE_URL}"

# Si no puedes conectarte como el usuario default, prueba con el role postgres y la contraseña que exportaste
PGPASSWORD=1234 psql -U postgres -h localhost -p 5432 -c "SELECT version();"
```

Errores comunes y soluciones rápidas
- password authentication failed for user "postgres": verifica `PGPASSWORD`/`DATABASE_URL` y que el usuario exista.
- connection refused: Postgres no está corriendo en ese host/puerto o hay un firewall/permiso que lo impide.
- column "name" does not exist o errores de esquema al correr `load-games`: puede que exista un esquema previo con columnas distintas. Solución: reinicia tablas con `python3 setup_db.py init-db` tras eliminar la DB o usar SQLAlchemy `db.drop_all()` y `db.create_all()` (ten cuidado con datos de producción).

## Sección D — Comandos seguros para resetear la base de datos (dev only)

Estos son comandos para desarrollo local — no usar en producción sin backups.

```bash
# Hacer dump antes de borrar (si quieres guardar datos)
PGPASSWORD=1234 pg_dump -U postgres -h localhost -p 5432 -Fc -f videogames_db.dump videogames_db || echo "pg_dump falló"

# Terminar conexiones y recrear la base de datos (drop/create)
PGPASSWORD=1234 psql -U postgres -h localhost -p 5432 -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='videogames_db' AND pid<>pg_backend_pid();"
PGPASSWORD=1234 psql -U postgres -h localhost -p 5432 -c "DROP DATABASE IF EXISTS videogames_db;"
PGPASSWORD=1234 psql -U postgres -h localhost -p 5432 -c "CREATE DATABASE videogames_db OWNER postgres;"

# Luego recrear tablas y seeds
cd backend-flask
source .venv/bin/activate
python3 setup_db.py init-db
python3 setup_db.py create-admin
python3 setup_db.py load-games
```

## Sección E — Notas sobre variables de entorno y configuración

- `DATABASE_URL`: conexión completa Postgres (ej: `postgresql://user:pass@host:port/dbname`). Si la variable no está presente, el backend usará la URL por defecto mostrada arriba.
- `JWT_SECRET_KEY`: secreto para tokens JWT. Cambia el valor en producción.
- `VITE_API_URL` (frontend): URL de la API que el frontend usa para hacer peticiones.

## Sección F — Si quieres, puedo ayudar a diagnosticar ahora mismo

Si me pegas el error exacto que ves en la consola cuando intentas correr `flask run` o el log que aparece al ejecutar `python3 setup_db.py init-db`, puedo darte pasos concretos (por ejemplo: ajustar `DATABASE_URL`, arrancar Postgres, crear el role correcto, o cambiar el puerto si tu Postgres usa otro).

---

Fechas/autor

- Actualizado: 2025-11-01 — Guía de primer arranque y diagnóstico añadida.

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
02/11/2025
Eva Blázquez Pardo y Gabriela Damas García