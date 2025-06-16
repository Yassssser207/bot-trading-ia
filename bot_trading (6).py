
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf

# Titre de l'application
st.title("📈 Bot IA de Trading Crypto")

# Saisie de l'utilisateur
symbol = st.text_input("Entrez le symbole de la crypto (ex: BTC-USD)", "BTC-USD")

# Choix de la périodicité
interval = st.selectbox("Choisissez la périodicité des données", ["1d", "1h", "1wk"])

# Choix de la durée
duration_label = st.selectbox("Choisissez la durée d'analyse", ["1 jour", "1 semaine", "1 mois"])
duration_map = {
    "1 jour": "1d",
    "1 semaine": "7d",
    "1 mois": "30d"
}
period = duration_map[duration_label]

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
    latest = df.iloc[-1]
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
            signals["Tendance"] = "⏸️ Neutre"
    except Exception as e:
        st.warning(f"Erreur lors de l'analyse des signaux : {e}")

    # Affichage des signaux
    st.subheader("📊 Signaux de Trading")
    for key, value in signals.items():
        st.write(f"**{key}** : {value}")

    # Affichage du graphique en chandeliers
    st.subheader("🕯️ Graphique des prix (bougies)")
    df_plot = df.copy()
    df_plot.index.name = 'Date'
    df_plot = df_plot[["Open", "High", "Low", "Close", "Volume"]]

    fig, ax = mpf.plot(df_plot, type='candle', style='charles', volume=True, returnfig=True)
    st.pyplot(fig)

