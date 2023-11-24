# Basi 2022

### Installazione
Installare le dipendenze
```
pip3 install -r requirements.txt
```
Editare il file .env(sample), e salvarlo come .env all'interno della cartella "sito"
```bash
> set FLASK_APP=hello
> flask run
 * Running on http://127.0.0.1:5000/
```
[Documentazione flask](https://flask.palletsprojects.com/en/2.1.x/quickstart/)

### Struttura file
```
static -> contiene file js e css
templates -> file html
.env -> file dove inserire database
*.py -> file importanti per il funzionamento del progetto
requirements.txt -> file contenente le dipendenze da scaricare
main.py -> app 
```

### Struttura  file ".env" (se manca)
Da inserire dentro la cartella sito
```
#dialect+driver://username:password@host:port/database
#postgresql://postgres:123@localhost/progBasi
DATABASE=INSERISCI QUI
```






