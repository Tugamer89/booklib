import os
import base64

ENV_FILE = ".env"

def generate_base64_key(length=32):
    return base64.b64encode(os.urandom(length)).decode('utf-8')

def create_env_file():
    if os.path.exists(ENV_FILE):
        print(f"Il file {ENV_FILE} esiste già, saltando la creazione.")
        return

    session_secret = generate_base64_key()
    csrf_secret = generate_base64_key()
    database_url = "postgresql://bookuser:password@localhost:5432/booklib"
    cloudinary_cloud_name = "your_cloud_name"
    cloudinary_api_key = "your_api_key"
    cloudinary_api_secret = "your_api"
    admin_user = {"admin1", "admin2"}

    with open(ENV_FILE, "w") as f:
        f.write(f"SESSION_SECRET='{session_secret}'\n")
        f.write(f"CSRF_SECRET='{csrf_secret}'\n")
        f.write(f"DATABASE_URL='{database_url}'\n")
        f.write(f"CLOUDINARY_CLOUD_NAME='{cloudinary_cloud_name}'\n")
        f.write(f"CLOUDINARY_API_KEY='{cloudinary_api_key}'\n")
        f.write(f"CLOUDINARY_API_SECRET='{cloudinary_api_secret}'\n")
        f.write(f"ADMIN_USERS='{','.join(admin_user)}'\n")

    print(f"File {ENV_FILE} creato con chiavi generate automaticamente.")

def create_tables():
    print("Creazione tabelle nel database...")
    Base.metadata.create_all(bind=engine)
    print("Tabelle create con successo.")

if __name__ == "__main__":
    create_env_file()
    from db.database import engine, Base
    create_tables()
