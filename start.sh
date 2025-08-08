#!/bin/bash

echo "Avvio servizio PostgreSQL..."
sudo service postgresql start

echo "Avvio server FastAPI con uvicorn..."
source venv/bin/activate
uvicorn main:app --reload
