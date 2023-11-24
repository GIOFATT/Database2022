from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from . import db
from .models import Utente, Corso, Iscrizione

popola = Blueprint("popola", __name__, static_folder='static', template_folder='templates')

'''
ATTENZIONE!
Questo file contiene funzioni non controllate per popolare il database!
Collegato al file debug.html e tramite blueprint, verranno poi eliminati a consegna del progetto
DA USARE SOLO A SCOPO DI TESTING E DEBUG PER PIGRIZIA
'''


@popola.route('/debug')
@login_required
def debug():
    return render_template("debug.html", user=current_user)


@popola.route('/popolautenti')
def popusers():
    popUtenti()
    return redirect(url_for('views.home'))


@popola.route('/popolacorsi')
def popucourse():
    popCorsi()
    return redirect(url_for('views.home'))


@popola.route('/popolaiscrizioni')
def popiscrizioni():
    popIscrizioni()
    return redirect(url_for('views.home'))


@popola.route('/popolaTrigger')
def poptrigger():
    popTrigger()
    return redirect(url_for('views.home'))


def popUtenti():
    db.session.add_all([
        Utente(nome='Giovanni', cognome='Esposito', compleanno='1999-09-14',
               email='giovanniesposito@gmail.com',
               password=generate_password_hash('giovannifigo', method='sha256'),
               genere='maschio'),
        Utente(nome='Lucia', cognome='Galbanino', compleanno='1999-09-14',
               email='luciagalbanino@gmail.com',
               password=generate_password_hash('mozzarelle123', method='sha256'),
               genere='femmina'),
        Utente(nome='Roberto', cognome='Benigno', compleanno='1999-09-14',
               email='robbino@gmail.com',
               password=generate_password_hash('password123', method='sha256'),
               genere='maschio'),
        Utente(nome='Testo', cognome='Sterone', compleanno='1999-09-14',
               email='testosterone@gmail.com',
               password=generate_password_hash('erabellocosi', method='sha256'),
               genere='altro'),
        Utente(nome='Arty', cognome='Figo', compleanno='1999-09-14',
               email='artyfigo@gmail.com',
               password=generate_password_hash('artyfigo', method='sha256'),
               genere='altro', isprofessor=True, isadmin=False),
    ])
    db.session.commit()


def popCorsi():
    db.session.add_all([
        Corso(nome='Introduzione alla pagliacceria', professore='6', descrizione='test', modalita='Offline'),
        Corso(nome='Ingegneria dei tendoni', professore='6', descrizione='test', modalita='Online'),
        Corso(nome='Pagliaccieria del software', professore='6', descrizione='test', modalita='Mista')
    ])
    db.session.commit()


# Funzione molto pericolosa perchè associa agli id corsi il loro id studente
# Consiglio controllo database
def popIscrizioni():
    db.session.add_all([
        Iscrizione(corso=1, studente=2),
        Iscrizione(corso=2, studente=3),
        Iscrizione(corso=3, studente=4),
    ])
    db.session.commit()


def popTrigger():
    db.session.execute(
        """
        CREATE OR REPLACE FUNCTION check_mode_on_change()
        RETURNS TRIGGER AS $$
            DECLARE
            mista varchar(6) = 'Mista';
            BEGIN
                IF OLD.modalita <> NEW.modalita AND NEW.modalita <> mista THEN
                    UPDATE lezioni
                    SET modalita = NEW.modalita
                    WHERE corso = NEW.id AND data > NOW();

                END IF;
                RETURN NEW;
            END;
        $$ LANGUAGE plpgsql;
        
        
        DROP TRIGGER IF EXISTS check_mode_on_change ON corsi;
        CREATE TRIGGER check_mode_on_change
            AFTER UPDATE ON corsi
            FOR EACH ROW
        EXECUTE PROCEDURE check_mode_on_change();
        """)

    db.session.execute(
        """
        CREATE OR REPLACE FUNCTION check_course_operation_permission()
        RETURNS TRIGGER AS $$
            DECLARE
                conta integer;
            BEGIN
                WITH date_disponibili(date) AS
                    (SELECT l.data
                    FROM corsi c JOIN lezioni l ON c.id = l.corso JOIN utenti u ON c.professore = u.id
                    WHERE l.data > NOW() AND l.corso = NEW.id AND NEW.data = l.data)
                    SELECT COUNT(*) INTO conta FROM date_disponibili;

                IF conta > 0 THEN
                    RETURN NULL;
                END IF;
                RETURN NEW;
            END;
        $$ LANGUAGE plpgsql;
        
        
        DROP TRIGGER IF EXISTS check_course_operation_permission ON lezioni;
        CREATE TRIGGER check_course_operation_permission
            BEFORE INSERT ON lezioni
            FOR EACH ROW
        EXECUTE PROCEDURE check_course_operation_permission();
        
        """)

    db.session.execute(
        """
        CREATE OR REPLACE FUNCTION check_prof_or_admin_insert()
        RETURNS TRIGGER AS $$
            BEGIN
                IF (NEW.isprofessor == ‘True’ AND NEW.isadmin == ‘True’) THEN
                    SET NEW.isprofessor = ‘False’;
                    SET NEW.isadmin = ‘False’;
                    RETURN NEW;
                END IF;
            END;
        $$ LANGUAGE plpgsql;


        DROP TRIGGER IF EXISTS check_prof_or_admin_insert ON utenti;
        CREATE TRIGGER check_prof_or_admin_insert
            BEFORE INSERT ON utenti
            FOR EACH ROW
        EXECUTE PROCEDURE check_prof_or_admin_insert();
        """)

    db.session.execute(
        """
        CREATE OR REPLACE FUNCTION check_prof_or_admin_update()
        RETURNS TRIGGER AS $$
            BEGIN
                IF (NEW.isprofessor = TRUE AND NEW.isadmin = TRUE) THEN
                    NEW.isprofessor = OLD.isprofessor;
                    NEW.isadmin = OLD.isadmin;
                END IF;
                RETURN NEW;
            END;
        $$ LANGUAGE plpgsql;


        DROP TRIGGER IF EXISTS check_prof_or_admin_update ON utenti;
        CREATE TRIGGER check_prof_or_admin_update
            BEFORE UPDATE ON utenti
            FOR EACH ROW
        EXECUTE PROCEDURE check_prof_or_admin_update();
        """)

    db.session.commit()
