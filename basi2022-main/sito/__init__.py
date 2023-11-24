import os

from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import query_expression

# from flask_admin import Admin


load_dotenv()

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.secret_key = 'djsabdsakhdsal'
    app.config['SECRET_kEY'] = 'Khiem figo!'  # TODO modificabile
    # Config per il warning
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE')
    db.init_app(app)
    # admin = Admin(app, name='basi2022', template_mode='bootstrap4')

    # Importare all'interno della funzione permette di evitare l'errore delle importazioni
    # circolari che creano errori durante la funzione auth.py
    from .views import views
    from .auth import auth
    from .admin import admin
    from .course import corso
    from .user import user
    from .lesson import lesson
    from .analitica import analitics
    from .models import Utente
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(corso, url_prefix="/course")
    app.register_blueprint(user, url_prefix='/user')
    app.register_blueprint(lesson, url_prefix='/lesson')
    app.register_blueprint(analitics, url_prefix='/analitics')

    #TODO A scopo di debug, da eliminare a consegna fatta
    from .populate import popola
    app.register_blueprint(popola, url_prefix='/')

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        utente = Utente.query.get(id)
        if utente is not None:
            return User(utente.id, utente.nome, utente.cognome, utente.email, utente.genere, utente.compleanno,
                        admin=utente.isadmin, professor=utente.isprofessor,
                        is_authenticated=True, active=True, anon=False)
        else:
            return utente

    # classe utente che può essere Cliente o Istruttore
    class User:
        def __init__(self, id, nome, cognome, email,genere,compleanno , admin=False,
                     professor=False, is_authenticated=False, active=False, anon=True):
            self.id = id
            self.nome = nome
            self.cognome = cognome
            self.email = email
            self.genere = genere
            self.compleanno = compleanno
            self.isadmin = admin
            self.isprofessor = professor
            self.is_authenticated = is_authenticated
            self.is_active = active
            self.is_anonymous = anon

    db.create_all(app=app)

    return app
