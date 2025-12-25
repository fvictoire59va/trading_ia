# Trading IA 📈

Plateforme de trading algorithmique avec intelligence artificielle pour l'analyse des crypto-monnaies et des actions françaises.

## Description

Ce projet implémente un système de trading automatisé utilisant des techniques d'intelligence artificielle pour analyser les marchés financiers. Il offre une interface moderne pour charger, stocker et visualiser les données historiques de trading.

### Fonctionnalités

- ✅ Chargement de données historiques de **crypto-monnaies** (Bitcoin, Ethereum, etc.)
- ✅ Chargement de données historiques d'**actions françaises** (CAC 40)
- ✅ Stockage persistant dans **PostgreSQL**
- ✅ Interface web moderne avec **NiceGUI**
- ✅ Graphiques interactifs en chandeliers (candlestick charts)
- ✅ API REST avec **FastAPI**
- ✅ Architecture **Docker** complète

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│   Frontend      │────▶│    Backend      │────▶│   PostgreSQL    │
│   (NiceGUI)     │     │   (FastAPI)     │     │   (Database)    │
│   Port: 8080    │     │   Port: 8000    │     │   Port: 5432    │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Prérequis

- **Docker** et **Docker Compose**
- Au moins 2 GB de RAM disponible
- Connexion Internet (pour télécharger les données de marché)

## Installation et Démarrage

### 1. Cloner le dépôt

```bash
git clone https://github.com/fvictoire59va/trading_ia.git
cd trading_ia
```

### 2. Démarrer l'infrastructure

```bash
# Démarrer tous les services
docker-compose up -d

# Vérifier les logs
docker-compose logs -f
```

### 3. Accéder à l'application

- **Frontend (Interface utilisateur)** : http://localhost:8080
- **Backend API** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs

## Structure du projet

```
trading_ia/
├── backend/                 # Backend FastAPI
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py             # Point d'entrée de l'API
│   ├── database.py         # Configuration SQLAlchemy
│   ├── models.py           # Modèles de données
│   ├── schemas.py          # Schémas Pydantic
│   └── services/
│       └── data_loader.py  # Service de chargement de données
├── frontend/               # Frontend NiceGUI
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py            # Interface utilisateur
├── database/              # Configuration PostgreSQL
│   └── init.sql          # Script d'initialisation
├── data/                 # Dossier pour les données
├── docker-compose.yml    # Orchestration Docker
├── .gitignore
└── README.md
```

## Utilisation

### Charger des données de crypto-monnaies

1. Accédez à l'onglet **"Crypto-monnaies"**
2. Sélectionnez un symbole (ex: BTC-USD)
3. Choisissez les dates de début et de fin
4. Cliquez sur **"Charger les données"**
5. Cliquez sur **"Afficher les données"** pour voir le graphique

**Note** : Les données crypto utilisent l'API CoinGecko (gratuite et fiable). En cas d'échec, le système bascule automatiquement vers Yahoo Finance.

### Charger des données d'actions françaises

1. Accédez à l'onglet **"Bourse Française"**
2. Sélectionnez un symbole (ex: MC.PA pour LVMH)
3. Choisissez les dates de début et de fin
4. Cliquez sur **"Charger les données"**
5. Cliquez sur **"Afficher les données"** pour voir le graphique

**Note** : Les données boursières utilisent Yahoo Finance. En raison de limitations de l'API gratuite, certaines requêtes peuvent échouer. Essayez avec des périodes plus courtes (30-90 jours) pour de meilleurs résultats.

### Voir les statistiques

Accédez à l'onglet **"Statistiques"** pour voir :
- Nombre total de symboles chargés
- Nombre total d'enregistrements en base

## API Endpoints

### Crypto-monnaies

- `GET /api/crypto/symbols` - Liste des symboles crypto disponibles
- `POST /api/crypto/load` - Charger les données historiques
- `GET /api/crypto/data/{symbol}` - Récupérer les données d'un symbole

### Actions françaises

- `GET /api/stocks/symbols` - Liste des symboles boursiers disponibles
- `POST /api/stocks/load` - Charger les données historiques
- `GET /api/stocks/data/{symbol}` - Récupérer les données d'un symbole

### Statistiques

- `GET /api/stats` - Statistiques globales de la base de données

## Commandes Docker utiles

```bash
# Démarrer les services
docker-compose up -d

# Arrêter les services
docker-compose down

# Voir les logs
docker-compose logs -f [service_name]

# Rebuild après modification du code
docker-compose up -d --build

# Supprimer tout (y compris les données)
docker-compose down -v
```

## Développement

### Backend (FastAPI)

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend (NiceGUI)

```bash
cd frontend
pip install -r requirements.txt
python main.py
```

## Technologies utilisées

- **Backend**: FastAPI, SQLAlchemy, Pandas
- **Frontend**: NiceGUI, Plotly
- **Base de données**: PostgreSQL
- **Data sources**: Yahoo Finance (yfinance)
- **Containerisation**: Docker, Docker Compose

## Données supportées

### Crypto-monnaies (via Yahoo Finance)
- Bitcoin (BTC-USD)
- Ethereum (ETH-USD)
- Binance Coin (BNB-USD)
- Ripple (XRP-USD)
- Cardano (ADA-USD)
- Et bien d'autres...

### Actions françaises (CAC 40)
- LVMH (MC.PA)
- L'Oréal (OR.PA)
- TotalEnergies (TTE.PA)
- Sanofi (SAN.PA)
- Airbus (AIR.PA)
- BNP Paribas (BNP.PA)
- Et bien d'autres...

## Roadmap

- [ ] Intégration de modèles d'IA pour la prédiction
- [ ] Backtesting de stratégies
- [ ] Alertes en temps réel
- [ ] Support de plus de sources de données
- [ ] Dashboard de performance

## Licence

À définir

## Contact

Projet maintenu par [fvictoire59va](https://github.com/fvictoire59va)
