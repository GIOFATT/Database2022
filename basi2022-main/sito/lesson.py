from datetime import datetime

from flask import Blueprint, flash, request, url_for, render_template
from flask_login import login_required, current_user
from werkzeug.utils import redirect

from sito import db
from sito.models import Lezione, Corso

lesson = Blueprint("lesson", __name__, static_folder='static', template_folder='templates')


def __init__(self, course, data, modalita):
    self.corso = course
    self.data = data
    self.modalita = modalita


# Funzione per aggiungere una lezione
@lesson.route('/lesson/add_lesson/<int:course_id>', methods=['GET', 'POST'])
@login_required
def add_lesson(course_id):
    if request.method == 'POST':
        date = request.form.get('dateStandard')
        time = request.form.get('timeStandard')
        mode = request.form.get('selezioneMod')
        mode.lower()

        if date == "" or time == "" or mode == "":
            flash("Devi riempire tutti i campi!", category='error')
            return redirect(url_for('course.courseInfo', course_id=course_id))

        # Split date and time to make a datetime object
        d = date.split('-')
        t = time.split(':')
        new_datetime = datetime(int(d[0]), int(d[1]), int(d[2]), int(t[0]), int(t[1]))

        if new_datetime < datetime.now():
            flash("Questa data è già passata!", category='error')

        # Check whether modalità makes sense
        course = Corso.query.filter_by(id=course_id).first()
        print(course.modalita)
        print(mode)
        if course.modalita.lower() != "Mista" and course.modalita != mode:
            flash("Modalità incompatibile!", category='error')
            return redirect(url_for('course.courseInfo', course_id=course_id))

        new_lesson = Lezione(corso=course_id, data=new_datetime, modalita=mode)

        if check_availability(new_lesson):
            try:
                db.session.add(new_lesson)
                db.session.commit()
                flash("Lezione creata con successo", category='success')
            except:
                db.session.rollback()
                flash("Non è stato possibile creare la lezione", category='error')
        else:
            flash("Data e/o professore non disponibile", category='error')
        return redirect(url_for('course.courseInfo', course_id=course_id))
    else:
        return render_template("nuovalezione.html", user=current_user, id=course_id)


# Funzione per rimuovere una lezione
@lesson.route('/lesson/remove_lesson/<int:lesson_id>')
@login_required
def remove_lesson(lesson_id):
    to_delete = Lezione.query.filter_by(id=lesson_id).first()
    try:
        db.session.delete(to_delete)
        db.session.commit()
        flash("Lezione cancellata", category='success')
    except:
        db.session.rollback()
        flash("Non è stato possibile cancellare la lezione", category='error')

    return redirect('/course/courses/dash')


def check_availability(new_lesson):
    available = new_lesson.data > datetime.now()
    if available:
        # Check if lesson already exists
        to_check = Lezione.query.filter_by(corso=new_lesson.corso, data=new_lesson.data).first()
        if not to_check:
            # Check whether the professor is busy or not with another lesson at that time
            course = Corso.query.filter_by(id=new_lesson.corso).first()
            professor_id = course.professore
            all_courses = Corso.query.filter_by(professore=professor_id).all()

            for c in all_courses:
                all_lessons = Lezione.query.filter_by(corso=c.id).all()
                for l in all_lessons:
                    if l.data == new_lesson.data:
                        flash("Il professore non è disponibile questo giorno!", category='error')
            return True
        else:
            flash("Questa lezione esiste già!", category='error')
            return False
    else:
        flash("Non puoi mettere una lezione nel passato!", category='error')
        return False
