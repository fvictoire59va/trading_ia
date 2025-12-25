from nicegui import ui, app
import requests
import os
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
from typing import Optional

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


class TradingIAApp:
    def __init__(self):
        self.current_data = None
        self.current_symbol = None
        self.data_type = "crypto"  # crypto ou stocks
        
    def create_chart(self, data: list, symbol: str) -> go.Figure:
        """Crée un graphique en chandeliers"""
        if not data:
            return go.Figure()
        
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        fig = go.Figure(data=[go.Candlestick(
            x=df['timestamp'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name=symbol
        )])
        
        fig.update_layout(
            title=f'{symbol} - Données historiques',
            yaxis_title='Prix',
            xaxis_title='Date',
            template='plotly_dark',
            height=600
        )
        
        return fig


# Initialisation de l'application
trading_app = TradingIAApp()


@ui.page('/')
def index():
    """Page principale de l'application"""
    
    with ui.header().classes('bg-blue-900 text-white'):
        ui.label('Trading IA - Plateforme d\'Analyse').classes('text-2xl font-bold')
    
    with ui.tabs().classes('w-full') as tabs:
        crypto_tab = ui.tab('Crypto-monnaies', icon='currency_bitcoin')
        stocks_tab = ui.tab('Bourse Française', icon='trending_up')
        stats_tab = ui.tab('Statistiques', icon='analytics')
    
    with ui.tab_panels(tabs, value=crypto_tab).classes('w-full'):
        # Panel Crypto
        with ui.tab_panel(crypto_tab):
            create_crypto_panel()
        
        # Panel Actions
        with ui.tab_panel(stocks_tab):
            create_stocks_panel()
        
        # Panel Statistiques
        with ui.tab_panel(stats_tab):
            create_stats_panel()


def create_crypto_panel():
    """Panel pour les crypto-monnaies"""
    ui.label('Chargement de données Crypto').classes('text-xl font-bold mb-4')
    
    with ui.card().classes('w-full p-4'):
        with ui.row().classes('w-full gap-4'):
            # Sélection du symbole
            symbol_select = ui.select(
                label='Symbole',
                options=[],
                value=None
            ).classes('w-64')
            
            # Dates
            start_date = ui.input(
                label='Date de début',
                value=(datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            ).classes('w-48')
            
            end_date = ui.input(
                label='Date de fin',
                value=datetime.now().strftime('%Y-%m-%d')
            ).classes('w-48')
        
        # Boutons d'action
        with ui.row().classes('gap-2 mt-4'):
            load_btn = ui.button('Charger les données', icon='download')
            show_btn = ui.button('Afficher les données', icon='visibility')
        
        status_label = ui.label('').classes('mt-2')
        
        # Zone de graphique
        chart_container = ui.column().classes('w-full mt-4')
    
    # Chargement des symboles disponibles
    async def load_crypto_symbols():
        try:
            response = requests.get(f'{BACKEND_URL}/api/crypto/symbols')
            if response.status_code == 200:
                symbols = response.json()
                symbol_select.options = symbols
                if symbols:
                    symbol_select.value = symbols[0]
        except Exception as e:
            ui.notify(f'Erreur: {e}', type='negative')
    
    # Chargement des données
    async def load_data():
        if not symbol_select.value:
            ui.notify('Veuillez sélectionner un symbole', type='warning')
            return
        
        status_label.text = 'Chargement en cours...'
        load_btn.disable()
        
        try:
            response = requests.post(
                f'{BACKEND_URL}/api/crypto/load',
                params={
                    'symbol': symbol_select.value,
                    'start_date': start_date.value,
                    'end_date': end_date.value
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                status_label.text = f"✓ {result['records_loaded']} enregistrements chargés"
                ui.notify('Données chargées avec succès !', type='positive')
            else:
                status_label.text = f"Erreur: {response.text}"
                ui.notify('Erreur lors du chargement', type='negative')
        except Exception as e:
            status_label.text = f"Erreur: {e}"
            ui.notify(f'Erreur: {e}', type='negative')
        finally:
            load_btn.enable()
    
    # Affichage des données
    async def show_data():
        if not symbol_select.value:
            ui.notify('Veuillez sélectionner un symbole', type='warning')
            return
        
        try:
            response = requests.get(
                f'{BACKEND_URL}/api/crypto/data/{symbol_select.value}',
                params={
                    'start_date': start_date.value,
                    'end_date': end_date.value,
                    'limit': 1000
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    chart_container.clear()
                    with chart_container:
                        fig = trading_app.create_chart(data, symbol_select.value)
                        ui.plotly(fig).classes('w-full')
                    ui.notify(f'{len(data)} points de données affichés', type='positive')
                else:
                    ui.notify('Aucune donnée disponible', type='warning')
            else:
                ui.notify('Erreur lors de la récupération', type='negative')
        except Exception as e:
            ui.notify(f'Erreur: {e}', type='negative')
    
    load_btn.on_click(load_data)
    show_btn.on_click(show_data)
    
    # Chargement initial des symboles
    app.on_startup(load_crypto_symbols)


def create_stocks_panel():
    """Panel pour les actions françaises"""
    ui.label('Chargement de données Bourse Française').classes('text-xl font-bold mb-4')
    
    with ui.card().classes('w-full p-4'):
        with ui.row().classes('w-full gap-4'):
            # Sélection du symbole
            symbol_select = ui.select(
                label='Symbole',
                options=[],
                value=None
            ).classes('w-64')
            
            # Dates
            start_date = ui.input(
                label='Date de début',
                value=(datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            ).classes('w-48')
            
            end_date = ui.input(
                label='Date de fin',
                value=datetime.now().strftime('%Y-%m-%d')
            ).classes('w-48')
        
        # Boutons d'action
        with ui.row().classes('gap-2 mt-4'):
            load_btn = ui.button('Charger les données', icon='download')
            show_btn = ui.button('Afficher les données', icon='visibility')
        
        status_label = ui.label('').classes('mt-2')
        
        # Zone de graphique
        chart_container = ui.column().classes('w-full mt-4')
    
    # Chargement des symboles disponibles
    async def load_stock_symbols():
        try:
            response = requests.get(f'{BACKEND_URL}/api/stocks/symbols')
            if response.status_code == 200:
                symbols = response.json()
                symbol_select.options = symbols
                if symbols:
                    symbol_select.value = symbols[0]
        except Exception as e:
            ui.notify(f'Erreur: {e}', type='negative')
    
    # Chargement des données
    async def load_data():
        if not symbol_select.value:
            ui.notify('Veuillez sélectionner un symbole', type='warning')
            return
        
        status_label.text = 'Chargement en cours...'
        load_btn.disable()
        
        try:
            response = requests.post(
                f'{BACKEND_URL}/api/stocks/load',
                params={
                    'symbol': symbol_select.value,
                    'start_date': start_date.value,
                    'end_date': end_date.value
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                status_label.text = f"✓ {result['records_loaded']} enregistrements chargés"
                ui.notify('Données chargées avec succès !', type='positive')
            else:
                status_label.text = f"Erreur: {response.text}"
                ui.notify('Erreur lors du chargement', type='negative')
        except Exception as e:
            status_label.text = f"Erreur: {e}"
            ui.notify(f'Erreur: {e}', type='negative')
        finally:
            load_btn.enable()
    
    # Affichage des données
    async def show_data():
        if not symbol_select.value:
            ui.notify('Veuillez sélectionner un symbole', type='warning')
            return
        
        try:
            response = requests.get(
                f'{BACKEND_URL}/api/stocks/data/{symbol_select.value}',
                params={
                    'start_date': start_date.value,
                    'end_date': end_date.value,
                    'limit': 1000
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    chart_container.clear()
                    with chart_container:
                        fig = trading_app.create_chart(data, symbol_select.value)
                        ui.plotly(fig).classes('w-full')
                    ui.notify(f'{len(data)} points de données affichés', type='positive')
                else:
                    ui.notify('Aucune donnée disponible', type='warning')
            else:
                ui.notify('Erreur lors de la récupération', type='negative')
        except Exception as e:
            ui.notify(f'Erreur: {e}', type='negative')
    
    load_btn.on_click(load_data)
    show_btn.on_click(show_data)
    
    # Chargement initial des symboles
    app.on_startup(load_stock_symbols)


def create_stats_panel():
    """Panel pour les statistiques"""
    ui.label('Statistiques de la base de données').classes('text-xl font-bold mb-4')
    
    stats_container = ui.column().classes('w-full')
    
    async def load_stats():
        try:
            response = requests.get(f'{BACKEND_URL}/api/stats')
            if response.status_code == 200:
                stats = response.json()
                
                stats_container.clear()
                with stats_container:
                    with ui.row().classes('w-full gap-4'):
                        # Stats Crypto
                        with ui.card().classes('p-4'):
                            ui.label('Crypto-monnaies').classes('text-lg font-bold')
                            ui.label(f"Symboles: {stats['crypto']['symbols_count']}").classes('text-sm')
                            ui.label(f"Enregistrements: {stats['crypto']['total_records']:,}").classes('text-sm')
                        
                        # Stats Actions
                        with ui.card().classes('p-4'):
                            ui.label('Actions françaises').classes('text-lg font-bold')
                            ui.label(f"Symboles: {stats['stocks']['symbols_count']}").classes('text-sm')
                            ui.label(f"Enregistrements: {stats['stocks']['total_records']:,}").classes('text-sm')
        except Exception as e:
            ui.notify(f'Erreur: {e}', type='negative')
    
    ui.button('Actualiser', icon='refresh', on_click=load_stats).classes('mb-4')
    
    # Chargement initial
    app.on_startup(load_stats)


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        host='0.0.0.0',
        port=8080,
        title='Trading IA',
        reload=True,
        show=False
    )
