from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import timedelta

# utilities to ensure postgres DB exists
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url
from urllib.parse import quote_plus

app = Flask(__name__)

# Config
# Prefer an explicit DATABASE_URL environment variable. If it's not set,
# default to a local PostgreSQL database named `videogames_db` using the
# PGUSER or the current system user. This makes Postgres the default for
# development when PostgreSQL is installed locally.
default_db_user = os.environ.get('PGUSER') or os.environ.get('USER') or 'postgres'
default_db_name = os.environ.get('PGDATABASE') or 'videogames_db'
default_postgres_url = f'postgresql://{default_db_user}@localhost:5432/{default_db_name}'
DATABASE_URL = os.environ.get('DATABASE_URL', default_postgres_url)


def ensure_postgres_db_exists(database_url: str):
    """If DATABASE_URL points to PostgreSQL, attempt to create the database if it doesn't exist.
    This is best-effort: on failure it will print a warning but won't stop the app.
    """
    try:
        url = make_url(database_url)
        if url.get_backend_name() != 'postgresql':
            return

        # target DB name
        target_db = url.database or default_db_name

        # connection args (username/password/host/port)
        connect_args = url.translate_connect_args()
        user = connect_args.get('username')
        password = connect_args.get('password')
        host = connect_args.get('host') or 'localhost'
        port = connect_args.get('port') or 5432

        # build admin URL to connect to the 'postgres' maintenance DB
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
                # Create database (requires appropriate privileges)
                conn.execute(text(f'CREATE DATABASE "{target_db}"'))
                print(f"Created database '{target_db}' on {host}:{port}")
    except Exception as e:
        print('Warning: could not ensure Postgres database exists:', e)


ensure_postgres_db_exists(DATABASE_URL)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'dev-secret')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)  # allow all origins by default (for dev). Restrict in production.


class Game(db.Model):
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    release_year = db.Column(db.Integer, nullable=True)
    url = db.Column(db.String(500), nullable=True)
    image = db.Column(db.String(500), nullable=True)
    description = db.Column(db.Text, nullable=True)

    def to_dict(self):
        # Provide both backend canonical keys and frontend-friendly aliases
        return {
            'id': self.id,
            'title': self.title,
            'name': self.title,  # frontend expects 'name'
            'release_year': self.release_year,
            'year': self.release_year,  # frontend expects 'year'
            'url': self.url,
            'image': self.image,
            'description': self.description
        }


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # NOTE: hashed
    is_admin = db.Column(db.Boolean, default=False, nullable=False)


@app.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'msg': 'username and password required'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'msg': 'username already exists'}), 400
    # store hashed password
    user = User(username=username, password=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    return jsonify({'msg': 'user created'}), 201


@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'msg': 'invalid credentials'}), 401
    # use string identity to avoid JWT library errors about subject type
    access_token = create_access_token(identity=str(user.id))
    return jsonify({'access_token': access_token}), 200


@app.route('/games', methods=['GET'])
def list_games():
    # pagination
    try:
        limit = int(request.args.get('limit', 10))
        skip = int(request.args.get('skip', 0))
    except ValueError:
        return jsonify({'msg': 'invalid pagination params'}), 400
    query = Game.query.order_by(Game.id)
    total = query.count()
    games = query.offset(skip).limit(limit).all()
    return jsonify({'total': total, 'games': [g.to_dict() for g in games]})


@app.route('/games/<int:game_id>', methods=['GET'])
def get_game(game_id):
    game = Game.query.get_or_404(game_id)
    return jsonify(game.to_dict())


@app.route('/games', methods=['POST'])
@jwt_required()
def create_game():
    # only admin users may create games
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or not user.is_admin:
        return jsonify({'msg': 'admin privileges required'}), 403
    data = request.get_json() or {}
    # accept either 'title' or frontend 'name'
    title = data.get('title') or data.get('name')
    if not title:
        return jsonify({'msg': 'title is required'}), 400
    game = Game(
        title=title,
        release_year=data.get('release_year') or data.get('year'),
        url=data.get('url'),
        image=data.get('image'),
        description=data.get('description')
    )
    db.session.add(game)
    db.session.commit()
    return jsonify(game.to_dict()), 201


@app.route('/games/<int:game_id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_game(game_id):
    # only admin users may update games
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or not user.is_admin:
        return jsonify({'msg': 'admin privileges required'}), 403

    game = Game.query.get_or_404(game_id)
    data = request.get_json() or {}
    game.title = data.get('title', data.get('name', game.title))
    game.release_year = data.get('release_year', data.get('year', game.release_year))
    game.url = data.get('url', game.url)
    game.image = data.get('image', game.image)
    game.description = data.get('description', game.description)
    db.session.commit()
    return jsonify(game.to_dict())



@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


@app.route('/games/<int:game_id>', methods=['DELETE'])
@jwt_required()
def delete_game(game_id):
    # only admin users may delete games
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or not user.is_admin:
        return jsonify({'msg': 'admin privileges required'}), 403

    game = Game.query.get_or_404(game_id)
    db.session.delete(game)
    db.session.commit()
    return jsonify({'msg': 'deleted'})


if __name__ == '__main__':
    app.run(debug=True)
