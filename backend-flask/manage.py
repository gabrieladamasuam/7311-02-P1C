from app import app, db
import click


@click.group()
def cli():
    pass


@cli.command('init-db')
def init_db():
    # Ensure an application context is active when creating the database
    with app.app_context():
        db.create_all()
    print('Initialized the database.')


@cli.command('create-admin')
def create_admin():
    """Create or update the admin user with username 'admin' and password '1234'.
    Password is stored hashed using werkzeug.security.generate_password_hash.
    """
    from werkzeug.security import generate_password_hash
    with app.app_context():
        # Ensure tables exist for the current DATABASE_URL
        db.create_all()

        # Import User model from app and create/update admin user
        from app import User

        admin = User.query.filter_by(username='admin').first()
        hashed = generate_password_hash('1234')
        if admin:
            admin.password = hashed
            admin.is_admin = True
            print('Updated existing admin user.')
        else:
            admin = User(username='admin', password=hashed, is_admin=True)
            db.session.add(admin)
            print('Created admin user.')
        db.session.commit()
        print('Admin user is ready: username=admin password=1234')


if __name__ == '__main__':
    cli()
