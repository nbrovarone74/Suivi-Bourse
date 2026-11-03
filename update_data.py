"""Récupère les données du CAC 40 (+ vos titres perso) et écrit data.json."""
import json, datetime, yfinance as yf

CAC40 = ["AI.PA","AIR.PA","ALO.PA","MT.AS","CS.PA","BNP.PA","EN.PA","CAP.PA","CA.PA","ACA.PA",
         "BN.PA","DSY.PA","EDEN.PA","ENGI.PA","EL.PA","ERF.PA","RMS.PA","KER.PA","OR.PA","LR.PA",
         "MC.PA","ML.PA","ORA.PA","RI.PA","PUB.PA","RNO.PA","SAF.PA","SGO.PA","SAN.PA","SU.PA",
         "GLE.PA","STLAP.PA","STMPA.PA","TEP.PA","HO.PA","TTE.PA","URW.AS","VIE.PA","DG.PA","BVI.PA"]

# Ajoutez ici vos autres titres (ex. "AAPL", "MSFT")
EXTRA = []

def get(t):
    try:
        i = yf.Ticker(t).info
        return {
            "ticker": t,
            "nom": i.get("shortName") or t,
            "secteur": i.get("sector") or "Autre",
            "devise": i.get("currency") or "EUR",
            "cours": i.get("currentPrice") or i.get("regularMarketPrice"),
            "var": i.get("regularMarketChangePercent"),
            "per": i.get("trailingPE"),
            "ca": i.get("totalRevenue"),
            "resultat": i.get("netIncomeToCommon"),
            "cac40": t in CAC40,
        }
    except Exception as e:
        print("Erreur", t, e)
        return None

rows = [r for r in (get(t) for t in CAC40 + EXTRA) if r]
out = {"maj": datetime.datetime.utcnow().isoformat() + "Z", "actions": rows}
json.dump(out, open("data.json", "w"), ensure_ascii=False, indent=1)
print(len(rows), "titres écrits")
