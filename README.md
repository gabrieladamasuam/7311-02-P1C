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
# Proyecto: Videogames (Vue 3 frontend) + Backend Flask

Este repositorio contiene dos subproyectos:

- `frontend-videogames/` — aplicación Vue 3 (Vite).
- `backend-flask/` — API en Flask que usa PostgreSQL.

Este README está reducido a lo esencial para que tu profesor pueda ejecutar el proyecto:

Requisitos previos
- Node.js + npm
- Python 3.8+
- PostgreSQL en localhost (puerto 5432)

Primera vez (instalación y puesta en marcha)

1) Backend

```bash
cd backend-flask
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt
# Inicializar tablas y usuario admin
python3 setup_db.py init-db
python3 setup_db.py create-admin
# cargar datos de ejemplo
python3 setup_db.py load-games
# Arrancar la API
export FLASK_APP=api.py
flask run --host=0.0.0.0 --port=5001
```

2) Frontend

```bash
cd frontend-videogames
npm install   # solo la primera vez
# Opcional: crear frontend-videogames/.env con VITE_API_URL=http://localhost:5001
npm run dev
```

Ejecución habitual (segunda vez)

1) Backend

```bash
cd backend-flask
source .venv/bin/activate
export FLASK_APP=api.py
flask run --host=0.0.0.0 --port=5001
```

2) Frontend

```bash
cd frontend-videogames
npm run dev
```

Notas rápidas
- El fichero de dependencias del backend está en `backend-flask/requirements.txt`.
- Si tu PostgreSQL no usa usuario `postgres`/contraseña `1234`, exporta `DATABASE_URL` con la URL correcta antes de inicializar la base de datos.