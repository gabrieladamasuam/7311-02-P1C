# Proyecto: Videogames + Backend Flask

Este repositorio contiene dos partes principales:
- `frontend-videogames/`: aplicación Vue 3 (Vite) que muestra una lista de juegos y permite añadirlos.
- `backend-flask/`: API en Flask que gestiona los juegos con PostgreSQL y autenticación JWT.

Instrucciones rápidas (sin usar `.venv`)

1) Instalar dependencias (sistema global de Python)

```bash
cd backend-flask
# Si NO quieres usar el archivo `requirements.txt` (por ejemplo para evitar compilar psycopg2)
# instala un subconjunto mínimo compatible con SQLite y desarrollo local:
# Proyecto: Videogames + Backend Flask

Este repositorio contiene dos partes principales:

- `frontend-videogames/`: aplicación Vue 3 (Vite) que muestra una lista de juegos y permite autenticarse, añadir, editar y borrar juegos desde la UI.
- `backend-flask/`: API REST en Flask que gestiona usuarios y juegos con SQLAlchemy y JWT.

Este README describe cómo ejecutar el proyecto en desarrollo, qué variables de entorno configurar y cómo probar las rutas principales.

---

Requisitos principales
- Node.js + npm (para el frontend)
- Python 3.8+ (para el backend)
- PostgreSQL (la aplicación requiere PostgreSQL; el backend intentará crear la base de datos indicada por `DATABASE_URL` si tiene privilegios).

Ejecución rápida (desarrollo)

Backend (Flask)

1. Instala dependencias (recomendado en un entorno virtual):

```bash
cd backend-flask
python3 -m pip install --upgrade pip
pip3 install -r requirements.txt
```

2. Inicializa la base de datos (opcional, `setup_db.py` hará CREATE TABLES):

```bash
python3 setup_db.py init-db
```

3. (Opcional) Crea el admin por defecto (username=admin, password=1234):

```bash
python3 setup_db.py create-admin
```

4. Arranca la API (usa la `DATABASE_URL` definida, por defecto apunta a un Postgres local):

```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5001
```

Nota: en este repositorio la API se ha probado en puerto 5001 — ajusta `VITE_API_URL` en el frontend si cambias el puerto.

Frontend (Vue + Vite)

1. Instala dependencias y arranca el servidor de desarrollo:

```bash
cd frontend-videogames
npm install
npm run dev
```

2. El frontend busca la API en la variable `VITE_API_URL`. Por ejemplo, crea `frontend-videogames/.env` con:

```text
VITE_API_URL=http://localhost:5001
```

Endpoints relevantes (backend)
- POST /auth/register — crear usuario (body: {username, password})
- POST /auth/login — obtener access_token (body: {username, password})
- GET /games — listar juegos (paginado: ?limit=&skip=)
- POST /games — crear juego (JWT requerido y usuario debe ser admin)
- PUT /games/:id — actualizar (admin)
- DELETE /games/:id — eliminar (admin)
- GET /health — estado de la API

Notas sobre la base de datos
- Por defecto el backend construye una URL Postgres local si no está `DATABASE_URL` definida: `postgresql://<user>@localhost:5432/videogames_db`.
-- La app intenta crear la base de datos en Postgres si no existe (best-effort). Asegúrate de que `DATABASE_URL` apunte a una instancia de Postgres disponible.

Autenticación y permisos
- La API usa JWT (Flask-JWT-Extended). Las operaciones que modifican datos (POST/PUT/DELETE en `/games`) requieren un token válido y que el usuario tenga `is_admin = True`.
- La UI mantiene el `access_token` en `localStorage` y lo manda en las peticiones Axios.

Credenciales de ejemplo
- Admin por defecto: `username=admin`, `password=1234` (si ejecutaste `python3 setup_db.py create-admin`).

Ejemplos rápidos con curl

Login y crear juego (ejemplo):

```bash
# login
TOKEN=$(curl -s -X POST http://localhost:5001/auth/login -H "Content-Type: application/json" -d '{"username":"admin","password":"1234"}' | jq -r .access_token)

# create game
curl -s -X POST http://localhost:5001/games \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Mi Juego","release_year":2025,"description":"Prueba"}' | jq .
```

Desarrollo y notas finales
- La UI obtiene los datos exclusivamente desde la API del backend. No se usa un fallback local embebido por defecto.
- Si algo falla al instalar los drivers de Postgres (`psycopg2`), instala las dependencias del sistema en macOS (por ejemplo: `brew install postgresql` o `brew install libpq`), y luego instala `psycopg2-binary` en el entorno Python.

Si quieres, puedo:
- añadir un endpoint `/auth/me` para que el frontend pueda verificar roles y mostrar/ocultar controles según `is_admin`.
- crear scripts para poblar la BBDD con los juegos locales.

---

Fechas/autor

- Generado automáticamente para este ejercicio (actualizado 2025-10-23)
