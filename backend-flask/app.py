from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
import os
from datetime import timedelta

app = Flask(__name__)

# Config
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'dev-secret')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

db = SQLAlchemy(app)
jwt = JWTManager(app)


class Game(db.Model):
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    release_year = db.Column(db.Integer, nullable=True)
    url = db.Column(db.String(500), nullable=True)
    image = db.Column(db.String(500), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'release_year': self.release_year,
            'url': self.url,
            'image': self.image
        }


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # NOTE: store hashed in prod


@app.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'msg': 'username and password required'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'msg': 'username already exists'}), 400
    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'msg': 'user created'}), 201


@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username, password=password).first()
    if not user:
        return jsonify({'msg': 'invalid credentials'}), 401
    access_token = create_access_token(identity=user.id)
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
    data = request.get_json() or {}
    title = data.get('title')
    if not title:
        return jsonify({'msg': 'title is required'}), 400
    game = Game(
        title=title,
        release_year=data.get('release_year'),
        url=data.get('url'),
        image=data.get('image')
    )
    db.session.add(game)
    db.session.commit()
    return jsonify(game.to_dict()), 201


@app.route('/games/<int:game_id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_game(game_id):
    game = Game.query.get_or_404(game_id)
    data = request.get_json() or {}
    game.title = data.get('title', game.title)
    game.release_year = data.get('release_year', game.release_year)
    game.url = data.get('url', game.url)
    game.image = data.get('image', game.image)
    db.session.commit()
    return jsonify(game.to_dict())


@app.route('/games/<int:game_id>', methods=['DELETE'])
@jwt_required()
def delete_game(game_id):
    game = Game.query.get_or_404(game_id)
    db.session.delete(game)
    db.session.commit()
    return jsonify({'msg': 'deleted'})


if __name__ == '__main__':
    app.run(debug=True)
