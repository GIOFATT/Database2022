from sito import create_app  # Possibile perche sito ha init.py che lo rende un pacchetto python

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
    # debug permette di rerunnare il programma ad ogni cambiamento del sito
