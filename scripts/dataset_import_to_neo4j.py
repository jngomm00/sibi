import pandas as pd
from neo4j import GraphDatabase
import ast

# Configuración
CSV_PATH = "data/clean/tv_shows_embeddings.csv"
NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = ""
NEO4J_DB = "neo4j"

# Conectar a Neo4j
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# Función para crear nodos
def crear_nodo(tx, show):
    tx.run("""
    CREATE (s:TVShow {
        title: $title,
        description: $description,
        release_year: $release_year,
        genre: $genre,
        platform: $platform,
        embedding: $embedding
    })
    """, **show)

# Leer CSV
df = pd.read_csv(CSV_PATH)

# Convertir la columna embedding de string a lista si es necesario
if isinstance(df['embedding'].iloc[0], str):
    df['embedding'] = df['embedding'].apply(ast.literal_eval)

# Insertar en Neo4j
with driver.session(database=NEO4J_DB) as session:
    for _, row in df.iterrows():
        show = {
            "title": row['title'],
            "description": row['description'],
            "release_year": int(row['release_year']),
            "genre": row['genre'],
            "platform": row['platform'],
            "embedding": row['embedding']
        }
        session.execute_write(crear_nodo, show)

driver.close()

print(f"✅ Todos los {len(df)} registros se han insertado en Neo4j como nodos TVShow")
