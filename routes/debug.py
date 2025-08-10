from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import OperationalError

router = APIRouter()

@router.get("/test-401")
async def test_401():
    raise HTTPException(status_code=401, detail="Non autorizzato")

@router.get("/test-404")
async def test_404():
    raise HTTPException(status_code=404, detail="Pagina non trovata")

@router.get("/test-500")
async def test_500():
    raise HTTPException(status_code=500, detail="Errore simulato")

@router.get("/test-validation")
async def test_validation(parametro: int):
    return {"ok": True}

@router.get("/test-operational-error")
async def test_operational_error():
    raise OperationalError("Simulated operational error", params=None, orig=None)

@router.get("/test-generic")
async def test_generic():
    raise ValueError("Errore Python generico")
