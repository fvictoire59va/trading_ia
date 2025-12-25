import yfinance as yf
import pandas as pd
from datetime import datetime
from typing import List
import logging
from sqlalchemy.orm import Session
import models
import time

logger = logging.getLogger(__name__)

# Configuration pour éviter le blocage de Yahoo Finance
yf.pdr_override()


class DataLoader:
    """Service pour charger les données historiques crypto et actions"""
    
    # Principales cryptos
    CRYPTO_SYMBOLS = [
        "BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD", "ADA-USD",
        "SOL-USD", "DOGE-USD", "DOT-USD", "MATIC-USD", "AVAX-USD"
    ]
    
    # Principales actions françaises (CAC 40)
    FRENCH_STOCKS = [
        "MC.PA",      # LVMH
        "OR.PA",      # L'Oréal
        "SAN.PA",     # Sanofi
        "TTE.PA",     # TotalEnergies
        "AIR.PA",     # Airbus
        "BNP.PA",     # BNP Paribas
        "CA.PA",      # Carrefour
        "ACA.PA",     # Crédit Agricole
        "CS.PA",      # AXA
        "DG.PA",      # Vinci
        "EN.PA",      # Bouygues
        "SGO.PA",     # Saint-Gobain
        "RMS.PA",     # Hermès
        "KER.PA",     # Kering
        "UL.PA",      # Unilever
    ]
    
    def get_available_crypto_symbols(self) -> List[str]:
        """Retourne la liste des symboles crypto disponibles"""
        return self.CRYPTO_SYMBOLS
    
    def get_available_french_stocks(self) -> List[str]:
        """Retourne la liste des actions françaises disponibles"""
        return self.FRENCH_STOCKS
    
    async def load_crypto_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        db: Session
    ) -> List[models.CryptoData]:
        """Charge les données historiques d'une crypto via Yahoo Finance"""
        try:
            logger.info(f"Chargement des données crypto pour {symbol}")
            
            # Petit délai pour éviter le rate limiting
            time.sleep(0.5)
            
            # Téléchargement des données avec retry
            max_retries = 3
            df = pd.DataFrame()
            
            for attempt in range(max_retries):
                try:
                    ticker = yf.Ticker(symbol)
                    df = ticker.history(start=start_date, end=end_date, interval='1d')
                    
                    if not df.empty:
                        break
                    
                    if attempt < max_retries - 1:
                        logger.warning(f"Tentative {attempt + 1}/{max_retries} échouée, nouvelle tentative...")
                        time.sleep(2)
                except Exception as e:
                    logger.warning(f"Erreur lors de la tentative {attempt + 1}: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2)
            
            if df.empty:
                logger.warning(f"Aucune donnée trouvée pour {symbol} après {max_retries} tentatives")
                return []
            
            # Sauvegarde en base de données
            records = []
            for index, row in df.iterrows():
                crypto_data = models.CryptoData(
                    symbol=symbol,
                    timestamp=index.to_pydatetime(),
                    open=float(row['Open']),
                    high=float(row['High']),
                    low=float(row['Low']),
                    close=float(row['Close']),
                    volume=float(row['Volume'])
                )
                records.append(crypto_data)
            
            # Insertion par lot
            db.bulk_save_objects(records)
            db.commit()
            
            loPetit délai pour éviter le rate limiting
            time.sleep(0.5)
            
            # Téléchargement des données avec retry
            max_retries = 3
            df = pd.DataFrame()
            
            for attempt in range(max_retries):
                try:
                    ticker = yf.Ticker(symbol)
                    df = ticker.history(start=start_date, end=end_date, interval='1d')
                    
                    if not df.empty:
                        break
                    
                    if attempt < max_retries - 1:
                        logger.warning(f"Tentative {attempt + 1}/{max_retries} échouée, nouvelle tentative...")
                        time.sleep(2)
                except Exception as e:
                    logger.warning(f"Erreur lors de la tentative {attempt + 1}: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2)
            
            if df.empty:
                logger.warning(f"Aucune donnée trouvée pour {symbol} après {max_retries} tentatives")
                return []
            
            # Sauvegarde en base de données
            records = []
            for index, row in df.iterrows():
                crypto_data = models.CryptoData(
                    symbol=symbol,
                    timestamp=index.to_pydatetime(),
                    open=float(row['Open']),
                    high=float(row['High']),
                    low=float(row['Low']),
                    close=float(row['Close']),
                    volume=float(row['Volume'])
                )
                records.append(crypto_data)
            
            # Insertion par lot
            db.bulk_save_objects(records)
            db.commit()
            
            logger.info(f"✓ {len(records)} enregistrements sauvegardés pour {symbol}")
            return records
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement de {symbol}: {e}")
            db.rollback()
            raise
    
    async def load_stock_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        db: Session
    ) -> List[models.StockData]:
        """Charge les données historiques d'une action française via Yahoo Finance"""
        try:
            logger.info(f"Chargement des données boursières pour {symbol}")
            
            # Petit délai pour éviter le rate limiting
            time.sleep(0.5)
            
            # Téléchargement des données avec retry
            max_retries = 3
            df = pd.DataFrame()
            
            for attempt in range(max_retries):
                try:
                    ticker = yf.Ticker(symbol)
                    df = ticker.history(start=start_date, end=end_date, interval='1d')
                    
                    if not df.empty:
                        break
                    
                    if attempt < max_retries - 1:
                        logger.warning(f"Tentative {attempt + 1}/{max_retries} échouée, nouvelle tentative...")
                        time.sleep(2)
                except Exception as e:
                    logger.warning(f"Erreur lors de la tentative {attempt + 1}: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2)
            
            if df.empty:
                logger.warning(f"Aucune donnée trouvée pour {symbol} après {max_retries} tentatives")
                return []
            
            # Sauvegarde en base de données
            records = []
            for index, row in df.iterrows():
                stock_data = models.StockData(
                    symbol=symbol,
                    timestamp=index.to_pydatetime(),
                    open=float(row['Open']),
                    high=float(row['High']),
                    low=float(row['Low']),
                    close=float(row['Close']),
                    volume=float(row['Volume'])
                )
                records.append(stock_data)
            
            # Insertion par lot
            db.bulk_save_objects(records)
            db.commit()
            
            logger.info(f"✓ {len(records)} enregistrements sauvegardés pour {symbol}")
            return records
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement de {symbol}: {e}")
            db.rollback()
            raise
