from flask import Blueprint, render_template, request, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import redirect
from . import db
from .models import Utente, Lista_insegnanti, Lista_studenti, Ruoli

admin = Blueprint("admin", __name__, static_folder='static', template_folder='templates')


@admin.route('/usersearch/dash')
@login_required
def dash():
    return render_template("dashUser.html", user=current_user, utenti=Lista_studenti(), len=len(Lista_studenti()),
                           insegnanti=Lista_insegnanti(), lenins=len(Lista_insegnanti()))


# Modifica utente
@admin.route('/admin/modify_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def modify_user(user_id):
    utente = db.session.query(Utente).filter(Utente.id==user_id).first()
    if request.method == 'POST':
        new_name = request.form.get('nomeuser')
        new_surname = request.form.get('cognomeuser')
        new_email = request.form.get('email')
        new_gender = request.form.get('gen')
        new_role = request.form.get('role')

        if new_name == "" or new_surname == "" or new_gender == "" or not new_role:
            flash('Devi riempire tutti i campi!', category='error')
            return redirect(url_for('admin.dash'))

        # Check if role changes and change it if necessary
        role = Ruoli(user_id)
        if role != 2 and new_role == "docente":
            promote_to_professor(user_id)
        elif role != 1 and new_role == "admin":
            promote_to_admin(user_id)
        elif role != get_role_int(new_role):
            flash("Modifica del ruolo non valida", category='error')
            return redirect(url_for('admin.dash'))

        # Controlla che la mail sia unica e valida
        email_check = Utente.query.filter_by(email=new_email).first()
        if not email_check or email_check.id == user_id:
            if len(new_email) < 4:
                flash('Email deve essere più lunga di 4 caratteri', category='error')
                return redirect(url_for('admin.dash'))
            try:
                user = Utente.query.filter_by(id=user_id).first()
                user.nome = new_name
                user.cognome = new_surname
                user.genere = new_gender
                user.email = new_email
                db.session.commit()
                flash("Utente modificato con successo", category='success')
            except:
                db.session.rollback()
                flash("Non è stato possibile modificare l'utente", category='error')
            return redirect(url_for('admin.dash'))
        else:
            flash("Email già utilizzata", category='error')
            return redirect(url_for('admin.dash'))
    else:
        return render_template("modificaUser.html", user=utente, role=Ruoli(user_id))


# Rimuovi un utente
@admin.route('/admin/remove_user/<int:user_id>')
@login_required
def remove_user(user_id):
    if user_id == current_user.id:
        flash("Non puoi cancellare te stesso!", category='error')
    else:
        to_delete = Utente.query.filter_by(id=user_id).first()
        try:
            db.session.delete(to_delete)
            db.session.commit()
            flash("Utente eliminato!", category='success!')
        except:
            flash("Qualcosa è andato storto", category='error')
    return redirect(url_for('admin.dash'))


# Funzione dell'admin per promuovere un utente a professore
@admin.route('/admin/promote/to_professor/<int:user_id>', methods=['GET'])
@login_required
def promote_to_professor(user_id):
    to_promote = Utente.query.filter_by(id=user_id).first()
    if not to_promote.isprofessor:
        try:
            to_promote.isprofessor = True
            db.session.commit()
            flash("L'utente è ora un professore!", category='success')
        except:
            db.session.rollback()
            flash("Qualcosa è andato storto", category='error')
    else:
        flash("L'utente selezionato è già un professore!", category='error')

    return redirect(url_for('admin.dash'))


# Promuovere un utente ad admin
@admin.route('/admin/promote/to_admin/<int:user_id>', methods=['GET'])
@login_required
def promote_to_admin(user_id):
    to_promote = Utente.query.filter_by(id=user_id).first()
    if not to_promote.isadmin:
        if to_promote.isprofessor:
            to_promote.isprofessor = False
        try:
            to_promote.isadmin = True
            db.session.commit()
            flash("L'utente è ora un admin!", category='success')
        except:
            db.session.rollback()
            flash("Qualcosa è andato storto", category='error')
    else:
        flash("L'utente selezionato è già un admin!", category='error')

    return redirect(url_for('admin.dash'))


def get_role_int(role):
    if role == "admin":
        return 1
    elif role == "docente":
        return 2
    elif role == "studente":
        return 3
