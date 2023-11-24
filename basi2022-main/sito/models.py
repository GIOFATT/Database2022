from sqlalchemy import and_
from . import db  # from sito import db -> __init__.py
from flask_login import UserMixin

'''
ATTENZIONE!
Questo file contiene buona parte delle funzioni di database per il controllo e l'accesso ad essa
Mettere qui possibilmente le funzioni che vanno a prendere dal database le informazioni e/o modifiche
SE POSSIBILE
non è obbligatorio -> vedi auth.py
'''


class Utente(db.Model, UserMixin):
    __tablename__ = 'utenti'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String, nullable=False)
    cognome = db.Column(db.String, nullable=False)
    compleanno = db.Column(db.Date, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    genere = db.Column(db.String, nullable=False)
    isprofessor = db.Column(db.Boolean, default=False, nullable=False)
    isadmin = db.Column(db.Boolean, default=False, nullable=False)

    iscrizioni = db.relationship('Iscrizione', cascade="all,delete", backref='utenti', lazy=True)
    corsi = db.relationship('Corso', cascade="all,delete", backref='corsi', lazy=True)


class Corso(db.Model, UserMixin):
    __tablename__ = 'corsi'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String, nullable=False, unique=True)
    modalita = db.Column(db.String, nullable=False)
    descrizione = db.Column(db.String, nullable=False)

    professore = db.Column(db.Integer, db.ForeignKey('utenti.id', ondelete='CASCADE'), default=False, nullable=False)
    lezioni = db.relationship('Lezione', cascade="all,delete", backref='corsi', lazy=True, passive_deletes=True)
    iscrizioni = db.relationship('Iscrizione', cascade="all,delete", backref='iscrizioni', lazy=True,
                                 passive_deletes=True)


class Lezione(db.Model, UserMixin):
    __tablename__ = 'lezioni'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    data = db.Column(db.DateTime, nullable=False)
    modalita = db.Column(db.String, nullable=False)

    corso = db.Column(db.Integer, db.ForeignKey('corsi.id', ondelete='CASCADE'), nullable=False)


class Iscrizione(db.Model, UserMixin):
    __tablename__ = 'iscrizioni'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    corso = db.Column(db.Integer, db.ForeignKey('corsi.id', ondelete='CASCADE'), nullable=False)
    studente = db.Column(db.Integer, db.ForeignKey('utenti.id', ondelete='CASCADE'), nullable=False)


# FUNZIONI ----------------------------------------------------------------------------

# Funzione che mi ritorna la lista degli utenti
def Lista_utenti():
    utenti = db.session.query(Utente.id, Utente.nome, Utente.cognome).all()
    # print(utenti[1])
    print(utenti)
    return utenti


# Funzione che ritorna la lista di tutti gli studenti
def Lista_studenti():
    studenti = Utente.query.filter_by(isprofessor=False).filter_by(isadmin=False).all()
    return studenti


# Funzione che ritorna la lista di tutti gli insegnanti
def Lista_insegnanti():
    professor = db.session.query(Utente.id, Utente.nome, Utente.cognome).filter(Utente.isprofessor == True).all()
    return professor


# Funzione che ritorna la lista di tutti i corsi
def Lista_corsi():
    corsi = db.session.query(Corso.id, Corso.nome, Corso.professore).all()
    return corsi

# Funzione che ritorna la lista di tutti i corsi
def Lista_corsi_popolati():
    corsi = db.session.query(Corso.id, Corso.nome, Corso.professore).\
        all()
    return corsi

# Funzione che ritorna la lista di tutti i corsi di un dato professore
def Lista_corsi_popolati_prof(prof_id):
    corsi = db.session.query(Corso.id, Corso.nome, Corso.professore).\
        filter(Corso.professore == prof_id).all()
    return corsi


# Funzione che ritorna tutte le informazioni di un corso tramite ID corso
def Dettagli_corso(id):
    corsi = db.session.query(Corso.id, Corso.nome, Corso.modalita, Corso.descrizione, Corso.professore,
                             Utente.cognome, Utente.genere, Utente.compleanno, Utente.email).\
                            filter(Corso.id == id, Corso.professore == Utente.id).first()
    return corsi


# Funzione di utilità per il front che, data una lista di corsi, estrapola i professori in ordine
def get_professors(courses):
    profs = []
    for c in courses:
        prof_id = c.professore
        prof = Utente.query.filter_by(id=prof_id).first()
        name = prof.cognome
        profs.append(name)
    return profs


# Funzione che mi ritorna un int in base al ruolo dell'utente
def Ruoli(user_id):
    user = Utente.query.filter_by(id=user_id).first()
    if user.isadmin:
        role = 1
    elif user.isprofessor:
        role = 2
    else:
        role = 3
    return role


# Funzione che mi ritorna True se l'utente è iscritto a quel corso, altrimenti False
def isIscritto(idcorso, idutente):
    studenti = db.session.query(Corso, Utente) \
        .filter(and_(Iscrizione.corso == Corso.id, Iscrizione.studente == Utente.id)) \
        .filter(Iscrizione.corso == idcorso, Iscrizione.studente == idutente) \
        .first()
    Lista_corsi_iscritto(idutente)
    if studenti is not None:
        return True
    else:
        return False


# Ritorna la lista di tutti i corsi in cui è iscritto l'utente
def Lista_corsi_iscritto(idutente):
    studenti = db.session.query(Corso, Utente) \
        .filter(and_(Iscrizione.corso == Corso.id, Iscrizione.studente == Utente.id)) \
        .filter(Iscrizione.studente == idutente) \
        .all()
    lista = []
    for r in studenti:  # Scorro la lista
        lista.append(r[0].id)
    return lista


# Ritorna una lista di tutti gli utenti iscritti a quel corso
def Lista_iscritti_corso(corso_id):
    corsi = db.session.query(Corso, Utente) \
        .filter(and_(Iscrizione.corso == Corso.id, Iscrizione.studente == Utente.id)) \
        .filter(Iscrizione.corso == corso_id) \
        .all()
    lista = []
    for r in corsi:  # Scorro la lista
        lista.append(r[1])
    return lista
