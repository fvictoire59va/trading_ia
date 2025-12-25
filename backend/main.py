from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
import logging

from database import get_db, engine
import models
import schemas
from services.data_loader import DataLoader

# Création des tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Trading IA Backend", version="1.0.0")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

data_loader = DataLoader()


@app.get("/")
def read_root():
    return {"message": "Trading IA Backend API", "status": "running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


# Routes pour les données historiques crypto
@app.get("/api/crypto/symbols", response_model=List[str])
def get_crypto_symbols():
    """Retourne la liste des symboles crypto disponibles"""
    return data_loader.get_available_crypto_symbols()


@app.post("/api/crypto/load")
async def load_crypto_data(
    symbol: str,
    start_date: str,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Charge les données historiques d'une crypto"""
    try:
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        data = await data_loader.load_crypto_data(symbol, start_date, end_date, db)
        return {
            "status": "success",
            "symbol": symbol,
            "records_loaded": len(data),
            "start_date": start_date,
            "end_date": end_date
        }
    except Exception as e:
        logger.error(f"Erreur lors du chargement des données crypto: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/crypto/data/{symbol}", response_model=List[schemas.CryptoData])
def get_crypto_data(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 1000,
    db: Session = Depends(get_db)
):
    """Récupère les données historiques d'une crypto depuis la DB"""
    query = db.query(models.CryptoData).filter(models.CryptoData.symbol == symbol)
    
    if start_date:
        query = query.filter(models.CryptoData.timestamp >= start_date)
    if end_date:
        query = query.filter(models.CryptoData.timestamp <= end_date)
    
    data = query.order_by(models.CryptoData.timestamp.desc()).limit(limit).all()
    return data


# Routes pour les données de bourse française
@app.get("/api/stocks/symbols", response_model=List[str])
def get_french_stock_symbols():
    """Retourne la liste des symboles boursiers français disponibles"""
    return data_loader.get_available_french_stocks()


@app.post("/api/stocks/load")
async def load_stock_data(
    symbol: str,
    start_date: str,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Charge les données historiques d'une action française"""
    try:
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        data = await data_loader.load_stock_data(symbol, start_date, end_date, db)
        return {
            "status": "success",
            "symbol": symbol,
            "records_loaded": len(data),
            "start_date": start_date,
            "end_date": end_date
        }
    except Exception as e:
        logger.error(f"Erreur lors du chargement des données boursières: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stocks/data/{symbol}", response_model=List[schemas.StockData])
def get_stock_data(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 1000,
    db: Session = Depends(get_db)
):
    """Récupère les données historiques d'une action depuis la DB"""
    query = db.query(models.StockData).filter(models.StockData.symbol == symbol)
    
    if start_date:
        query = query.filter(models.StockData.timestamp >= start_date)
    if end_date:
        query = query.filter(models.StockData.timestamp <= end_date)
    
    data = query.order_by(models.StockData.timestamp.desc()).limit(limit).all()
    return data


@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    """Retourne des statistiques sur les données en base"""
    crypto_count = db.query(models.CryptoData).count()
    stock_count = db.query(models.StockData).count()
    
    crypto_symbols = db.query(models.CryptoData.symbol).distinct().count()
    stock_symbols = db.query(models.StockData.symbol).distinct().count()
    
    return {
        "crypto": {
            "total_records": crypto_count,
            "symbols_count": crypto_symbols
        },
        "stocks": {
            "total_records": stock_count,
            "symbols_count": stock_symbols
        }
    }
