from flask import Blueprint, render_template
from flask_login import login_required, current_user

from sito.models import Lista_corsi, get_professors

views = Blueprint('views', __name__)


# Route principale che reinderizza la home
@views.route('/')
@login_required
def home():
    print(f'current_user = {current_user}')
    print(current_user.isadmin)
    corsi = Lista_corsi()
    profs = get_professors(corsi)
    return render_template("home.html", user=current_user, corsi=corsi, len=len(corsi), prof=profs)
