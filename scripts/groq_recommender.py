import os
import numpy as np
from neo4j import GraphDatabase

from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core.base.llms.types import ChatMessage

from llama_index.llms.groq import Groq

class GroqRecommender:
    def __init__(
            self,
            neo4j_uri="neo4j://127.0.0.1:7687",
            neo4j_user="neo4j",
            neo4j_password="",
            neo4j_db="neo4j",
            model_name_embed="mxbai-embed-large:latest",
            model_name_llm="llama-3.1-8b-instant",
            groq_api_key="",
            top_k=5,
    ):
        self.neo4j_uri = neo4j_uri
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password
        self.neo4j_db = neo4j_db
        self.top_k = top_k

        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

        self.emb_model = OllamaEmbedding(model_name=model_name_embed)


        self.llm = Groq(model=model_name_llm, api_key=groq_api_key)

    def _coseno_sim(self, a, b):
        a, b = np.array(a), np.array(b)
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def _get_shows(self):

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
        try:
            query_emb = self.emb_model.get_text_embedding_batch([query])[0]
            shows = self._get_shows()
            if not shows:
                return "No hay series disponibles en la base de datos."

            sims = [(self._coseno_sim(query_emb, s["embedding"]), s) for s in shows]
            sims = sorted(sims, reverse=True, key=lambda x: x[0])
            top_shows = [s[1] for s in sims[:self.top_k]]

            print("List by embeddings: ")
            print({chr(10).join(
                [f"- {s['title']} ({s['genre']}, {s['platform']}) — {s['description']}" for s in top_shows])})

            prompt = f"""
            You are an expert in TV and streaming entertainment.
            Your goal is to help the user discover TV shows based on their message.

            Instructions:
            - If the user ask for any other topic just tell them that you are only gonna help them with tv shows recommendations..
            - Recommendations:
            {chr(10).join([f"- {s['title']} ({s['genre']}, {s['platform']}) — {s['description']}" for s in top_shows])}

            User Query: "{query}"

            Respond in a warm tone recommending the best matches from the list above.
            """

            messages = [ChatMessage(role="user", content=prompt)]

            respuesta = self.llm.chat(messages)

            print("LLM Response: ")
            print(respuesta.message.content)
            return respuesta.message.content

        except Exception as e:
            return f"Error al generar recomendación: {str(e)}"

    def close(self):
        self.driver.close()