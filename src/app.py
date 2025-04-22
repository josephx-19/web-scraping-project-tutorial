import os
from bs4 import BeautifulSoup
import requests
import time
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd



import requests
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import date
from io import StringIO

def convertir_streams(valor):
    try:
        return float(valor) * 1e9  # vienen en billones
    except:
        return None

# Descargar HTML
url = "https://en.wikipedia.org/wiki/List_of_most-streamed_songs_on_Spotify"
response = requests.get(url)
html = response.text

# Leer tablas y seleccionar la correcta (tabla 0)
tablas = pd.read_html(StringIO(html))
df = tablas[0]

# Limpiar columnas
df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

# Renombrar columna de streams
df = df.rename(columns={'streams_(billions)': 'streams'})

# Convertir streams a número real
df['streams'] = df['streams'].apply(convertir_streams)
df = df.dropna(subset=['streams'])

# Extraer año
df['release_year'] = df['release_date'].astype(str).str.extract(r'(\d{4})')

# Guardar en SQLite
conn = sqlite3.connect("spotify.db")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS daily_rankings (
    scraping_date TEXT,
    rank INTEGER,
    song TEXT,
    artist TEXT,
    streams REAL,
    release_year TEXT
)
''')

for i, row in df.iterrows():
    cursor.execute('''
        INSERT INTO daily_rankings (scraping_date, rank, song, artist, streams, release_year)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        date.today().isoformat(),
        row['rank'],
        row['song'],
        row['artist(s)'],
        row['streams'],
        row['release_year']
    ))

conn.commit()

# Visualización
df_sql = pd.read_sql_query("SELECT * FROM daily_rankings", conn)
conn.close()

plt.figure(figsize=(12, 6))
sns.countplot(y='song', data=df_sql, order=df_sql['song'].value_counts().index[:10])
plt.title("Canciones más frecuentes en el ranking", fontsize=16)
plt.xlabel("Frecuencia")
plt.ylabel("Canción")
plt.tight_layout()
plt.show()


