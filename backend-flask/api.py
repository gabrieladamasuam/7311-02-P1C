from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from flask_cors import CORS
from datetime import timedelta
import os
import json

api = Flask(__name__)

# --- CONFIG BASE DE DATOS ---
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL no está definida en Render.")

# Convertir postgres:// → postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# --- CONFIG FLASK ---
api.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
api.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
api.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'dev-secret')
api.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

db = SQLAlchemy(api)
jwt = JWTManager(api)
CORS(api)


# --- MODELOS ---
class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    year = db.Column(db.Integer)
    url = db.Column(db.String(500))
    image = db.Column(db.String(500))
    description = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'year': self.year,
            'url': self.url,
            'image': self.image,
            'description': self.description
        }


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

# Crear tablas al iniciar
with api.app_context():
    db.create_all()

    # ------ ADMIN AUTOMÁTICO ------
    admin_username = os.environ.get("ADMIN_USERNAME", "admin")
    admin_password = os.environ.get("ADMIN_PASSWORD", "admin")

    admin = User.query.filter_by(is_admin=True).first()
    if not admin:
        new_admin = User(
            username=admin_username,
            password=admin_password,
            is_admin=True
        )
        db.session.add(new_admin)
        db.session.commit()
        print(">>> Admin creado automáticamente")

    # ------ CARGA DE JUEGOS SOLO SI LA TABLA ESTÁ VACÍA ------
    if Game.query.count() == 0:
        json_path = os.path.join(os.path.dirname(__file__), "data", "games.json")
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            added = 0
            for item in data:
                game = Game(
                    name=item.get("name"),
                    year=item.get("year"),
                    url=item.get("url"),
                    image=item.get("image"),
                    description=item.get("description")
                )
                db.session.add(game)
                added += 1

            db.session.commit()
            print(f">>> {added} juegos cargados automáticamente")


# --- RUTAS DE AUTENTICACIÓN ---
@api.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    if not user or user.password != password:
        return jsonify({'msg': 'Credenciales incorrectas'}), 401
    token = create_access_token(identity=str(user.id))
    return jsonify({'access_token': token}), 200


# --- RUTAS DE JUEGOS ---
def is_admin():
    user = User.query.get(get_jwt_identity())
    return user and user.is_admin


@api.route('/games', methods=['GET'])
def list_games():
    limit = int(request.args.get('limit', 10))
    skip = int(request.args.get('skip', 0))
    query = Game.query.order_by(Game.id)
    total = query.count()
    games = query.offset(skip).limit(limit).all()
    return jsonify({'total': total, 'games': [g.to_dict() for g in games]})


@api.route('/games/<int:game_id>', methods=['GET'])
def get_game(game_id):
    game = Game.query.get_or_404(game_id)
    return jsonify(game.to_dict())


@api.route('/games', methods=['POST'])
@jwt_required()
def create_game():
    if not is_admin():
        return jsonify({'msg': 'Solo el administrador puede crear juegos'}), 403

    data = request.get_json() or {}
    if not data.get('name'):
        return jsonify({'msg': 'El nombre del juego es obligatorio'}), 400

    game = Game(
        name=data.get('name'),
        year=data.get('year'),
        url=data.get('url'),
        image=data.get('image'),
        description=data.get('description')
    )
    db.session.add(game)
    db.session.commit()
    return jsonify(game.to_dict()), 201


@api.route('/games/<int:game_id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_game(game_id):
    if not is_admin():
        return jsonify({'msg': 'Solo el administrador puede editar juegos'}), 403

    game = Game.query.get_or_404(game_id)
    data = request.get_json() or {}

    game.name = data.get('name', game.name)
    game.year = data.get('year', game.year)
    game.url = data.get('url', game.url)
    game.image = data.get('image', game.image)
    game.description = data.get('description', game.description)
    db.session.commit()

    return jsonify(game.to_dict())


@api.route('/games/<int:game_id>', methods=['DELETE'])
@jwt_required()
def delete_game(game_id):
    if not is_admin():
        return jsonify({'msg': 'Solo el administrador puede borrar juegos'}), 403

    game = Game.query.get_or_404(game_id)
    db.session.delete(game)
    db.session.commit()
    return jsonify({'msg': 'Juego eliminado'})


# --- SUBIDA DE IMÁGENES ---
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@api.route('/add_image', methods=['POST'])
@jwt_required()
def add_image():
    if not is_admin():
        return jsonify({'msg': 'Solo el administrador puede subir imágenes'}), 403

    if 'image' not in request.files:
        return jsonify({'msg': 'No se envió ninguna imagen'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'msg': 'Archivo no seleccionado'}), 400
    if not allowed_file(file.filename):
        return jsonify({'msg': 'Formato no permitido'}), 400

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    image_url = f"/images/{file.filename}"
    return jsonify({'msg': 'Imagen subida correctamente', 'image_url': image_url}), 200


# --- EJECUCIÓN DE LA APP ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    api.run(host='0.0.0.0', port=port)