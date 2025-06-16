
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt

# Fonction pour calculer les indicateurs techniques
def calculate_indicators(df):
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    df['SMA50'] = df['Close'].rolling(window=50).mean()
    df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()

    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

    return df

# Fonction pour générer les signaux de trading
def generate_signals(df):
    latest = df.iloc[-1]
    signals = {}

    if latest['MACD'] > latest['Signal'] and latest['RSI'] < 70 and latest['SMA20'] > latest['SMA50']:
        signals['Tendance'] = 'Achat'
    elif latest['MACD'] < latest['Signal'] and latest['RSI'] > 30 and latest['SMA20'] < latest['SMA50']:
        signals['Tendance'] = 'Vente'
    else:
        signals['Tendance'] = 'Neutre'

    entry_price = latest['Close']
    if signals['Tendance'] == 'Achat':
        signals['Prix d'entrée'] = round(entry_price, 2)
        signals['Stop Loss'] = round(entry_price * 0.97, 2)
        signals['Take Profit'] = round(entry_price * 1.05, 2)
        signals['Prix de sortie estimé'] = round(entry_price * 1.03, 2)
    elif signals['Tendance'] == 'Vente':
        signals['Prix d'entrée'] = round(entry_price, 2)
        signals['Stop Loss'] = round(entry_price * 1.03, 2)
        signals['Take Profit'] = round(entry_price * 0.95, 2)
        signals['Prix de sortie estimé'] = round(entry_price * 0.97, 2)

    return signals

# Interface utilisateur Streamlit
st.title("🤖 Bot de Trading Crypto IA")
st.markdown("Ce bot analyse la tendance d'une crypto et propose des niveaux d'entrée, stop loss et take profit.")

symbol = st.text_input("Entrez le symbole de la crypto (ex: BTC-USD)", value="BTC-USD")
period = st.selectbox("Période d'analyse", ["7d", "1mo", "3mo", "6mo", "1y"], index=1)

if st.button("Analyser"):
    with st.spinner("Analyse en cours..."):
        df = yf.download(symbol, period=period, interval="1h")
        if df.empty:
            st.error("Aucune donnée trouvée pour ce symbole.")
        else:
            df = calculate_indicators(df)
            signals = generate_signals(df)

            st.subheader("📈 Résultats de l'analyse")
            for key, value in signals.items():
                st.write(f"**{key}** : {value}")

            st.subheader("📊 Graphique des prix et indicateurs")
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(df['Close'], label='Prix')
            ax.plot(df['SMA20'], label='SMA20')
            ax.plot(df['SMA50'], label='SMA50')
            ax.plot(df['EMA20'], label='EMA20')
            ax.set_title(f"{symbol} - Prix et indicateurs")
            ax.legend()
            st.pyplot(fig)
