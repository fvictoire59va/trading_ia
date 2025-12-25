import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import List
import logging
from sqlalchemy.orm import Session
import models
import time
import requests
from pycoingecko import CoinGeckoAPI

logger = logging.getLogger(__name__)

# Configuration CoinGecko
cg = CoinGeckoAPI()


class DataLoader:
    """Service pour charger les données historiques crypto et actions"""
    
    # Principales cryptos avec mapping CoinGecko
    CRYPTO_SYMBOLS = [
        "BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD", "ADA-USD",
        "SOL-USD", "DOGE-USD", "DOT-USD", "MATIC-USD", "AVAX-USD"
    ]
    
    # Mapping Yahoo -> CoinGecko
    COINGECKO_MAP = {
        "BTC-USD": "bitcoin",
        "ETH-USD": "ethereum",
        "BNB-USD": "binancecoin",
        "XRP-USD": "ripple",
        "ADA-USD": "cardano",
        "SOL-USD": "solana",
        "DOGE-USD": "dogecoin",
        "DOT-USD": "polkadot",
        "MATIC-USD": "matic-network",
        "AVAX-USD": "avalanche-2"
    }
    
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
    
    async def _load_from_coingecko(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Charge les données depuis CoinGecko"""
        try:
            coin_id = self.COINGECKO_MAP.get(symbol)
            if not coin_id:
                return pd.DataFrame()
            
            # Convertir les dates en timestamps
            start_ts = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
            end_ts = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())
            
            # Récupérer les données depuis CoinGecko
            logger.info(f"Recuperation depuis CoinGecko: {coin_id}")
            data = cg.get_coin_market_chart_range_by_id(
                id=coin_id,
                vs_currency='usd',
                from_timestamp=start_ts,
                to_timestamp=end_ts
            )
            
            if not data or 'prices' not in data:
                return pd.DataFrame()
            
            # Convertir en DataFrame
            prices = data['prices']
            df = pd.DataFrame(prices, columns=['timestamp', 'close'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Resample par jour et calculer OHLC
            df_daily = df.resample('D').agg({
                'close': ['first', 'max', 'min', 'last']
            })
            
            df_daily.columns = ['Open', 'High', 'Low', 'Close']
            df_daily['Volume'] = 0  # CoinGecko gratuit ne fournit pas le volume détaillé
            
            # Supprimer les lignes vides
            df_daily = df_daily.dropna()
            
            logger.info(f"CoinGecko: {len(df_daily)} enregistrements recuperes")
            return df_daily
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement depuis CoinGecko: {e}")
            return pd.DataFrame()
    
    async def _load_from_yahoo(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Charge les données depuis Yahoo Finance avec retry"""
        try:
            time.sleep(0.5)
            
            max_retries = 3
            df = pd.DataFrame()
            
            for attempt in range(max_retries):
                try:
                    ticker = yf.Ticker(symbol)
                    df = ticker.history(start=start_date, end=end_date, interval='1d')
                    
                    if not df.empty:
                        break
                    
                    if attempt < max_retries - 1:
                        logger.warning(f"Tentative {attempt + 1}/{max_retries} echouee, nouvelle tentative...")
                        time.sleep(2)
                except Exception as e:
                    logger.warning(f"Erreur lors de la tentative {attempt + 1}: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2)
            
            return df
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement depuis Yahoo: {e}")
            return pd.DataFrame()
    
    async def load_crypto_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        db: Session
    ) -> List[models.CryptoData]:
        """Charge les données historiques d'une crypto via CoinGecko ou Yahoo Finance"""
        try:
            logger.info(f"Chargement des donnees crypto pour {symbol}")
            
            # Essayer d'abord avec CoinGecko si disponible
            if symbol in self.COINGECKO_MAP:
                df = await self._load_from_coingecko(symbol, start_date, end_date)
                if not df.empty:
                    logger.info(f"Donnees chargees depuis CoinGecko pour {symbol}")
                else:
                    logger.warning(f"CoinGecko n'a pas retourne de donnees, essai avec Yahoo Finance")
                    df = await self._load_from_yahoo(symbol, start_date, end_date)
            else:
                # Utiliser Yahoo Finance pour les symboles non supportés par CoinGecko
                df = await self._load_from_yahoo(symbol, start_date, end_date)
            
            if df.empty:
                logger.warning(f"Aucune donnee trouvee pour {symbol}")
                return []
            
            # Sauvegarde en base de données
            records = []
            for index, row in df.iterrows():
                crypto_data = models.CryptoData(
                    symbol=symbol,
                    timestamp=index.to_pydatetime() if hasattr(index, 'to_pydatetime') else index,
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
            
            logger.info(f"OK {len(records)} enregistrements sauvegardes pour {symbol}")
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
            logger.info(f"Chargement des donnees boursieres pour {symbol}")
            
            # Utiliser Yahoo Finance pour les actions
            df = await self._load_from_yahoo(symbol, start_date, end_date)
            
            if df.empty:
                logger.warning(f"Aucune donnee trouvee pour {symbol}")
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
            
            logger.info(f"OK {len(records)} enregistrements sauvegardes pour {symbol}")
            return records
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement de {symbol}: {e}")
            db.rollback()
            raise
