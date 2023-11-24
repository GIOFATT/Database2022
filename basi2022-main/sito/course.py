from flask import Blueprint, flash, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import and_
from werkzeug.utils import redirect

from sito import db
from sito.models import Corso, Utente, Lista_corsi, get_professors, Lezione, Lista_insegnanti, Iscrizione, \
    isIscritto, Lista_corsi_iscritto, Dettagli_corso

corso = Blueprint("course", __name__, static_folder='static', template_folder='templates')


def __init__(self, name, professor, mode, description):
    self.nome = name
    self.professore = professor
    self.modalita = mode
    self.descrizione = description


'''
Non so a cosa serva
'''


@corso.route('/courses/dash')
def dash_corsi():
    user = Utente.query.filter_by(id=current_user.id).first()
    if user.isadmin:
        corsi = Lista_corsi()
    elif user.isprofessor:
        corsi = Corso.query.filter_by(professore=user.id).all()
    else:
        corsi = db.session.query(Corso).filter(and_(Iscrizione.corso == Corso.id, Iscrizione.studente == user.id)).all()

    profs = get_professors(corsi)
    return render_template("DashCorsi.html", user=current_user, corsi=corsi, len=len(corsi), prof=profs)


# Lista corsi
@corso.route('/courses')
def course():
    corsi = Lista_corsi()
    profs = get_professors(corsi)
    return render_template("courses.html", user=current_user, corsi=corsi, len=len(corsi), prof=profs,
                           listcorsi=Lista_corsi_iscritto(current_user.id),
                           lenlistacorsi=len(Lista_corsi_iscritto(current_user.id)))


# Route per ogni corso
@corso.route('/courses/info/<int:course_id>')
def courseInfo(course_id):
    course = Corso.query.filter_by(id=course_id).first()
    professor = Utente.query.filter_by(id=course.professore).first()
    lessons = Lezione.query.filter_by(corso=course_id).all()

    return render_template("CourseInfo.html", user=current_user, id=course.id, name=course.nome, mode=course.modalita,
                           description=course.descrizione,
                           professorid=professor.id, profname=professor.nome, profsurname=professor.cognome,
                           lessons=lessons, len=len(lessons))


@corso.route('/courses/add_course', methods=['GET', 'POST'])
@login_required
def add_course():
    global prof_id
    if request.method == 'POST':
        name = request.form.get('nomecorso')
        mode = request.form.get('mod')
        description = request.form.get("descrizione")

        if name == "" or mode == "" or description == "":
            flash('Devi inserire tutti i campi!', category='error')
            return redirect(url_for('course.add_course'))

        # Per ovviare al nonetype nel caso fosse l'insegnante stesso a creare un corso
        if current_user.isadmin:
            professor = request.form.get("profselect")

            if professor is None:
                flash('Campo del professore non valido!', category='error')
                return redirect(url_for('course.add_course'))
            # Split name from surname and retrieve the id
            prof_data = professor.split()
            prof_name = prof_data[0]
            prof_surname = prof_data[1]

            prof = Utente.query.filter_by(nome=prof_name).filter_by(cognome=prof_surname).first()
            prof_id = prof.id
        else:
            if current_user.isprofessor:
                prof_id = current_user.id

        # Check if course already exists
        check_name = Corso.query.filter_by(nome=name).first()
        if check_name:
            flash('Un altro corso ha già questo nome', category='error')
            return redirect(url_for('course.add_course'))

        new_course = Corso(nome=name, professore=prof_id, modalita=mode, descrizione=description)
        try:
            db.session.add(new_course)
            db.session.commit()
            flash('Corso aggiunto correttamente', category='success')

        except:
            db.session.rollback()
            flash("Non è stato possibile aggiungere il corso", category='error')
        return redirect(url_for('course.dash_corsi'))
    else:
        return render_template("formcourse.html", user=current_user, insegnanti=Lista_insegnanti(),
                               lenins=len(Lista_insegnanti()))


# Modifica del corso
@corso.route('/courses/modify_course/<int:course_id>', methods=['GET', 'POST'])
@login_required
def modify_course(course_id):
    if request.method == 'POST':
        # admin
        if current_user.isadmin:
            new_name = request.form.get("nomecorso")
            new_prof = request.form.get("profselect")
            new_desc = request.form.get("descrizione")
            new_mode = request.form.get("mod")

            if new_name == "" or new_desc == "" or new_mode == "" or new_prof is None:
                flash('Devi inserire tutti i campi!', category='error')
                return redirect(url_for('course.dash_corsi'))

            prof_data = new_prof.split()
            prof_name = prof_data[0]
            prof_surname = prof_data[1]
            prof = Utente.query.filter_by(nome=prof_name).filter_by(cognome=prof_surname).first()
            prof_id = prof.id

            print(new_name, new_desc, new_mode, prof_name, prof_surname)

            to_modify = Corso.query.filter_by(id=course_id).first()

            # Check if there already exists a course with the same name
            check_name = Corso.query.filter_by(nome=new_name).first()
            if check_name and check_name.nome != new_name:
                flash("Esiste già un altro corso con questo nome", category='error')
                return redirect(url_for('course.dash_corsi'))
            change_mode(course_id, new_mode)

            try:
                to_modify.nome = new_name
                to_modify.professore = prof_id
                to_modify.descrizione = new_desc
                to_modify.modalita = new_mode
                db.session.commit()
                flash("Modifica completata", category='success')
            except:
                db.session.rollback()
                flash("Non è stato possibile modificare il corso", category='error')
        # professore
        else:
            new_desc = request.form.get("descrizione")
            new_mode = request.form.get("mod")
            change_mode(course_id, new_mode)
            to_modify = Corso.query.filter_by(professore=current_user.id).first()
            print(new_desc, new_mode, to_modify.professore)
            try:
                to_modify.descrizione = new_desc
                to_modify.modalita = new_mode
                db.session.commit()
                flash("Modifica completata", category='success')
            except:
                db.session.rollback()
                flash("Non è stato possibile modificare il corso", category='error')
        return redirect(url_for('course.dash_corsi'))
    else:
        return render_template("modificaCorso.html", user=current_user, corso=Dettagli_corso(course_id), id=course_id,
                               insegnanti=Lista_insegnanti(), lenins=len(Lista_insegnanti()))


@corso.route('/courses/remove_course/<int:course_id>')
@login_required
def remove_course(course_id):
    to_delete = Corso.query.filter_by(id=course_id).first()
    try:
        elimina = Lezione.query.filter_by(corso=course_id).delete()
        db.session.delete(to_delete)
        db.session.commit()
        flash("Corso eliminato correttamente", category='success')
    except:
        db.session.rollback()
        flash("Non è stato possibile eliminare il corso", category='error')

    return redirect(url_for('course.dash_corsi'))


def change_mode(course_id, new_mode):
    # Check whether new mode is compatible with upcoming scheduled lessons, else modify
    course = Corso.query.filter_by(id=course_id).first()
    if new_mode != course.modalita and new_mode != 'Mista':
        lessons = Lezione.query.filter_by(corso=course_id).all()
        for l in lessons:
            if l.modalita != new_mode:
                l.modalita = new_mode
                try:
                    db.session.commit()
                except:
                    db.session.rollback()
                    return False
    return True


@corso.route('/unsubscribe/<int:course_id>')
@login_required
def unsubscribe_course(course_id):
    # Se utente è studente
    if current_user.isadmin == False and current_user.isprofessor == False:
        to_delete = db.session.query(Iscrizione)\
            .filter(and_(Iscrizione.corso==course_id, Iscrizione.studente==current_user.id))\
            .first()
        print(to_delete)

        if not to_delete:
            flash("Iscrizione non esistente")
            return redirect(url_for('course.course'))

        try:
            db.session.delete(to_delete)
            db.session.commit()
            flash("Iscrizione cancellata correttamente", category='success')
        except:
            db.session.rollback()
            flash("Non è stato possibile cancellare l'iscrizione", category='error')

        return redirect(url_for('course.course'))


# ISCRIZIONE-------------------------------------------------------------------------------

@corso.route('/iscrizione/<int:course_id>', methods=['GET', 'POST'])
@login_required
def subscribe_course(course_id):
    if isIscritto(course_id, current_user.id) == False:
        new_subscription = Iscrizione(corso=course_id, studente=current_user.id)

        try:
            db.session.add(new_subscription)
            db.session.commit()
            flash("Iscrizione effettuata correttamente", category='success')
        except:
            db.session.rollback()
            flash("Non è stato possibile effettuare l'iscrizione", category='error')
        return redirect(url_for('course.course'))
    else:
        flash("Sei gia iscritto a questo corso!", category='error')
        return redirect(url_for('course.course'))
