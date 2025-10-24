import os
import tempfile
import json
from api import api, db, User, Game


def setup_test_db():
    # Use the DATABASE_URL environment variable for tests (Postgres).
    # IMPORTANT: running tests will drop/create tables in the target DB, so
    # point DATABASE_URL to a dedicated test database to avoid data loss.
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise RuntimeError('DATABASE_URL must be set to run tests (use a test Postgres DB)')
    api.config['SQLALCHEMY_DATABASE_URI'] = database_url
    api.config['TESTING'] = True
    with api.app_context():
        # Ensure a clean schema for tests
        db.drop_all()
        db.create_all()


def run_tests():
    setup_test_db()
    client = api.test_client()

    # register a user
    r = client.post('/auth/register', json={'username': 'test', 'password': 'test'})
    assert r.status_code == 201

    # login
    r = client.post('/auth/login', json={'username': 'test', 'password': 'test'})
    assert r.status_code == 200
    token = r.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # create a game (use frontend-friendly keys 'name' and 'year')
    payload = {
        'name': 'Test Game',
        'year': 2025,
        'url': 'https://example.com/game',
        'image': 'https://example.com/img.png',
        'description': 'A test game'
    }
    r = client.post('/games', json=payload, headers=headers)
    assert r.status_code == 201
    game = r.get_json()
    assert game['name'] == 'Test Game'
    assert game['year'] == 2025
    assert game['url'] == payload['url']
    assert game['image'] == payload['image']
    assert game['description'] == payload['description']

    # list games
    r = client.get('/games')
    assert r.status_code == 200
    data = r.get_json()
    assert data['total'] == 1

    # update game
    r = client.put(f"/games/{game['id']}", json={'name': 'Updated'}, headers=headers)
    assert r.status_code == 200
    assert r.get_json()['name'] == 'Updated'

    # delete game
    r = client.delete(f"/games/{game['id']}", headers=headers)
    assert r.status_code == 200

    # verify empty
    r = client.get('/games')
    assert r.get_json()['total'] == 0

    print('All tests passed')


if __name__ == '__main__':
    run_tests()
