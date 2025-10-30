# 📚 BookLib - Libreria di Casa

![WakaTime](https://wakatime.com/badge/user/423e1479-325a-4958-8d21-2d5f97c11efb/project/272222e8-abdd-452c-afa2-6d56e77b1387.svg)

Applicazione web full-stack per gestire e catalogare la propria libreria di casa. Permette di aggiungere, filtrare, cercare e ordinare libri, con caricamento copertine (tramite upload o Cloudinary) e scansione ISBN via webcam.

---

## ✨ Tecnologie Utilizzate

### 🖥️ Backend
* **Python 3.10+**
* **FastAPI**: Per l'API RESTful ad alte prestazioni.
* **Uvicorn**: Come server ASGI.
* **SQLAlchemy**: Per l'ORM e l'interazione con il database.
* **PostgreSQL**: Come database relazionale.
* **Jinja2**: Per il rendering dei template HTML lato server (autenticazione, admin).
* **Cloudinary**: Per l'hosting e la gestione delle copertine dei libri.
* **Passlib**: Per l'hashing sicuro delle password.
* **Pydantic**: Per la validazione e la gestione delle impostazioni.
* **APScheduler**: Per i job programmati (es. keep-alive).

### 🎨 Frontend
* **Vue.js 3**: Utilizzato tramite CDN e `importmap` per un frontend reattivo.
* **TailwindCSS**: Utilizzato tramite CDN per lo styling rapido e responsive.
* **html5-qrcode**: Libreria per la scansione di codici a barre/QR via webcam.
* **Javascript (ESM)**: Logica frontend moderna strutturata in moduli (componenti, servizi, utility).

---

## 🚀 Funzionalità Principali
* ✅ **Autenticazione Utente**: Registrazione e Login sicuri.
* ✅ **Gestione Sessioni**: Sessioni sicure basate su cookie con limite massimo per utente.
* ✅ **Pannello Admin**: Sezione per amministratori (`/admin/users`) per la gestione degli utenti (reset password, elimina utente).
* ✅ **CRUD Libri**: Funzionalità complete di Aggiungi, Modifica, Elimina e Visualizza libri.
* ✅ **Gestione Copertine**: Caricamento di copertine tramite file upload o incollando un URL (l'app gestisce il download e l'upload su Cloudinary).
* ✅ **Integrazione Google Books**: Modal per cercare libri su Google Books e pre-compilare automaticamente il form di aggiunta.
* ✅ **Scansione ISBN**: Scansione dell'ISBN tramite la webcam/fotocamera del dispositivo.
* ✅ **Filtri e Ordinamento**: Filtri multi-campo (titolo, autore, ecc.) e ordinamento dinamico.
* ✅ **Paginazione "Infinite Scroll"**: Caricamento efficiente dei libri durante lo scorrimento.
* ✅ **Interfaccia Responsive**: Design ottimizzato per desktop e mobile con TailwindCSS.
* ✅ **Dark Mode**: Supporto per il tema scuro, con salvataggio della preferenza in `localStorage`.
* ✅ **Servizi Keep-Alive**: Job programmati opzionali per mantenere attivi il servizio web e il database (utile per piattaforme PaaS).

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
* Assicurati di avere un server PostgreSQL in esecuzione.
* Crea un utente e un database:

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
* **Apri il file `setup.py`** e modifica le variabili nella sezione `# --- CONFIGURAZIONE DA MODIFICARE ---` con i tuoi dati (credenziali DB, chiavi API Cloudinary, ecc.).
* Esegui lo script `setup.py`. Questo creerà il file `.env` con le chiavi segrete e configurerà le tabelle nel database:

```bash
python setup.py
```

---

## ▶️ Avvio in locale

Puoi usare lo script bash fornito (per ambienti Linux/macOS, dopo averlo reso eseguibile):
```bash
chmod +x start.sh
./start.sh
```

In alternativa, avvia manualmente il server (assicurati che PostgreSQL sia in esecuzione e l'ambiente virtuale sia attivo):
```bash
uvicorn main:app --reload --port 8000
```

L'app sarà disponibile su:
➡️ `http://127.0.0.1:8000`

---

## 📁 Struttura del progetto
```
.
├── main.py                # Entry point FastAPI (lifespan, middleware)
├── setup.py               # Script per generare .env e creare tabelle
├── core/                  # Configurazione e logica di base
│   ├── config.py          # Gestione settings (Pydantic)
│   ├── auth.py            # Helpers per autenticazione e dipendenze
│   ├── security.py        # Validatori credenziali
│   └── ...
├── db/                    # Logica Database
│   ├── database.py        # Configurazione engine e sessione SQLAlchemy
│   ├── models.py          # Modelli SQLAlchemy (User, Book, UserSession)
│   └── crud.py            # Funzioni CRUD (get_user, add_book, ecc.)
├── routes/                # Router FastAPI
│   ├── auth.py            # Route /auth, /logout
│   ├── books.py           # Route / (page), /books-data, /add, /edit, /delete
│   ├── admin.py           # Route /admin/*
│   ├── errors.py          # Gestori di eccezioni (404, 500...)
│   └── extras.py          # Route secondarie (favicon, keepalive)
├── static/                # File statici
│   ├── css/               # CSS
│   ├── js/                # Logica Vue.js e frontend
│   │   ├── components/    # Componenti Vue (BookCard, AddForm, Modals...)
│   │   ├── services/      # Servizio API (api.js)
│   │   ├── utils/         # Helpers (theme, formatters...)
│   │   ├── views/         # Vista principale Vue (Home.js)
│   │   └── main.js        # Entry point Vue
│   └── ...
├── templates/             # Template HTML Jinja2 (index.html, auth.html...)
├── requirements.txt       # Dipendenze Python
├── .env                   # (Generato da setup.py) Variabili d'ambiente
└── README.md
```

---

## 📜 Licenza

MIT License — sentiti libero di usare e modificare.

---

## 📋 TODO list
* Aggiungere `/.well-known/appspecific/com.chrome.devtools.json`
* Renderla compatibile come web-app