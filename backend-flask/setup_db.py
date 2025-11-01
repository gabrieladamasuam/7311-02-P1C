from api import api, db, User, Game
import click
import json
import os


@click.group()
def cli():
    """Comandos para inicializar la base de datos."""
    pass


@cli.command('init-db')
def init_db():
    """Crea todas las tablas necesarias en la base de datos."""
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
def load_games():
    """Carga los juegos desde el archivo JSON en /data/games.json."""
    path = os.path.join(os.path.dirname(__file__), 'data', 'games.json')
    if not os.path.exists(path):
        print(f'No se encontró el archivo: {path}')
        return

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    with api.app_context():
        db.create_all()
        added = 0
        for item in data:
            if not item.get('name'):
                continue
            if Game.query.filter_by(name=item['name']).first():
                continue

            game = Game(
                name=item['name'],
                year=item.get('year'),
                url=item.get('url'),
                image=item.get('image'),
                description=item.get('description')
            )
            db.session.add(game)
            added += 1

        db.session.commit()
        print(f'Carga completada. Juegos añadidos: {added}')


if __name__ == '__main__':
    cli()
