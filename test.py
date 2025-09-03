import yfinance as yf

msft = yf.Ticker("MSFT")
print(msft.history(period="5d"))
# tech_indicators.py
# Moving averages + RSI + MACD for one ticker, with saved charts & CSV.

from pathlib import Path
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# -------- Settings --------
