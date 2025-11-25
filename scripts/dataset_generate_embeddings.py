import pandas as pd
from llama_index.embeddings.ollama import OllamaEmbedding
import os

# Configuración ---
INPUT_CSV = "data/clean/tv_shows_clean.csv"
OUTPUT_CSV = "data/clean/tv_shows_embeddings.csv"
MODEL_NAME = "mxbai-embed-large:latest"
BASE_URL = "http://localhost:11434"

# Cargar CSV
df = pd.read_csv(INPUT_CSV)

# Crear modelo de embeddings
emb_model = OllamaEmbedding(
    model_name=MODEL_NAME,
    base_url=BASE_URL
)

# Función para combinar texto relevante
def text_for_embedding(row):
    return f"{row['title']} {row['description']} {row['genre']}"

# Generar embeddings
embeddings = emb_model.get_text_embedding_batch(
    [text_for_embedding(r) for _, r in df.iterrows()],
    show_progress=True
)

# Añadir embeddings al DataFrame
df['embedding'] = embeddings

# Guardar CSV con embeddings
os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
df.to_csv(OUTPUT_CSV, index=False)

print(f"✅ Embeddings generados y guardados en {OUTPUT_CSV}")
print(f"Total de registros: {len(df)}")
