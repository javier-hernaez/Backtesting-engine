import yfinance as yf
import pandas as pd

print("Descargando datos históricos de AAPL...")
df = yf.download('AAPL', start='2022-01-01', end='2026-01-01', progress=False)

# En yfinance actual a veces devuelve MultiIndex si se pasa una lista, o normal
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.droplevel(1)
    
df.columns = [str(col).lower() for col in df.columns]

# En algunos entornos yfinance no trae 'adj close' sino 'adj_close'
if 'adj close' in df.columns:
    df.rename(columns={'adj close': 'adj_close'}, inplace=True)

df.to_csv('data/AAPL.csv')
print("¡Archivo data/AAPL.csv descargado y reemplazado con éxito con 4 años de historia!")
