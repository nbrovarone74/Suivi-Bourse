"""Historique des cours (5 ans) -> historique.json"""
import json, yfinance as yf

tickers = [a["ticker"] for a in json.load(open("data.json"))["actions"]]
df = yf.download(tickers, period="5y", auto_adjust=False, progress=False)["Close"].ffill()
df.index = df.index.tz_localize(None)
out = {
    "dates": [d.strftime("%Y-%m-%d") for d in df.index],
    "px": {t: [None if v != v else round(float(v), 2) for v in df[t]] for t in tickers if t in df.columns},
}
json.dump(out, open("historique.json", "w"), separators=(",", ":"))
print(len(tickers), "titres,", len(df), "jours")
