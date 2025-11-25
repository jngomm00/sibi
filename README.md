# 📺 TV Show RAG Recommender System

Este proyecto implementa un sistema de recomendación semántica de series de televisión ("TV Shows") utilizando una arquitectura **RAG (Retrieval-Augmented Generation)** personalizada.

Combina datos de múltiples plataformas de streaming (Netflix, Amazon Prime, Hulu, Disney+), los procesa mediante embeddings locales (**Ollama**) y los almacena en un grafo (**Neo4j**). La inferencia final se realiza con **Groq** para obtener respuestas ultrarrápidas.

## 🏗️ Arquitectura Técnica

El sistema no utiliza un índice vectorial estándar de "caja negra", sino una implementación híbrida:

1.  **ETL & Preprocesamiento:**
    * Fusión de 4 datasets CSV.
    * Normalización de columnas y limpieza de nulos (`dropna`, `drop_duplicates`).
    * **Estrategia de Embedding:** Se concatena `title` + `description` + `genre` para generar el vector.
2.  **Almacenamiento (Neo4j):**
    * Los datos se guardan como nodos con la etiqueta `:TVShow`.
3.  **Motor de Búsqueda (Custom Retrieval):**
    * Se extraen los candidatos de Neo4j.
    * Se calcula la **Similitud del Coseno** en memoria utilizando `NumPy` entre el query del usuario y los vectores almacenados.
4.  **Generación (Groq):**
    * Se inyectan los Top-K (5) resultados más similares en el prompt del sistema.
    * Modelo LLM: `llama-3.1-8b-instant`.

---

## 🛠️ Requisitos e Instalación

### 1. Prerrequisitos de Infraestructura
* **Python 3.9+**
* **Neo4j Database:** Instancia activa (local o Docker).
* **Ollama:** Ejecutándose localmente para embeddings.
* **Groq API Key:** Necesaria para el LLM.

### 2. Dependencias Python
Instala las librerías utilizadas en el notebook:

```bash
pip install pandas numpy
pip install neo4j
pip install fastapi uvicorn
pip install llama-index-core
pip install llama-index-llms-groq
pip install llama-index-embeddings-ollama
```

### 3. Configuración de Modelos
El sistema espera el siguiente modelo de embeddings en Ollama:

```bash
ollama pull mxbai-embed-large
```

---

## 📂 Estructura de Datos y Archivos

Para que el pipeline de ingestión funcione, la estructura de carpetas debe ser:

```text
.
├── data/
│   ├── netflix_titles.csv
│   ├── amazon_prime_titles.csv
│   ├── hulu_titles.csv
│   ├── disney_plus_titles.csv
│   └── clean/                  # Generado automáticamente por el script
├── front/                      # Archivos estáticos del frontend
├── scripts/
│   ├── main.py                 # Lógica de FastAPI
│   └── groq_recommender.py     # Clase GroqRecommender
└── script.ipynb                # Notebook de ingestión y pruebas
```

---

## 💾 Esquema de Base de Datos (Neo4j)

El script de ingestión crea nodos con la siguiente estructura Cypher:

```cypher
(:TVShow {
    title: String,
    description: String,
    release_year: Integer,
    genre: String,
    platform: String,
    embedding: List<Float>
})
```

---

## 🚀 Ejecución y Uso

### Paso 1: Ingesta de Datos
Ejecuta las celdas del notebook `script.ipynb` o el script de ETL derivado para:
1.  Limpiar y unificar CSVs.
2.  Generar embeddings (esto puede tomar tiempo dependiendo del hardware).
3.  Cargar los datos en Neo4j.

### Paso 2: Levantar el Servidor API
El servidor utiliza `uvicorn` y `FastAPI`.

```bash
# Asegúrate de estar en la raíz del proyecto
uvicorn scripts.main:app --host 127.0.0.1 --port 8000 --reload
```

### Paso 3: Consumo de la API (Polling)
La API es asíncrona para no bloquear el hilo principal mientras el LLM piensa.

**1. Enviar consulta (`POST /send`):**
```json
{
  "content": "Recomiéndame algo de terror psicológico de los 90"
}
```
**Respuesta:**
```json
{
  "link": "/result/a1b2c3d4"
}
```

**2. Obtener resultado (`GET /result/a1b2c3d4`):**
* Si está procesando: `{"status": "not ready"}`
* Si terminó:
```json
{
  "status": "ready",
  "message": "Te recomiendo ver Twin Peaks..."
}
```

---
**Nota:** Asegúrate de configurar las variables de entorno o editar las constantes `NEO4J_URI`, `NEO4J_PASSWORD` y `groq_api_key` en el archivo `groq_recommender.py` antes de iniciar.
