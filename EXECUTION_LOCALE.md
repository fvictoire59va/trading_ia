# Exécution en Local (Alternative à Docker)

Si vous rencontrez des problèmes avec Yahoo Finance dans Docker, vous pouvez exécuter le backend en local.

## Prérequis

- Python 3.11+
- PostgreSQL (via Docker ou local)

## Installation

### 1. Démarrer uniquement PostgreSQL avec Docker

```bash
docker-compose up -d postgres
```

### 2. Installer les dépendances Python

```bash
cd backend
pip install -r requirements.txt
```

### 3. Configurer les variables d'environnement

Créer un fichier `.env` dans le dossier backend :

```env
DATABASE_URL=postgresql://trading_user:trading_pass@localhost:5432/trading_ia
PYTHONUNBUFFERED=1
```

### 4. Démarrer le backend

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Démarrer le frontend

Dans un autre terminal :

```bash
cd frontend
pip install -r requirements.txt
python main.py
```

## Accès

- **Frontend** : http://localhost:8080
- **Backend API** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs

## Avantages de l'exécution en local

✅ Yahoo Finance fonctionne mieux (pas de blocage Docker)
✅ Rechargement automatique du code (--reload)
✅ Déboggage plus facile
✅ Performance légèrement meilleure

## Retour à Docker

Pour revenir à l'exécution complète avec Docker :

```bash
# Arrêter les processus locaux (Ctrl+C)
# Démarrer tous les services Docker
docker-compose up -d
```
