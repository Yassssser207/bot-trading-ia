
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Bot Trading IA", layout="wide")

st.title("🤖 Bot IA de Trading Crypto")
st.markdown("Ce bot analyse la tendance d'une crypto et propose un prix d'entrée, un stop loss, un take profit, etc.")

symbol = st.text_input("Entrez le symbole de la crypto (ex: BTC-USD)", value="BTC-USD")
data = yf.download(symbol, period="3mo", interval="1d")

if not data.empty:
    data['SMA20'] = data['Close'].rolling(window=20).mean()
    data['SMA50'] = data['Close'].rolling(window=50).mean()
    data['EMA20'] = data['Close'].ewm(span=20, adjust=False).mean()

    delta = data['Close'].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window=14).mean()
    avg_loss = pd.Series(loss).rolling(window=14).mean()
    rs = avg_gain / avg_loss
    data['RSI'] = 100 - (100 / (1 + rs))

    exp1 = data['Close'].ewm(span=12, adjust=False).mean()
    exp2 = data['Close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = exp1 - exp2
    data['Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()

    latest = data.iloc[-1]
    signals = {}

    if latest['MACD'] > latest['Signal'] and latest['RSI'] < 70 and latest['SMA20'] > latest['SMA50']:
        signals['Tendance'] = 'Achat 📈'
        entry_price = latest['Close']
        signals["Prix d'entrée"] = round(entry_price, 2)
        signals['Stop Loss'] = round(entry_price * 0.97, 2)
        signals['Take Profit'] = round(entry_price * 1.05, 2)
        signals['Prix de sortie estimé'] = round(entry_price * 1.04, 2)
    elif latest['MACD'] < latest['Signal'] and latest['RSI'] > 30 and latest['SMA20'] < latest['SMA50']:
        signals['Tendance'] = 'Vente 📉'
        entry_price = latest['Close']
        signals["Prix d'entrée"] = round(entry_price, 2)
        signals['Stop Loss'] = round(entry_price * 1.03, 2)
        signals['Take Profit'] = round(entry_price * 0.95, 2)
        signals['Prix de sortie estimé'] = round(entry_price * 0.96, 2)
    else:
        signals['Tendance'] = "Indécise 🤔"

    st.subheader("📊 Résultats de l'analyse")
    for key, value in signals.items():
        st.write(f"**{key}** : {value}")

    st.subheader("📈 Graphique des prix")
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(data['Close'], label='Prix')
    ax.plot(data['SMA20'], label='SMA20')
    ax.plot(data['SMA50'], label='SMA50')
    ax.plot(data['EMA20'], label='EMA20')
    ax.set_title(f"{symbol} - Prix et Moyennes Mobiles")
    ax.legend()
    st.pyplot(fig)
else:
    st.error("Impossible de récupérer les données pour ce symbole.")
