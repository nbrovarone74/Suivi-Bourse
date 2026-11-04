"""Récupère CAC 40 (+ vos titres) : cours, ratios, dividendes, calendrier -> data.json."""
import json, time, datetime, yfinance as yf, pandas as pd

CAC40 = ["AI.PA","AIR.PA","ALO.PA","MT.AS","CS.PA","BNP.PA","EN.PA","CAP.PA","CA.PA","ACA.PA",
         "BN.PA","DSY.PA","EDEN.PA","ENGI.PA","EL.PA","ERF.PA","RMS.PA","KER.PA","OR.PA","LR.PA",
         "MC.PA","ML.PA","ORA.PA","RI.PA","PUB.PA","RNO.PA","SAF.PA","SGO.PA","SAN.PA","SU.PA",
         "GLE.PA","STLAP.PA","STMPA.PA","TEP.PA","HO.PA","TTE.PA","URW.AS","VIE.PA","DG.PA","BVI.PA"]

# Ajoutez ici vos autres titres (ex. "AAPL", "MSFT")
EXTRA = []

TODAY = datetime.date.today().isoformat()
try:
    OLD = {a["ticker"]: a for a in json.load(open("data.json"))["actions"]}
except Exception:
    OLD = {}

def val(df, name, col):
    try:
        v = float(df.loc[name, col])
        return None if v != v else v
    except Exception:
        return None

def slow(t):
    """Données lentes (dividendes, calendrier, ratios) : 1 fois par jour."""
    tk = yf.Ticker(t)
    out = {"divs": {}, "events": {}, "ratios": []}
    try:
        d = tk.dividends
        if len(d):
            y = d.groupby(d.index.year).sum()
            lim = datetime.date.today().year - 10
            out["divs"] = {int(k): round(float(v), 4) for k, v in y.items() if k >= lim}
    except Exception as e:
        print("dividendes", t, e)
    try:
        cal = tk.calendar or {}
        e = cal.get("Earnings Date")
        if e: out["events"]["resultats"] = str(e[0])
        x = cal.get("Ex-Dividend Date")
        if x: out["events"]["detachement"] = str(x)
    except Exception as e:
        print("calendrier", t, e)
    try:
        inc, bal, cf = tk.income_stmt, tk.balance_sheet, tk.cashflow
        h = tk.history(period="6y", auto_adjust=False)["Close"]
        h.index = h.index.tz_localize(None)
        for col in inc.columns:
            dt = pd.Timestamp(col)
            hh = h[:dt]
            if hh.empty: continue
            px = float(hh.iloc[-1])
            sh = val(bal, "Ordinary Shares Number", col) or val(bal, "Share Issued", col)
            if not sh: continue
            mc = px * sh
            eps = val(inc, "Diluted EPS", col)
            rev = val(inc, "Total Revenue", col)
            ebitda = val(inc, "EBITDA", col)
            fcf = val(cf, "Free Cash Flow", col)
            eq = val(bal, "Stockholders Equity", col)
            debt = val(bal, "Total Debt", col) or 0
            cash = val(bal, "Cash And Cash Equivalents", col) or 0
            r = lambda v: round(v, 1) if v is not None else None
            out["ratios"].append({
                "annee": dt.year,
                "pe": r(px / eps) if eps and eps > 0 else None,
                "ps": r(mc / rev) if rev and rev > 0 else None,
                "pfcf": r(mc / fcf) if fcf and fcf > 0 else None,
                "pb": r(mc / eq) if eq and eq > 0 else None,
                "evebitda": r((mc + debt - cash) / ebitda) if ebitda and ebitda > 0 else None,
            })
        out["ratios"].sort(key=lambda z: z["annee"])
    except Exception as e:
        print("ratios", t, e)
    return out

def get(t):
    try:
        i = yf.Ticker(t).info
        row = {
            "ticker": t,
            "nom": i.get("shortName") or t,
            "secteur": i.get("sector") or "Autre",
            "devise": i.get("currency") or "EUR",
            "cours": i.get("currentPrice") or i.get("regularMarketPrice"),
            "var": i.get("regularMarketChangePercent"),
            "per": i.get("trailingPE"),
            "ca": i.get("totalRevenue"),
            "resultat": i.get("netIncomeToCommon"),
            "div_rate": i.get("dividendRate"),
            "payout": i.get("payoutRatio"),
            "cac40": t in CAC40,
        }
        o = OLD.get(t, {})
        if o.get("slow_maj") == TODAY:
            for k in ("divs", "events", "ratios"): row[k] = o.get(k)
        else:
            row.update(slow(t))
        row["slow_maj"] = TODAY
        return row
    except Exception as e:
        print("Erreur", t, e)
        return OLD.get(t)

rows = []
for t in CAC40 + EXTRA:
    r = get(t)
    if r: rows.append(r)
    time.sleep(0.3)
out = {"maj": datetime.datetime.utcnow().isoformat() + "Z", "actions": rows}
json.dump(out, open("data.json", "w"), ensure_ascii=False, indent=1)
print(len(rows), "titres écrits")
