from app import app, db
import click


@click.group()
def cli():
    pass


@cli.command('init-db')
def init_db():
    db.create_all()
    print('Initialized the database.')


if __name__ == '__main__':
    cli()
