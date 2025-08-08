# 📚 Libreria di Casa

![WakaTime](https://wakatime.com/badge/user/423e1479-325a-4958-8d21-2d5f97c11efb/project/272222e8-abdd-452c-afa2-6d56e77b1387.svg)

Applicazione web per gestire e catalogare la propria libreria di casa.  
Permette di aggiungere, filtrare, cercare e ordinare libri, con caricamento copertine e scansione ISBN via webcam.

---

## 🚀 Funzionalità principali
- ✅ Autenticazione utente (login / registrazione)
- ✅ Gestione sicura sessioni + CSRF
- ✅ Catalogazione con copertina (file o URL da Google Books API)
- ✅ Ricerca, filtri e ordinamento personalizzati
- ✅ Scansione ISBN da webcam
- ✅ Interfaccia responsive con TailwindCSS
- ✅ Tema e design ottimizzati

---

## 📦 Installazione

### 1️⃣ Clona il repository
```bash
git clone https://github.com/Tugamer89/booklib.git
cd booklib
```

### 2️⃣ Crea ed attiva l'ambiente virtuale
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3️⃣ Installa le dipendenze
```bash
pip install -r requirements.txt
```

### 4️⃣ Installa e configura PostgreSQL

* Vedi istruzioni specifiche per il tuo sistema operativo (Ubuntu, macOS, Windows).
* Crea utente e database PostgreSQL:

```bash
sudo -u postgres psql
```

```sql
CREATE USER bookuser WITH PASSWORD 'password';
CREATE DATABASE booklib OWNER bookuser;
GRANT ALL PRIVILEGES ON DATABASE booklib TO bookuser;
\q
```

### 5️⃣ Configura e inizializza il progetto

* Apri lo script `setup.py` e modifica le variabili `database_url`, `cloudinary_cloud_name`, `cloudinary_api_key` e `cloudinary_api_secret`.
* Esegui lo script `setup.py` che crea il file `.env` con le chiavi segrete e crea le tabelle nel database:

```bash
python setup.py
```



---

## ▶️ Avvio in locale

Per avviare PostgreSQL e il server FastAPI usa lo script bash:

```bash
./start.sh
```

L'app sarà disponibile su:
➡️ `http://127.0.0.1:8000`

---

## 📁 Struttura del progetto

```
.
├── main.py                # Entry point FastAPI
├── core/                  # 
├── db/                    # 
├── routes/                # 
├── utils/                 # 
├── static/                # File statici (JS, immagini)
├── templates/             # Template HTML Jinja2
├── requirements.txt       # Dipendenze Python
├── .env                   # Variabili d'ambiente
├── .gitignore
└── README.md
```

---

## 📜 Licenza

MIT License — sentiti libero di usare e modificare.

---

## 📋 TODO list

* Aggiungere azione modifica
* Aggiungere compatibiltà per mobile
