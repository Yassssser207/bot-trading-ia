
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Bot Trading IA", layout="wide")

st.title("🤖 Bot de Trading IA - Crypto")

symbol = st.text_input("Entrez le symbole de la crypto (ex: BTC-USD)", "BTC-USD")

@st.cache_data
def load_data(symbol):
    data = yf.download(symbol, period="3mo", interval="1d")
    data.dropna(inplace=True)
    return data

def calculate_indicators(df):
    df["SMA20"] = df["Close"].rolling(window=20).mean()
    df["SMA50"] = df["Close"].rolling(window=50).mean()
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()

    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()

    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    df["MACD"] = df["Close"].ewm(span=12, adjust=False).mean() - df["Close"].ewm(span=26, adjust=False).mean()
    df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()

    return df

def generate_signals(df):
    signals = {}
    latest = df.iloc[-1]

    if latest["MACD"] > latest["Signal"] and latest["RSI"] < 70 and latest["SMA20"] > latest["SMA50"]:
        signals["Tendance"] = "📈 Achat"
        entry_price = latest["Close"]
        signals["Prix d'entrée"] = round(entry_price, 2)
        signals["Stop Loss"] = round(entry_price * 0.97, 2)
        signals["Take Profit"] = round(entry_price * 1.05, 2)
        signals["Prix de sortie estimé"] = round(entry_price * 1.03, 2)
    elif latest["MACD"] < latest["Signal"] and latest["RSI"] > 30 and latest["SMA20"] < latest["SMA50"]:
        signals["Tendance"] = "📉 Vente"
        entry_price = latest["Close"]
        signals["Prix d'entrée"] = round(entry_price, 2)
        signals["Stop Loss"] = round(entry_price * 1.03, 2)
        signals["Take Profit"] = round(entry_price * 0.95, 2)
        signals["Prix de sortie estimé"] = round(entry_price * 0.97, 2)
    else:
        signals["Tendance"] = "⏸️ Attente"
        signals["Message"] = "Pas de signal clair pour le moment."

    return signals

def plot_chart(df):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df["Close"], label="Prix de clôture")
    ax.plot(df["SMA20"], label="SMA20")
    ax.plot(df["SMA50"], label="SMA50")
    ax.plot(df["EMA20"], label="EMA20")
    ax.set_title("Graphique des prix et indicateurs")
    ax.legend()
    st.pyplot(fig)

if symbol:
    df = load_data(symbol)
    df = calculate_indicators(df)
    signals = generate_signals(df)

    st.subheader("📊 Analyse Technique")
    plot_chart(df)

    st.subheader("📌 Recommandation")
    for key, value in signals.items():
        st.write(f"**{key}** : {value}")
