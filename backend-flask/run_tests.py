from api import api, db, User


def setup_test_db():
    """Crea una base de datos limpia para las pruebas."""
    with api.app_context():
        db.drop_all()
        db.create_all()


def create_admin_user():
    """Crea un usuario admin para las pruebas."""
    with api.app_context():
        admin = User(username='admin', password='1234', is_admin=True)
        db.session.add(admin)
        db.session.commit()

def run_tests():
    "Ejecuta las pruebas básicas del backend."
    setup_test_db()
    create_admin_user()
    client = api.test_client()
    
    # Iniciar sesión como admin
    r = client.post('/auth/login', json={'username': 'admin', 'password': '1234'})
    assert r.status_code == 200
    token = r.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # Crear juego
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

    # Listar juegos
    r = client.get('/games')
    assert r.status_code == 200
    data = r.get_json()
    assert data['total'] == 1

    # Actualizar juego
    r = client.put(f"/games/{game['id']}", json={'name': 'Updated'}, headers=headers)
    assert r.status_code == 200
    assert r.get_json()['name'] == 'Updated'

    # Eliminar juego
    r = client.delete(f"/games/{game['id']}", headers=headers)
    assert r.status_code == 200

    # Verificar que se eliminó
    r = client.get('/games')
    assert r.get_json()['total'] == 0

    print('Todas las pruebas pasaron correctamente')


if __name__ == '__main__':
    run_tests()
