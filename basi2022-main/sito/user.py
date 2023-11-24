from flask import Blueprint, flash, request, url_for, render_template
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import redirect

from sito import db
from sito.models import Utente, Ruoli

user = Blueprint("user", __name__, static_folder='static', template_folder='templates')


def __init__(self, name, surname, birthday, gender, isprofessor=False, isadmin=False):
    self.nome = name
    self.cognome = surname
    self.compleanno = birthday
    self.genere = gender
    self.isprofessor = isprofessor
    self.isadmin = isadmin


# Route che porta al profilo principale dell'utente
@user.route('/profile/<int:user_id>')
def userprofile(user_id):
    user = Utente.query.filter_by(id=user_id).first()
    role = Ruoli(user_id)
    return render_template("Userpage.html", user=user, role=role)


# Funzione per la modifica della password
@user.route('/user/modify_password', methods=['GET', 'POST'])
@login_required
def modify_password():
    if request.method == 'POST':
        user = Utente.query.filter_by(id=current_user.id).first()
        email = request.form.get('email')
        old_pw = request.form.get('passwordOld')

        if email != user.email or not check_password_hash(user.password, old_pw):
            flash("Credenziali errate", category='error')
            return redirect(url_for('user.modify_password'))

        new_pw1 = request.form.get('password1')
        new_pw2 = request.form.get('password2')

        if new_pw1 != new_pw2:
            flash('Inserite due password diverse', category='error')
            return redirect(url_for('user.modify_password'))

        if len(new_pw1) < 7:
            flash("Password dev'essere più lunga di 7 caratteri", category='error')
            return redirect(url_for('user.modify_password'))

        try:
            user.password = generate_password_hash(new_pw1, method='sha256')
            db.session.commit()
            flash("Password cambiata con successo", category='success')
        except:
            db.session.rollback()
            flash("Non è stato possibile modificare la password", category='error')
        return redirect(url_for('user.modify_password'))
    else:
        return render_template('change_psw.html', user=current_user)
