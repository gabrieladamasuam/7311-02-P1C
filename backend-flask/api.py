from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from flask_cors import CORS
from datetime import timedelta
import os
import json

api = Flask(__name__)

default_db_user = 'postgres'
default_db_pass = '1234'
default_db_name = 'videogames_db'
default_db_host = 'localhost'
default_db_port = '5432'

default_postgres_url = (
    f'postgresql://{default_db_user}:{default_db_pass}@{default_db_host}:{default_db_port}/{default_db_name}'
)
DATABASE_URL = os.environ.get('DATABASE_URL', default_postgres_url)

api.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
api.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
api.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'dev-secret')
api.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

db = SQLAlchemy(api)
jwt = JWTManager(api)
CORS(api)


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


with api.app_context():
    db.create_all()

    admin_user = os.environ.get('ADMIN_USERNAME')
    admin_pass = os.environ.get('ADMIN_PASSWORD')

    if admin_user and admin_pass:
        existing = User.query.filter_by(username=admin_user).first()
        if not existing:
            admin = User(username=admin_user, password=admin_pass, is_admin=True)
            db.session.add(admin)
            db.session.commit()

    json_path = os.path.join(os.path.dirname(__file__), 'data', 'games.json')
    if os.path.exists(json_path):
        if Game.query.count() == 0:
            with open(json_path, 'r', encoding='utf-8') as f:
                items = json.load(f)
            for item in items:
                if not item.get('name'):
                    continue
                game = Game(
                    name=item['name'],
                    year=item.get('year'),
                    url=item.get('url'),
                    image=item.get('image'),
                    description=item.get('description')
                )
                db.session.add(game)
            db.session.commit()


@api.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'msg': 'Falta nombre de usuario o contraseña'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'msg': 'Ese usuario ya existe'}), 400
    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'msg': 'Usuario creado correctamente'}), 201


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


def is_admin():
    user = User.query.get(get_jwt_identity())
    return user and user.is_admin


@api.route('/games', methods=['GET'])
def list_games():
    limit = int(request.args.get('limit', 100))
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

    image_url = f'/images/{file.filename}'
    return jsonify({'msg': 'Imagen subida correctamente', 'image_url': image_url}), 200


@api.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


if __name__ == '__main__':
    api.run(debug=True)