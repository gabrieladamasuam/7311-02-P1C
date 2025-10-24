from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from flask_cors import CORS
import os
from datetime import timedelta

# imports para utilidades que aseguran que la BD exista
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url
from urllib.parse import quote_plus

api = Flask(__name__)

default_db_user = os.environ.get('PGUSER') or os.environ.get('USER') or 'postgres'
default_db_name = os.environ.get('PGDATABASE') or 'videogames_db'
default_postgres_url = f'postgresql://{default_db_user}@localhost:5432/{default_db_name}'
DATABASE_URL = os.environ.get('DATABASE_URL', default_postgres_url)


def ensure_postgres_db_exists(database_url: str):
    """Se asegura de que la base de datos Postgres especificada en database_url exista."""
    try:
        url = make_url(database_url)
        if url.get_backend_name() != 'postgresql':
            return
        # nombre de la BD objetivo
        target_db = url.database or default_db_name
        # args de conexión (usuario/contraseña/host/puerto)
        connect_args = url.translate_connect_args()
        user = connect_args.get('username')
        password = connect_args.get('password')
        host = connect_args.get('host') or 'localhost'
        port = connect_args.get('port') or 5432
        # URL de conexión al servidor Postgres (a la BD 'postgres')
        auth = ''
        if user:
            if password:
                auth = f"{quote_plus(user)}:{quote_plus(password)}@"
            else:
                auth = f"{quote_plus(user)}@"

        admin_url = f"postgresql://{auth}{host}:{port}/postgres"
        engine = create_engine(admin_url)
        with engine.connect() as conn:
            exists = conn.execute(text("SELECT 1 FROM pg_database WHERE datname = :d"), {'d': target_db}).scalar()
            if not exists:
                # Creación de la BD (requiere privilegios apropiados)
                conn.execute(text(f'CREATE DATABASE "{target_db}"'))
                print(f"Base de datos '{target_db}' creada en {host}:{port}")
    except Exception as e:
        print('Warning: No se pudo asegurar que la base de datos Postgres exista:', e)


ensure_postgres_db_exists(DATABASE_URL)

api.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
api.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
api.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'dev-secret')
api.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

db = SQLAlchemy(api)
jwt = JWTManager(api)
CORS(api)  # permitir CORS para todas las rutas (para desarrollo).


class Game(db.Model):
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    year = db.Column(db.Integer, nullable=True)
    url = db.Column(db.String(500), nullable=True)
    image = db.Column(db.String(500), nullable=True)
    description = db.Column(db.Text, nullable=True)

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
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)


@api.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'msg': 'Se requieren nombre de usuario y contraseña'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'msg': 'El nombre de usuario ya existe'}), 400
    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'msg': 'Usuario creado'}), 201


@api.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    if not user or user.password != password:
        return jsonify({'msg': 'Credenciales inválidas'}), 401
    access_token = create_access_token(identity=str(user.id))
    return jsonify({'access_token': access_token}), 200


@api.route('/games', methods=['GET'])
def list_games():
    # obtiene lista parcial de juegos
    try:
        limit = int(request.args.get('limit', 10))
        skip = int(request.args.get('skip', 0))
    except ValueError:
        return jsonify({'msg': 'Error en los parámetros de paginación'}), 400
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
    # Solo el usuario admin puede crear juegos
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or not user.is_admin:
        return jsonify({'msg': 'Se requieren privilegios de administrador'}), 403
    data = request.get_json() or {}
    name = data.get('name')
    if not name:
        return jsonify({'msg': 'El nombre es obligatorio'}), 400
    game = Game(
        name=name,
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
    # Solo el usuario admin puede actualizar juegos
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or not user.is_admin:
        return jsonify({'msg': 'Se requieren privilegios de administrador'}), 403

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
    # Solo el usuario admin puede eliminar juegos
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or not user.is_admin:
        return jsonify({'msg': 'Se requieren privilegios de administrador'}), 403

    game = Game.query.get_or_404(game_id)
    db.session.delete(game)
    db.session.commit()
    return jsonify({'msg': 'Juego eliminado'})


if __name__ == '__main__':
    api.run(debug=True)