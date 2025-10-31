import os
import base64
from urllib.parse import quote_plus

ENV_FILE = ".env"

print("📚 Avvio script di setup per BookLib...")

def generate_base64_key(length=32):
    """Genera una chiave sicura codificata in Base64."""
    return base64.b64encode(os.urandom(length)).decode('utf-8')

def create_env_file():
    """
    Crea il file .env se non esiste, utilizzando le configurazioni
    specificate in questo script.
    """
    if os.path.exists(ENV_FILE):
        print(f"Il file {ENV_FILE} esiste già. Assicurati che sia configurato correttamente.")
        print("Saltando la creazione del .env...")
        return

    print(f"Creazione del file {ENV_FILE}...")

    # --- CONFIGURAZIONE DA MODIFICARE ---
    # Modifica queste variabili con i tuoi valori prima di eseguire lo script.

    # Configurazione Database PostgreSQL
    DB_USER = "bookuser"
    DB_PASSWORD = "password"  # Assicurati di usare una password sicura
    DB_HOST = "localhost"
    DB_PORT = "5432"
    DB_NAME = "booklib"

    # Configurazione Cloudinary (per le copertine)
    CLOUDINARY_CLOUD_NAME = "your_cloud_name"
    CLOUDINARY_API_KEY = "your_api_key"
    CLOUDINARY_API_SECRET = "your_api_secret"

    # Amministratori dell'applicazione (elenco di stringhe)
    ADMIN_USERS_LIST = ["admin", "admin2"]

    # Keepalive (opzionale, lascia stringa vuota "" per disabilitare)
    # Esempio: 'https://mia-app.onrender.com/'
    KEEPALIVE_URL = ""
    KEEPALIVE_CRON = "*/10 * * * *"
    KEEPALIVE_DB = ""  # Es. 'test' (un nome qualsiasi per attivare il keepalive DB)
    KEEPALIVE_DB_CRON = "0 0 */5 * *"

    # --- FINE CONFIGURAZIONE ---

    # Generazione chiavi segrete
    session_secret = generate_base64_key()
    csrf_secret = generate_base64_key()

    # Creazione URL database sicuro
    safe_password = quote_plus(DB_PASSWORD)
    database_url = f"postgresql://{DB_USER}:{safe_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # Conversione lista admin
    admin_users_str = ",".join(ADMIN_USERS_LIST)

    # Scrittura del file .env
    with open(ENV_FILE, "w") as f:
        f.write(f"SESSION_SECRET='{session_secret}'\n")
        f.write(f"CSRF_SECRET='{csrf_secret}'\n")
        f.write(f"DATABASE_URL='{database_url}'\n")
        f.write(f"CLOUDINARY_CLOUD_NAME='{CLOUDINARY_CLOUD_NAME}'\n")
        f.write(f"CLOUDINARY_API_KEY='{CLOUDINARY_API_KEY}'\n")
        f.write(f"CLOUDINARY_API_SECRET='{CLOUDINARY_API_SECRET}'\n")
        f.write(f"ADMIN_USERS='{admin_users_str}'\n")
        f.write(f"KEEPALIVE_URL='{KEEPALIVE_URL}'\n")
        f.write(f"KEEPALIVE_CRON='{KEEPALIVE_CRON}'\n")
        f.write(f"KEEPALIVE_DB='{KEEPALIVE_DB}'\n")
        f.write(f"KEEPALIVE_DB_CRON='{KEEPALIVE_DB_CRON}'\n")
        f.write("DEBUG='False'\n")

    print(f"File {ENV_FILE} creato con chiavi generate automaticamente.")

def create_tables(engine, base):
    """
    Crea tutte le tabelle definite nei modelli SQLAlchemy.
    """
    print("Creazione tabelle nel database...")
    try:
        base.metadata.create_all(bind=engine)
        print("Tabelle create con successo.")
    except Exception as e:
        print(f"Errore durante la creazione delle tabelle: {e}")
        print("Assicurati che il database sia in esecuzione e le credenziali in .env (o nello script) siano corrette.")

if __name__ == "__main__":
    # 1. Crea il file .env
    create_env_file()

    # 2. Importa la configurazione del DB (che ora legge da .env)
    #    e i modelli solo DOPO che .env è stato creato.
    print("\nImportazione configurazione e modelli DB...")
    try:
        from db.database import engine, Base
        # Importa i modelli per registrarli con Base
        from db.models import User, UserSession, Book
    except ImportError as e:
        print(f"Errore di importazione: {e}")
        print("Assicurati di eseguire questo script dalla directory principale del progetto.")
        exit(1)
    except Exception as e:
        print(f"Errore durante l'importazione dei moduli DB: {e}")
        print("Controlla la configurazione del database e le dipendenze installate.")
        exit(1)

    # 3. Crea le tabelle
    create_tables(engine, Base)

    print("\n✅ Setup completato con successo!")
    print("Ora puoi avviare l'applicazione con:")
    print("uvicorn main:app --reload")