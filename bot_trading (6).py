import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

st.title("🤖 Bot IA de Trading Crypto")

# Saisie de l'utilisateur
symbol = st.text_input("Entrez le symbole de la crypto (ex: BTC-USD)", value="BTC-USD")

# Télécharger les données
@st.cache_data
def load_data(symbol):
    try:
        df = yf.download(symbol, period="3mo", interval="1d")
        return df
    except Exception as e:
        return pd.DataFrame()

df = load_data(symbol)

if df.empty:
    st.error("Impossible de charger les données. Vérifiez le symbole ou réessayez plus tard.")
else:
    # Calcul des indicateurs
    df["SMA20"] = df["Close"].rolling(window=20).mean()
    df["SMA50"] = df["Close"].rolling(window=50).mean()
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()

    # RSI
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    # MACD
    exp1 = df["Close"].ewm(span=12, adjust=False).mean()
    exp2 = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = exp1 - exp2
    df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()

    # Génération des signaux
    def generate_signals(df):
        signals = {}
        latest = df.iloc[-1]

        try:
            macd = float(latest["MACD"])
            signal = float(latest["Signal"])
            rsi = float(latest["RSI"])
            sma20 = float(latest["SMA20"])
            sma50 = float(latest["SMA50"])
            close = float(latest["Close"])

            if macd > signal and rsi < 70 and sma20 > sma50:
                signals["Tendance"] = "📈 Achat"
                signals["Prix d'entrée"] = round(close, 2)
                signals["Stop Loss"] = round(close * 0.97, 2)
                signals["Take Profit"] = round(close * 1.05, 2)
                signals["Prix de sortie estimé"] = round(close * 1.04, 2)
            elif macd < signal and rsi > 30 and sma20 < sma50:
                signals["Tendance"] = "📉 Vente"
                signals["Prix d'entrée"] = round(close, 2)
                signals["Stop Loss"] = round(close * 1.03, 2)
                signals["Take Profit"] = round(close * 0.95, 2)
                signals["Prix de sortie estimé"] = round(close * 0.96, 2)
            else:
                signals["Tendance"] = "⏸️ Aucune tendance claire"
        except Exception as e:
            signals["Erreur"] = f"Impossible de générer les signaux : {e}"

        return signals

    signals = generate_signals(df)

    # Affichage des signaux
    st.subheader("📊 Signaux de Trading")
    for key, value in signals.items():
        st.write(f"**{key}** : {value}")

    # Affichage du graphique
    st.subheader("📈 Graphique des prix")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df["Close"], label="Prix de clôture")
    ax.plot(df["SMA20"], label="SMA20")
    ax.plot(df["SMA50"], label="SMA50")
    ax.set_title(f"Prix de {symbol}")
    ax.legend()
    st.pyplot(fig)
