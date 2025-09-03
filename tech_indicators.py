# tech_indicators.py
# Moving averages + RSI + MACD for one ticker, with saved charts & CSV.

from pathlib import Path
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# -------- Settings --------
TICKER = "AAPL"      # change to MSFT, TSLA, etc.
PERIOD = "2y"        # or "1y", "5y", etc.
INTERVAL = "1d"      # daily bars
DATA_DIR = Path("data")
CHART_DIR = Path("charts")
DATA_DIR.mkdir(exist_ok=True)
CHART_DIR.mkdir(exist_ok=True)

# -------- Download --------
df = yf.download(TICKER, period=PERIOD, interval=INTERVAL, auto_adjust=True)
if df.empty:
    raise SystemExit("No data returned. Check ticker/period/interval.")
df = df.dropna()

# -------- Indicators --------
# Simple Moving Averages
df["SMA20"]  = df["Close"].rolling(window=20).mean()
df["SMA50"]  = df["Close"].rolling(window=50).mean()
df["SMA200"] = df["Close"].rolling(window=200).mean()

# Exponential Moving Averages (used in MACD)
df["EMA12"] = df["Close"].ewm(span=12, adjust=False).mean()
df["EMA26"] = df["Close"].ewm(span=26, adjust=False).mean()

# MACD (12/26 EMA) and signal (9 EMA of MACD)
df["MACD"] = df["EMA12"] - df["EMA26"]
df["MACD_signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
df["MACD_hist"] = df["MACD"] - df["MACD_signal"]

# RSI (14) using Wilder's smoothing
delta = df["Close"].diff()
up = delta.clip(lower=0)
down = -delta.clip(upper=0)
roll_up = up.ewm(alpha=1/14, adjust=False).mean()
roll_down = down.ewm(alpha=1/14, adjust=False).mean()
rs = roll_up / roll_down
df["RSI14"] = 100 - (100 / (1 + rs))

# -------- Signals (optional but impressive) --------
# Golden Cross: SMA50 crosses above SMA200
df["golden_cross"] = (df["SMA50"] > df["SMA200"]) & (df["SMA50"].shift(1) <= df["SMA200"].shift(1))
# Death Cross: SMA50 crosses below SMA200
df["death_cross"] = (df["SMA50"] < df["SMA200"]) & (df["SMA50"].shift(1) >= df["SMA200"].shift(1))

print(f"\nFirst 5 rows with indicators for {TICKER}:")
print(df[["Close","SMA20","SMA50","SMA200","RSI14","MACD","MACD_signal"]].head())

# Show any recent crosses
gc_dates = list(df.index[df["golden_cross"]])
dc_dates = list(df.index[df["death_cross"]])
if gc_dates:
    print(f"\nGolden Cross dates: {', '.join(d.strftime('%Y-%m-%d') for d in gc_dates[-3:])}")
else:
    print("\nGolden Cross dates: none in range")
if dc_dates:
    print(f"Death Cross dates: {', '.join(d.strftime('%Y-%m-%d') for d in dc_dates[-3:])}")
else:
    print("Death Cross dates: none in range")

# -------- Save CSV --------
csv_path = DATA_DIR / f"{TICKER}_indicators.csv"
df.to_csv(csv_path)
print(f"\nSaved data with indicators → {csv_path}")

# -------- Charts (saved as PNGs) --------
# 1) Price with SMA overlays
plt.figure(figsize=(11,6))
plt.plot(df.index, df["Close"], label="Close")
plt.plot(df.index, df["SMA20"], label="SMA20")
plt.plot(df.index, df["SMA50"], label="SMA50")
plt.plot(df.index, df["SMA200"], label="SMA200")
plt.title(f"{TICKER} Price with SMAs")
plt.xlabel("Date"); plt.ylabel("Price")
plt.legend()
price_chart_path = CHART_DIR / f"{TICKER}_price_smas.png"
plt.tight_layout(); plt.savefig(price_chart_path); plt.close()
print(f"Saved chart → {price_chart_path}")

# 2) MACD
plt.figure(figsize=(11,4))
plt.plot(df.index, df["MACD"], label="MACD")
plt.plot(df.index, df["MACD_signal"], label="Signal")
plt.bar(df.index, df["MACD_hist"], label="Hist")
plt.title(f"{TICKER} MACD")
plt.xlabel("Date"); plt.ylabel("Value")
plt.legend()
macd_chart_path = CHART_DIR / f"{TICKER}_macd.png"
plt.tight_layout(); plt.savefig(macd_chart_path); plt.close()
print(f"Saved chart → {macd_chart_path}")

# 3) RSI
plt.figure(figsize=(11,3.8))
plt.plot(df.index, df["RSI14"], label="RSI14")
plt.axhline(70, linestyle="--")
plt.axhline(30, linestyle="--")
plt.title(f"{TICKER} RSI (14)")
plt.xlabel("Date"); plt.ylabel("RSI")
plt.legend()
rsi_chart_path = CHART_DIR / f"{TICKER}_rsi.png"
plt.tight_layout(); plt.savefig(rsi_chart_path); plt.close()
print(f"Saved chart → {rsi_chart_path}")

print("\nDone. Open the PNGs in the 'charts/' folder and the CSV in 'data/'.")
