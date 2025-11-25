import pandas as pd
import os

# Carpeta donde están tus CSV
DATA_DIR = "data"

# Archivos a combinar
files = [
    "netflix_titles.csv",
    "amazon_prime_titles.csv",
    "hulu_titles.csv",
    "disney_plus_titles.csv"
]

# Lista para guardar los DataFrames
dataframes = []

for f in files:
    path = os.path.join(DATA_DIR, f)
    if os.path.exists(path):
        df = pd.read_csv(path)
        df["platform"] = f.split("_")[0].capitalize()
        dataframes.append(df)
    else:
        print(f" No se encontró: {path}")

# Combinar todos los DataFrames
merged = pd.concat(dataframes, ignore_index=True)

# Normalizar nombres de columnas
merged.columns = [c.lower().strip() for c in merged.columns]

# Columnas que queremos mantener (solo las que existen)
keep_cols = ["title", "description", "cast", "director", "country",
             "release_year", "duration", "listed_in", "platform"]

existing_cols = [c for c in keep_cols if c in merged.columns]
merged = merged[existing_cols]

# Renombrar listed_in -> genre
if "listed_in" in merged.columns:
    merged.rename(columns={"listed_in": "genre"}, inplace=True)

# Limpiar datos vacíos
merged.dropna(subset=["title", "description"], inplace=True)
merged.drop_duplicates(subset=["title", "platform"], inplace=True)

# Crear carpeta clean si no existe
os.makedirs("data/clean", exist_ok=True)

# Guardar CSV limpio
merged.to_csv("data/clean/tv_shows_complete.csv", index=False)

print(f"✅ Dataset combinado y limpio guardado en data/clean/tv_shows_complete.csv")
print(f"Total de registros: {len(merged)}")
