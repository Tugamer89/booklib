#!/bin/bash

echo "Avvio servizio PostgreSQL..."
sudo systemctl start postgresql

echo "Avvio server FastAPI con uvicorn..."
source venv/bin/activate
uvicorn main:app --reload
