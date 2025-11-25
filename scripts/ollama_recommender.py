import numpy as np
from neo4j import GraphDatabase
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core.base.llms.types import ChatMessage

class OllamaRecommender:
    def __init__(
        self,
        neo4j_uri="neo4j://127.0.0.1:7687",
        neo4j_user="neo4j",
        neo4j_password="j7hm3HtMmuj3g75",
        neo4j_db="neo4j",
        model_name_embed="mxbai-embed-large:latest",
        model_name_llm="qwen2.5:0.5b",
        top_k=5,
    ):
        self.neo4j_uri = neo4j_uri
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password
        self.neo4j_db = neo4j_db
        self.top_k = top_k

        # --- Inicialización de modelos y base de datos ---
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        self.emb_model = OllamaEmbedding(model_name=model_name_embed)
        self.llm = Ollama(model=model_name_llm)

    def _coseno_sim(self, a, b):
        a, b = np.array(a), np.array(b)
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def _get_shows(self):
        """Devuelve todos los shows almacenados en Neo4j con sus embeddings."""
        with self.driver.session(database=self.neo4j_db) as session:
            result = session.run("""
                MATCH (s:TVShow)
                RETURN s.title AS title, s.description AS description, 
                       s.genre AS genre, s.platform AS platform, 
                       s.embedding AS embedding
            """)
            shows = []
            for record in result:
                emb = record.get("embedding")
                if emb:
                    shows.append({
                        "title": record["title"],
                        "description": record["description"],
                        "genre": record["genre"],
                        "platform": record["platform"],
                        "embedding": np.array(emb, dtype=float)
                    })
            return shows

    def recommend(self, query: str) -> str:
        """Genera una recomendación basada en una consulta del usuario."""
        try:
            # 1️⃣ Embedding de la consulta
            query_emb = self.emb_model.get_text_embedding_batch([query])[0]

            # 2️⃣ Obtener series desde Neo4j
            shows = self._get_shows()
            if not shows:
                return "No hay series disponibles en la base de datos."

            # 3️⃣ Calcular similitudes
            sims = [(self._coseno_sim(query_emb, s["embedding"]), s) for s in shows]
            sims = sorted(sims, reverse=True, key=lambda x: x[0])
            top_shows = [s[1] for s in sims[:self.top_k]]

            print("List by embeddings: ")
            print({chr(10).join([f"- {s['title']} ({s['genre']}, {s['platform']}) — {s['description']}" for s in top_shows])})

            # 4️⃣ Create prompt
            prompt = f"""
            You are an expert in TV and streaming entertainment with deep knowledge of genres, storylines, and audiences. 
            Your goal is to help the user discover TV shows they might love, based on their message.

            Instructions:
            - Always write TV show titles surrounded by double asterisks, like **Breaking Bad**.
            - Always respond in a warm, conversational, and natural tone — like a friend who knows a lot about TV.
            - Never go off-topic. If the user asks about something unrelated to TV shows, gently remind them that you only recommend shows.
            - Focus on why each show fits the user’s request (genre, mood, tone, or theme), not just listing names.
            - Mention 3–5 recommendations maximum.
            - Do not use markdown other than the ** for titles.

            Context:
            The user said: "{query}"

            Here are some shows from the database that might match the user's interests:
            {chr(10).join([f"- {s['title']} ({s['genre']}, {s['platform']}) — {s['description']}" for s in top_shows])}

            Now, write a short and natural recommendation message as if you were chatting directly with the user.
            """

            # 5️⃣ Generar respuesta
            messages = [ChatMessage(role="user", content=prompt)]
            respuesta = self.llm.chat(messages)
            print("LLM Response: ")
            print(respuesta.message.content)
            return respuesta.message.content

        except Exception as e:
            return f"Error al generar recomendación: {str(e)}"

    def close(self):
        """Cierra la conexión con Neo4j."""
        self.driver.close()
