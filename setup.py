import base64
import os
from urllib.parse import quote_plus

ENV_FILE = ".env"

print("📚 Starting BookLib setup script...")


def generate_base64_key(length=32):
    """Generates a secure Base64-encoded key."""
    return base64.b64encode(os.urandom(length)).decode("utf-8")


def create_env_file():
    """Creates the .env file if it doesn't exist, using the configuration
    specified in this script.
    """
    if os.path.exists(ENV_FILE):
        print(f"The {ENV_FILE} file already exists. Make sure it is configured correctly.")
        print("Skipping .env creation...")
        return

    print(f"Creating {ENV_FILE} file...")

    # --- CONFIGURATION TO EDIT ---
    # Modify these variables with your values before running the script.

    # PostgreSQL Database Configuration
    DB_USER = "bookuser"
    DB_PASSWORD = "password"  # Make sure to use a strong password
    DB_HOST = "localhost"
    DB_PORT = "5432"
    DB_NAME = "booklib"

    # Cloudinary Configuration (for cover images)
    CLOUDINARY_CLOUD_NAME = "your_cloud_name"
    CLOUDINARY_API_KEY = "your_api_key"
    CLOUDINARY_API_SECRET = "your_api_secret"

    # Application administrators (list of strings)
    ADMIN_USERS_LIST = ["admin", "admin2"]

    # Keepalive (optional, leave empty string "" to disable)
    # Example: 'https://my-app.onrender.com/'
    KEEPALIVE_URL = ""
    KEEPALIVE_CRON = "*/10 * * * *"
    KEEPALIVE_DB = ""  # E.g. 'test' (any name to enable DB keepalive)
    KEEPALIVE_DB_CRON = "0 0 */5 * *"

    # --- END OF CONFIGURATION ---

    # Generate secret keys
    session_secret = generate_base64_key()
    csrf_secret = generate_base64_key()

    # Create secure database URL
    safe_password = quote_plus(DB_PASSWORD)
    database_url = f"postgresql://{DB_USER}:{safe_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # Convert admin list
    admin_users_str = ",".join(ADMIN_USERS_LIST)

    # Write the .env file
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

    print(f"{ENV_FILE} file created with auto-generated keys.")


def create_tables(engine, base):
    """Creates all tables defined in the SQLAlchemy models."""
    print("Creating database tables...")
    try:
        base.metadata.create_all(bind=engine)
        print("Tables created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")
        print(
            "Make sure the database is running and the credentials in .env (or in the script) are correct."
        )


if __name__ == "__main__":
    # 1. Create the .env file
    create_env_file()

    # 2. Import DB configuration (which now reads from .env)
    #    and models only AFTER .env has been created.
    print("\nImporting DB configuration and models...")
    try:
        from db.database import Base, engine
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure you run this script from the project root directory.")
        exit(1)
    except Exception as e:
        print(f"Error importing DB modules: {e}")
        print("Check the database configuration and installed dependencies.")
        exit(1)

    # 3. Create the tables
    create_tables(engine, Base)

    print("\n✅ Setup completed successfully!")
    print("You can now start the application with:")
    print("uvicorn main:app --reload")
