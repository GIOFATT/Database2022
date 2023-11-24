from datetime import date

from flask import Blueprint, render_template, flash, url_for
from flask_login import current_user, login_required
from sqlalchemy import and_
from werkzeug.utils import redirect

from sito import db
from sito.models import Iscrizione, Utente, Lista_corsi_popolati, Lista_corsi_popolati_prof

analitics = Blueprint("analitics", __name__, static_folder='static', template_folder='templates')


@analitics.route('/analitics')
@login_required
def analisi():
    dati = []
    if current_user.isadmin:
        corsi = Lista_corsi_popolati()
    else:
        corsi = Lista_corsi_popolati_prof(current_user.id)

    # Check if there actually are courses where analysis can be done
    if not corsi:
        flash("Non hai iscrizioni a nessun corso!", category='error')
        redirect(url_for('course.dash_corsi'))
    else:
        for c in corsi:
            print(c)
            id = c.id
            students = db.session.query(Utente). \
                filter(and_(Utente.id == Iscrizione.studente, Iscrizione.corso == id)).all()
            print(students)
            if students:
                # print(f'c= {c}')
                dati.append(analize(students))
            # print(f'dati = {dati}')
            # print(dati[0][1])
            # Corsi senza alcuno studente
            else:
                dati.append([0, 0, 0, 0, 0])

    # in dati, ogni elemento è un array costituito da: [n femmine, n maschi, n altro, età media, tot persone]
    return render_template('AnaliticaDocAd.html', user=current_user, corsi=corsi,
                           len_corsi=len(corsi), dati=dati)


# Ritorna un array contentente dati di corsi
def analize(students):
    tot_females = tot_males = tot_others = tot_age = 0
    for s in students:
        if s.genere == "femmina":
            tot_females += 1
        elif s.genere == "maschio":
            tot_males += 1
        else:
            tot_others += 1

        today = date.today()
        age = today.year - s.compleanno.year - ((today.month, today.day) < (s.compleanno.month, s.compleanno.day))
        tot_age += age

    tot = tot_females + tot_males + tot_others
    if tot > 0:
        females = tot_females / tot
        males = tot_males / tot
        others = tot_others / tot
        avg_age = tot_age / tot
        dati = [females, males, others, avg_age, tot]

        return dati