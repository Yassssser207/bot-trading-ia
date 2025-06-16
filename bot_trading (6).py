
# Correction: We will remove the mplfinance import and use matplotlib with candlestick_ohlc from mplfinance.original_flavor
# This avoids the ModuleNotFoundError on Streamlit Cloud if mplfinance is not installed

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mplfinance.original_flavor import candlestick_ohlc

# Titre de l'application
st.title("📈 Bot IA de Trading Crypto")

# Saisie de l'utilisateur
symbol = st.text_input("Entrez le symbole de la crypto (ex: BTC-USD)", value="BTC-USD")

# Choix de la durée d'analyse
duration_label = st.selectbox("Choisissez la durée d'analyse :", ["1 jour", "1 semaine", "1 mois"])
duration_map = {
    "1 jour": ("1d", "1h"),
    "1 semaine": ("7d", "1h"),
    "1 mois": ("30d", "1h")
}
period, interval = duration_map[duration_label]

# Télécharger les données
df = yf.download(symbol, period=period, interval=interval)

if df.empty:
    st.error("Impossible de récupérer les données. Vérifiez le symbole ou réessayez plus tard.")
else:
    # Calcul des indicateurs
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["SMA20"] = df["Close"].rolling(window=20).mean()
    df["SMA50"] = df["Close"].rolling(window=50).mean()

    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    exp1 = df["Close"].ewm(span=12, adjust=False).mean()
    exp2 = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = exp1 - exp2
    df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()

    # Génération des signaux
    def generate_signals(data):
        latest = data.iloc[-1]
        signals = {}

        try:
            if float(latest["MACD"]) > float(latest["Signal"]) and float(latest["RSI"]) < 70 and float(latest["SMA20"]) > float(latest["SMA50"]):
                signals["Tendance"] = "📈 Achat"
                entry_price = float(latest["Close"])
                signals["Prix d'entrée"] = round(entry_price, 2)
                signals["Stop Loss"] = round(entry_price * 0.97, 2)
                signals["Take Profit"] = round(entry_price * 1.05, 2)
                signals["Prix de sortie estimé"] = round(entry_price * 1.03, 2)
            elif float(latest["MACD"]) < float(latest["Signal"]) and float(latest["RSI"]) > 30 and float(latest["SMA20"]) < float(latest["SMA50"]):
                signals["Tendance"] = "📉 Vente"
                entry_price = float(latest["Close"])
                signals["Prix d'entrée"] = round(entry_price, 2)
                signals["Stop Loss"] = round(entry_price * 1.03, 2)
                signals["Take Profit"] = round(entry_price * 0.95, 2)
                signals["Prix de sortie estimé"] = round(entry_price * 0.97, 2)
            else:
                signals["Tendance"] = "🔍 Neutre"
        except Exception as e:
            signals["Erreur"] = str(e)

        return signals

    signals = generate_signals(df)

    # Affichage des signaux
    st.subheader("📊 Signaux de Trading")
    for key, value in signals.items():
        st.write(f"**{key}** : {value}")

    # Affichage du graphique en chandeliers
    st.subheader("📉 Graphique des prix (bougies)")

    df_plot = df[["Open", "High", "Low", "Close"]].copy()
    df_plot.reset_index(inplace=True)
    df_plot["Date"] = df_plot["Datetime"].map(mdates.date2num)

    ohlc = df_plot[["Date", "Open", "High", "Low", "Close"]]

    fig, ax = plt.subplots()
    candlestick_ohlc(ax, ohlc.values, width=0.01, colorup='green', colordown='red')
    ax.xaxis_date()
    ax.set_title(f"Graphique en chandeliers : {symbol}")
    ax.set_ylabel("Prix")
    plt.xticks(rotation=45)
    st.pyplot(fig)

