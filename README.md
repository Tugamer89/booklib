# 📚 BookLib - Libreria di Casa

![WakaTime](https://wakatime.com/badge/user/423e1479-325a-4958-8d21-2d5f97c11efb/project/272222e8-abdd-452c-afa2-6d56e77b1387.svg)

Applicazione web full-stack per gestire e catalogare la propria libreria di casa. Permette di aggiungere, filtrare, cercare e ordinare libri, con caricamento copertine (tramite upload o Cloudinary), scansione ISBN via webcam e un sistema completo di gestione dell'account utente.

---

## ✨ Tecnologie Utilizzate

### 🖥️ Backend

- **Python 3.13+**
- **uv**: Per la gestione ultra-rapida delle dipendenze e degli ambienti virtuali.
- **FastAPI**: Per l'API RESTful ad alte prestazioni.
- **Uvicorn**: Come server ASGI.
- **SQLAlchemy & PostgreSQL**: Per l'ORM e l'interazione con il database relazionale.
- **Jinja2**: Per il rendering dei template HTML lato server (autenticazione, admin, email).
- **Cloudinary**: Per l'hosting e la gestione delle copertine dei libri.
- **pwdlib[bcrypt]**: Per l'hashing sicuro delle password (sostituisce Passlib).
- **Brevo API (sib-api-v3-sdk)**: Per l'invio di email transazionali (verifica account, reset password).
- **Pydantic**: Per la validazione e la gestione delle impostazioni.

### 🎨 Frontend

- **Vue.js 3**: Utilizzato tramite CDN e `importmap` per un frontend reattivo.
- **TailwindCSS**: Utilizzato tramite CDN per lo styling rapido e responsive.
- **html5-qrcode**: Libreria per la scansione di codici a barre/QR via webcam.
- **Javascript (ESM)**: Logica frontend moderna strutturata in moduli.

### 🛠️ Tooling & CI/CD

- **Pre-commit, Ruff & Prettier**: Per il linting e la formattazione automatica del codice (Python, JS, CSS, HTML, YAML).
- **GitHub Actions**: Pipeline CI per validazione codice, auto-formattazione e gestione automatica delle release tramite **Release Please**.

---

## 🚀 Funzionalità Principali

- ✅ **Gestione Account Avanzata**: Registrazione, Login sicuro, Verifica dell'indirizzo Email e procedura di Reset Password.
- ✅ **Gestione Sessioni**: Sessioni sicure basate su cookie con limite massimo per utente.
- ✅ **Pannello Admin**: Sezione per amministratori (`/admin/users`) per la gestione degli utenti.
- ✅ **CRUD Libri**: Funzionalità complete di Aggiungi, Modifica, Elimina e Visualizza libri.
- ✅ **Gestione Copertine**: Caricamento tramite file upload o incollando un URL (appoggiandosi a Cloudinary).
- ✅ **Integrazione Google Books**: Modal per cercare libri su Google Books e pre-compilare i form.
- ✅ **Scansione ISBN**: Scansione diretta tramite la webcam/fotocamera del dispositivo.
- ✅ **Filtri e Ordinamento**: Ricerca multi-campo e ordinamento dinamico con paginazione "Infinite Scroll".
- ✅ **Interfaccia Responsive & Dark Mode**: Ottimizzazione mobile/desktop e tema scuro salvato in `localStorage`.
- ✅ **Servizi Keep-Alive**: Job programmati opzionali tramite APScheduler per mantenere attivi il servizio web e il database.

---

## 📦 Installazione

### 1️⃣ Clona il repository

```bash
git clone [https://github.com/Tugamer89/booklib.git](https://github.com/Tugamer89/booklib.git)
cd booklib
```

### 2️⃣ Installa `uv` (se non lo possiedi)

Il progetto utilizza [uv](https://github.com/astral-sh/uv) per gestire l'ambiente Python. Puoi installarlo seguendo la documentazione ufficiale o tramite:

```bash
curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh
```

### Installa le dipendenze

Grazie al `Makefile` incluso, puoi sincronizzare l'ambiente virtuale e installare tutte le dipendenze (incluse quelle di sviluppo) con un solo comando:

```bash
make install
```

_(In alternativa: `uv sync`)_

### 4️⃣ Installa e configura PostgreSQL

- Assicurati di avere un server PostgreSQL in esecuzione.
- Crea un utente e un database:

```sql
CREATE USER bookuser WITH PASSWORD 'password';
CREATE DATABASE booklib OWNER bookuser;
GRANT ALL PRIVILEGES ON DATABASE booklib TO bookuser;
```

### 5️⃣ Configura e inizializza il progetto

Apri il file `setup.py` e modifica le variabili nella sezione `# --- CONFIGURAZIONE DA MODIFICARE ---` con i tuoi dati (credenziali DB, chiavi API Cloudinary, chiavi Brevo per le email, ecc.).

Esegui lo script `setup.py` tramite `uv`. Questo creerà il file `.env` con le chiavi segrete e configurerà le tabelle nel database:

```bash
uv run python setup.py
```

---

## ▶️ Avvio in locale

Puoi avviare rapidamente l'applicazione usando il comando `make`:

```bash
make run
```

_(Questo eseguirà `uv run uvicorn main:app --reload --port 8000`)_

L'app sarà disponibile su:
➡️ [`http://127.0.0.1:8000`](http://127.0.0.1:8000)

### 🛠️ Comandi di Sviluppo Utili

- `make format`: Formatta tutto il codice sorgente lanciando Prettier (HTML, CSS, JS, YAML) e Ruff (Python).
- `make hook-update`: Aggiorna le versioni dei tool all'interno di `pre-commit`.

---

## 📁 Struttura del progetto

```
.
├── .github/               # Workflow CI/CD (GitHub Actions, dependabot, release-please)
├── core/                  # Configurazione base, sicurezza, middleware, email, template
├── db/                    # Logica Database SQLAlchemy (modelli, database.py, crud.py)
├── routes/                # Router FastAPI (auth, books, admin, errors)
├── static/                # File statici (JS Vue.js, CSS Tailwind, Immagini)
├── templates/             # Template HTML Jinja2 (pagine web e template email)
├── utils/                 # Script di utility (keepalive, starter, logger, ecc.)
├── main.py                # Entry point FastAPI
├── setup.py               # Script interattivo per generare .env e tabelle
├── Makefile               # Comandi rapidi (install, format, run)
├── pyproject.toml         # Configurazione pacchetti e tool (uv, ruff)
├── uv.lock                # Lockfile delle dipendenze Python
├── .pre-commit-config.yaml# Configurazione per gli hook di commit (linting/format)
├── .prettierrc            # Regole di formattazione Prettier
└── README.md
```

---

## 📜 Licenza

MIT License — sentiti libero di usare e modificare.
