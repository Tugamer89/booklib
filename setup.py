import os
import base64
from db.database import engine, Base

ENV_FILE = ".env"

def generate_base64_key(length=32):
    return base64.b64encode(os.urandom(length)).decode('utf-8')

def create_env_file():
    if os.path.exists(ENV_FILE):
        print(f"Il file {ENV_FILE} esiste già, saltando la creazione.")
        return

    session_secret = generate_base64_key()
    csrf_secret = generate_base64_key()
    # Cambia user, password, dbname se vuoi
    database_url = "postgresql://bookuser:password@localhost:5432/booklib"

    with open(ENV_FILE, "w") as f:
        f.write(f"SESSION_SECRET='{session_secret}'\n")
        f.write(f"CSRF_SECRET='{csrf_secret}'\n")
        f.write(f"DATABASE_URL='{database_url}'\n")

    print(f"File {ENV_FILE} creato con chiavi generate automaticamente.")

def create_tables():
    print("Creazione tabelle nel database...")
    Base.metadata.create_all(bind=engine)
    print("Tabelle create con successo.")

if __name__ == "__main__":
    create_env_file()
    create_tables()
