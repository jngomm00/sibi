import pandas as pd
import os

# Ruta al CSV combinado
input_csv = "data/clean/tv_shows_complete.csv"

# Cargar CSV
df = pd.read_csv(input_csv)

# Detectar columnas sin valores vacíos
complete_cols = [col for col in df.columns if df[col].notna().all()]

# Crear nuevo DataFrame solo con esas columnas
df_complete = df[complete_cols]

# Crear carpeta clean si no existe
os.makedirs("data/clean", exist_ok=True)

# Guardar CSV limpio solo con columnas completas
output_csv = "data/clean/tv_shows_clean.csv"
df_complete.to_csv(output_csv, index=False)

print(f"✅ CSV filtrado guardado en {output_csv}")
print(f"Columnas incluidas: {complete_cols}")
print(f"Total de registros: {len(df_complete)}")
