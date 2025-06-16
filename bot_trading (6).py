
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.title("📈 Bot IA de Trading Crypto")

# Sélection de l'actif
symbol = st.text_input("Entrez le symbole de la crypto (ex: BTC-USD)", value="BTC-USD")

# Sélection de la durée d'analyse
duree_options = {
    "1 jour": ("1d", "5m"),
    "1 semaine": ("7d", "30m"),
    "1 mois": ("1mo", "1h")
}
duree_choisie = st.selectbox("Choisissez la durée d'analyse", list(duree_options.keys()))
period, interval = duree_options[duree_choisie]

# Télécharger les données
@st.cache_data
def get_data(symbol, period, interval):
    try:
        df = yf.download(symbol, period=period, interval=interval)
        return df
    except Exception as e:
        st.error(f"Erreur lors du téléchargement des données : {e}")
        return pd.DataFrame()

df = get_data(symbol, period, interval)

if df.empty:
    st.warning("Aucune donnée disponible. Vérifiez le symbole ou la connexion.")
    st.stop()

# Calcul des indicateurs
df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
df["SMA20"] = df["Close"].rolling(window=20).mean()
df["SMA50"] = df["Close"].rolling(window=50).mean()

# RSI
delta = df["Close"].diff()
gain = delta.where(delta > 0, 0)
loss = -delta.where(delta < 0, 0)
avg_gain = gain.rolling(window=14).mean()
avg_loss = loss.rolling(window=14).mean()
rs = avg_gain / avg_loss
df["RSI"] = 100 - (100 / (1 + rs))

# MACD
ema12 = df["Close"].ewm(span=12, adjust=False).mean()
ema26 = df["Close"].ewm(span=26, adjust=False).mean()
df["MACD"] = ema12 - ema26
df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()

# Génération des signaux
def generate_signals(df):
    latest = df.iloc[-1]
    signals = {}

    if float(latest["MACD"]) > float(latest["Signal"]) and float(latest["RSI"]) < 70 and float(latest["SMA20"]) > float(latest["SMA50"]):
        signals["Tendance"] = "📈 Achat"
        entry_price = latest["Close"]
        signals["Prix d'entrée"] = round(entry_price, 2)
        signals["Stop Loss"] = round(entry_price * 0.97, 2)
        signals["Take Profit"] = round(entry_price * 1.05, 2)
        signals["Prix de sortie estimé"] = round(entry_price * 1.03, 2)
    elif float(latest["MACD"]) < float(latest["Signal"]) and float(latest["RSI"]) > 30 and float(latest["SMA20"]) < float(latest["SMA50"]):
        signals["Tendance"] = "📉 Vente"
        entry_price = latest["Close"]
        signals["Prix d'entrée"] = round(entry_price, 2)
        signals["Stop Loss"] = round(entry_price * 1.03, 2)
        signals["Take Profit"] = round(entry_price * 0.95, 2)
        signals["Prix de sortie estimé"] = round(entry_price * 0.97, 2)
    else:
        signals["Tendance"] = "⏸️ Neutre"
    return signals

signals = generate_signals(df)

# Affichage des signaux
st.subheader("🔍 Signaux de Trading")
for key, value in signals.items():
    st.write(f"**{key}** : {value}")

# Graphique en chandeliers avec Plotly
st.subheader("📊 Graphique des prix (bougies)")

fig = go.Figure(data=[
    go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name="Prix"
    ),
    go.Scatter(x=df.index, y=df["EMA20"], line=dict(color='blue', width=1), name="EMA20"),
    go.Scatter(x=df.index, y=df["SMA20"], line=dict(color='orange', width=1), name="SMA20"),
    go.Scatter(x=df.index, y=df["SMA50"], line=dict(color='green', width=1), name="SMA50")
])

fig.update_layout(xaxis_rangeslider_visible=False, height=500)
st.plotly_chart(fig, use_container_width=True)
