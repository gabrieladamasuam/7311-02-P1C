import os
import tempfile
import json
from app import app, db, User, Game


def setup_test_db():
    # Use in-memory sqlite for tests
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    with app.app_context():
        db.create_all()


def run_tests():
    setup_test_db()
    client = app.test_client()

    # register a user
    r = client.post('/auth/register', json={'username': 'test', 'password': 'test'})
    assert r.status_code == 201

    # login
    r = client.post('/auth/login', json={'username': 'test', 'password': 'test'})
    assert r.status_code == 200
    token = r.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # create a game
    r = client.post('/games', json={'title': 'Test Game', 'genre': 'RPG'}, headers=headers)
    assert r.status_code == 201
    game = r.get_json()
    assert game['title'] == 'Test Game'

    # list games
    r = client.get('/games')
    assert r.status_code == 200
    data = r.get_json()
    assert data['total'] == 1

    # update game
    r = client.put(f"/games/{game['id']}", json={'title': 'Updated'}, headers=headers)
    assert r.status_code == 200
    assert r.get_json()['title'] == 'Updated'

    # delete game
    r = client.delete(f"/games/{game['id']}", headers=headers)
    assert r.status_code == 200

    # verify empty
    r = client.get('/games')
    assert r.get_json()['total'] == 0

    print('All tests passed')


if __name__ == '__main__':
    run_tests()
