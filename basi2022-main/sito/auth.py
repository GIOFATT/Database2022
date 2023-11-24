from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Utente
from . import db

auth = Blueprint("auth", __name__, static_folder='static', template_folder='templates')


# Route che ci indirizza alla pagina per il login
@auth.route('/login', methods=['GET', 'POST'])
def login():
    data = request.form  # mi genera un dizionario con le informazioni
    print(data)  # TODO a scopo di debug
    if request.method == 'POST':
        email = request.form.get('email').lower() # Mail in minuscolo
        passw = request.form.get('password')

        user = Utente.query.filter_by(email=email).first()
        if user:
            # Controllo che la password combaci
            if check_password_hash(user.password, passw):
                flash('Loggato con successo', category='success')
                login_user(user, remember=True)  # remember -> serve per i cookies per ricordarci che siamo loggati
                return redirect(url_for('views.home'))
            else:
                flash('Password errata, riprova!', category='error')
        else:
            flash('Email non esistente!', category='error')
    return render_template("login.html", user=current_user)


# Funzione per disconnettere il profilo
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Ottengo informazioni dal form presente nella pagina html
        email = request.form.get('email').lower()  # Metto la mail in minuscolo "mail in minuscolo = maiuscolo vedi # internet"
        nome = request.form.get('name')
        cognome = request.form.get('surname')
        passw = request.form.get('password')
        passw2 = request.form.get('password2')
        birthday = request.form.get('birthday')
        genere = request.form.get('gender')

        # Caso in cui l'email con cui ci si registra è gia presente all'interno del database
        user = Utente.query.filter_by(email=email).first()
        if user:
            flash('Email già esistente', category='error')
        # Mail corta anche se...è 3 la lunghezza minima
        if len(email) < 4:
            flash('Email deve essere più lungo di 4 letteri', category='error')
        # Caso in cui nome <2 a discrezione del programmatore
        elif len(nome) < 2:
            flash('nome deve essere più lungo di 2 letteri', category='error')
        # Caso lunghezza cognome a discrezione del programmatore
        elif len(cognome) < 2:
            pass
        # Caso in cui le due password non combacino
        elif passw != passw2:
            flash('Le due password non combaciano!', category='error')
        # Caso password corta
        elif len(passw) < 7:
            pass
        else:
            new_user = Utente(nome=nome, cognome=cognome,genere=genere ,compleanno=birthday, email=email,
                                password=generate_password_hash(passw, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account creato!', category='success')
            return redirect(url_for("views.home"))
        # Serve per far funzionare i flash
        return render_template('signup.html', user=current_user)
    else:
        return render_template("signup.html", user=current_user)
