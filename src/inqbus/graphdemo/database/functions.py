from flask import g
from flask_security import Security, SQLAlchemyUserDatastore
from sqlalchemy.exc import IntegrityError

from inqbus.graphdemo.database.model import User, Role, DB


def set_up_db(app):
    # Create database connection object
    DB.init_app(app)

    DB.app = app

    # set tables as user storage
    user_datastore = SQLAlchemyUserDatastore(DB, User, Role)
    security = Security(app, user_datastore)

    DB.create_all()

    # just testing
    try:
        user_datastore.create_user(email='admin', password='password')
        user_datastore.create_user(email='normal', password='password')
        user_datastore.create_role(name='admin', description='Admin')
        user_datastore.add_role_to_user('admin', 'admin')
    except IntegrityError:
        DB.session.rollback()

    DB.session.commit()

    with app.app_context():
        g._user_datastore = user_datastore
