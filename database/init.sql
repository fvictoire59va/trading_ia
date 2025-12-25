-- Script d'initialisation de la base de données Trading IA

-- Extension pour les fonctions de date/heure
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table pour les données crypto
CREATE TABLE IF NOT EXISTS crypto_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    open DOUBLE PRECISION NOT NULL,
    high DOUBLE PRECISION NOT NULL,
    low DOUBLE PRECISION NOT NULL,
    close DOUBLE PRECISION NOT NULL,
    volume DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, timestamp)
);

-- Index pour optimiser les requêtes
CREATE INDEX IF NOT EXISTS idx_crypto_symbol ON crypto_data(symbol);
CREATE INDEX IF NOT EXISTS idx_crypto_timestamp ON crypto_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_crypto_symbol_timestamp ON crypto_data(symbol, timestamp);

-- Table pour les données boursières
CREATE TABLE IF NOT EXISTS stock_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    open DOUBLE PRECISION NOT NULL,
    high DOUBLE PRECISION NOT NULL,
    low DOUBLE PRECISION NOT NULL,
    close DOUBLE PRECISION NOT NULL,
    volume DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, timestamp)
);

-- Index pour optimiser les requêtes
CREATE INDEX IF NOT EXISTS idx_stock_symbol ON stock_data(symbol);
CREATE INDEX IF NOT EXISTS idx_stock_timestamp ON stock_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_stock_symbol_timestamp ON stock_data(symbol, timestamp);

-- Commentaires sur les tables
COMMENT ON TABLE crypto_data IS 'Données historiques des crypto-monnaies';
COMMENT ON TABLE stock_data IS 'Données historiques des actions françaises';
