# 📚 BookLib - Home Library

![WakaTime](https://wakatime.com/badge/user/423e1479-325a-4958-8d21-2d5f97c11efb/project/272222e8-abdd-452c-afa2-6d56e77b1387.svg)

A full-stack web application to manage and catalogue your home library. Allows you to add, filter, search and sort books, with cover image management (via file upload or Cloudinary), barcode scanning via webcam, and a complete user account management system.

---

## ✨ Technologies Used

### 🖥️ Backend

- **Python 3.13+**
- **uv**: For ultra-fast dependency and virtual environment management.
- **FastAPI**: For the high-performance RESTful API.
- **Uvicorn**: As the ASGI server.
- **SQLAlchemy & PostgreSQL**: For ORM and relational database interaction.
- **Jinja2**: For server-side HTML template rendering (authentication, admin, email).
- **Cloudinary**: For hosting and managing book cover images.
- **pwdlib[bcrypt]**: For secure password hashing (replaces Passlib).
- **Brevo API (sib-api-v3-sdk)**: For sending transactional emails (account verification, password reset).
- **Pydantic**: For settings validation and management.

### 🎨 Frontend

- **Vue.js 3**: Used via CDN and `importmap` for a reactive frontend.
- **TailwindCSS**: Used via CDN for rapid and responsive styling.
- **html5-qrcode**: Library for scanning barcodes/QR codes via webcam.
- **Javascript (ESM)**: Modern frontend logic structured in modules.

### 🛠️ Tooling & CI/CD

- **Pre-commit, Ruff & Prettier**: For automatic linting and code formatting (Python, JS, CSS, HTML, YAML).
- **GitHub Actions**: CI pipeline for code validation, auto-formatting, and automatic release management via **Release Please**.

---

## 🚀 Key Features

- ✅ **Advanced Account Management**: Registration, secure Login, Email verification, and Password Reset flow.
- ✅ **Session Management**: Secure cookie-based sessions with a maximum limit per user.
- ✅ **Admin Panel**: Section for administrators (`/admin/users`) for user management.
- ✅ **Book CRUD**: Full Add, Edit, Delete and View functionality for books.
- ✅ **Cover Management**: Upload via file or by pasting a URL (backed by Cloudinary).
- ✅ **Google Books Integration**: Modal to search Google Books and pre-fill forms.
- ✅ **ISBN Scanning**: Direct scanning via the device's webcam/camera.
- ✅ **Filters and Sorting**: Multi-field search and dynamic sorting with Infinite Scroll pagination.
- ✅ **Responsive UI & Dark Mode**: Mobile/desktop optimisation and dark theme saved in `localStorage`.
- ✅ **Keep-Alive Services**: Optional scheduled jobs via APScheduler to keep the web service and database alive.

---

## 📦 Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/Tugamer89/booklib.git
cd booklib
```

### 2️⃣ Install `uv` (if you don't have it)

The project uses [uv](https://github.com/astral-sh/uv) to manage the Python environment. You can install it by following the official documentation or via:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Install dependencies

Thanks to the included `Makefile`, you can sync the virtual environment and install all dependencies (including dev ones) with a single command:

```bash
make install
```

_(Alternative: `uv sync`)_

### 4️⃣ Install and configure PostgreSQL

- Make sure you have a running PostgreSQL server.
- Create a user and a database:

```sql
CREATE USER bookuser WITH PASSWORD 'password';
CREATE DATABASE booklib OWNER bookuser;
GRANT ALL PRIVILEGES ON DATABASE booklib TO bookuser;
```

### 5️⃣ Configure and initialise the project

Open `setup.py` and modify the variables in the `# --- CONFIGURATION TO EDIT ---` section with your details (DB credentials, Cloudinary API keys, Brevo keys for emails, etc.).

Run the `setup.py` script via `uv`. This will create the `.env` file with the secret keys and set up the database tables:

```bash
uv run python setup.py
```

---

## ▶️ Local startup

You can quickly start the application using the `make` command:

```bash
make run
```

_(This will execute `uv run uvicorn main:app --reload --port 8000`)_

The app will be available at:
➡️ [`http://127.0.0.1:8000`](http://127.0.0.1:8000)

### 🛠️ Useful Development Commands

- `make format`: Formats all source code by running Prettier (HTML, CSS, JS, YAML) and Ruff (Python).
- `make hook-update`: Updates tool versions inside `pre-commit`.

---

## 📁 Project Structure

```
.
├── .github/               # CI/CD Workflows (GitHub Actions, dependabot, release-please)
├── core/                  # Base configuration, security, middleware, email, templates
├── db/                    # SQLAlchemy Database logic (models, database.py, crud.py)
├── routes/                # FastAPI Routers (auth, books, admin, errors)
├── static/                # Static files (Vue.js JS, Tailwind CSS, Images)
├── templates/             # Jinja2 HTML Templates (web pages and email templates)
├── utils/                 # Utility scripts (keepalive, starter, logger, etc.)
├── main.py                # FastAPI entry point
├── setup.py               # Interactive script to generate .env and tables
├── Makefile               # Quick commands (install, format, run)
├── pyproject.toml         # Package and tool configuration (uv, ruff)
├── uv.lock                # Python dependency lockfile
├── .pre-commit-config.yaml# Configuration for commit hooks (linting/format)
├── .prettierrc            # Prettier formatting rules
└── README.md
```

---

## 📜 License

MIT License — feel free to use and modify.
