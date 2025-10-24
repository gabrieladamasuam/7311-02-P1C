from api import api, db, User, Game
import click
import json
import os


@click.group()
def cli():
    pass


@cli.command('init-db')
def init_db():
    # Asegura que exista el contexto de aplicación al crear las tablas
    with api.app_context():
        db.create_all()
    print('Base de datos inicializada.')


@cli.command('create-admin')
def create_admin():
    """Crea o actualiza el usuario admin (username='admin', password='1234')."""
    with api.app_context():
        db.create_all()

        admin = User.query.filter_by(username='admin').first()
        if admin:
            admin.password = '1234'
            admin.is_admin = True
            print('Usuario admin actualizado.')
        else:
            admin = User(username='admin', password='1234', is_admin=True)
            db.session.add(admin)
            print('Usuario admin creado.')
        db.session.commit()
        print('Admin listo: username=admin password=1234')


@cli.command('load-games')
def load_games(file):
    """Carga la tabla de juegos desde un archivo JSON."""
    path = file or os.path.join(os.path.dirname(__file__), 'data', 'games.json')
    if not os.path.exists(path):
        print(f'Archivo de juegos no encontrado: {path}')
        return

    with open(path, 'r', encoding='utf-8') as fh:
        try:
            data = json.load(fh)
        except Exception as e:
            print('Error al cargar JSON:', e)
            return

    added = 0
    with api.app_context():
        db.create_all()
        for item in data:
            name = item.get('name')
            if not name:
                continue
            # Si ya existe un juego con ese nombre, lo omitimos
            existing = Game.query.filter(db.func.lower(Game.name) == name.lower()).first()
            if existing:
                continue

            game = Game(
                name=name,
                year=item.get('year'),
                url=item.get('url'),
                image=item.get('image'),
                description=item.get('description')
            )
            db.session.add(game)
            added += 1
        db.session.commit()

    print(f'Carga completa. Juegos añadidos: {added}')


if __name__ == '__main__':
    cli()
