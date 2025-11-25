import os
import asyncio
import string
import random
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import re

from scripts.groq_recommender import GroqRecommender

app = FastAPI()
llm_recommender = GroqRecommender()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONT_DIR = os.path.join(BASE_DIR, "front")

# Almacen temporal de resultados
results = {}


def format_bold(text):
    # Compilar la expresión regular
    pattern = re.compile(r"\*\*\s*(.*?)\s*\*\*")

    # Reemplazar todas las coincidencias
    def repl(match):
        return f"<b>{match.group(1)}</b>"

    return pattern.sub(repl, text)

def generate_random_id(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


@app.post("/send")
async def receive_content(request: Request):
    data = await request.json()
    content = data.get("content", "")

    # Generar ID y registrar como "not ready"
    link_id = generate_random_id()
    results[link_id] = {"status": "not ready", "message": content}

    # Iniciar proceso asíncrono para procesar el texto
    asyncio.create_task(process_content(link_id))

    # Devolver link al cliente
    return JSONResponse({"link": f"/result/{link_id}"})


async def process_content(link_id: str):
    response = llm_recommender.recommend(results[link_id]["message"])
    response = response.replace("\n", "<br>")
    response = format_bold(response)
    results[link_id]["status"] = "ready"
    results[link_id]["message"] = response


@app.get("/result/{link_id}")
async def get_result(link_id: str):
    result = results.get(link_id)
    if not result:
        return JSONResponse({"error": "invalid link"}, status_code=404)

    if result["status"] == "not ready":
        return JSONResponse({"status": "not ready"})
    else:
        return JSONResponse({
            "status": "ready",
            "message": result["message"]
        })


# Servir el front-end
app.mount("/", StaticFiles(directory=FRONT_DIR, html=True), name="front")

if __name__ == "__main__":
    uvicorn.run("scripts.main:app", host="127.0.0.1", port=8000, reload=True)
