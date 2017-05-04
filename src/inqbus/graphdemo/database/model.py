from flask_security import RoleMixin, UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, \
    DateTime
from sqlalchemy.orm import relationship, backref

DB = SQLAlchemy()


roles_users = DB.Table(
    'roles_users',
    DB.Column(
        'user_id',
        DB.Integer(),
        DB.ForeignKey('user.id')),
    DB.Column(
        'role_id',
        DB.Integer(),
        DB.ForeignKey('role.id')))


class Role(DB.Model, RoleMixin):
    __tablename__ = 'role'
    id = Column(Integer(), primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))


class User(DB.Model, UserMixin):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    password = Column(String(255))
    active = Column(Boolean())
    confirmed_at = Column(DateTime())
    roles = relationship('Role', secondary=roles_users,
                         backref=backref('users', lazy='dynamic'))

# Define models for storing data
# class Paths(DB.Model):
#     __tablename__ = 'paths'
#     id = Column(Integer, primary_key=True)
#     path = Column(String(), unique=True)
