import os

from google import genai
from google.genai import types

from core.shared.database import SessionLocal
from core.shared.models import Conhecimento

DIMENSAO_EMBEDDING = 768


def _client() -> genai.Client:
    return genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def gerar_embedding(texto: str) -> list[float]:
    resultado = _client().models.embed_content(
        model="gemini-embedding-2",
        contents=texto,
        config=types.EmbedContentConfig(output_dimensionality=DIMENSAO_EMBEDDING),
    )
    return resultado.embeddings[0].values


def salvar_conhecimento(channel_id, titulo: str, conteudo: str, fontes: list[dict] | None = None) -> Conhecimento:
    embedding = gerar_embedding(f"{titulo}\n{conteudo}")
    db = SessionLocal()
    try:
        item = Conhecimento(
            channel_id=channel_id,
            titulo=titulo,
            conteudo=conteudo,
            fontes=fontes,
            embedding=embedding,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item
    finally:
        db.close()


def buscar_conhecimento_relevante(channel_id, consulta: str, limite: int = 3) -> list[Conhecimento]:
    embedding_consulta = gerar_embedding(consulta)
    db = SessionLocal()
    try:
        return (
            db.query(Conhecimento)
            .filter(Conhecimento.channel_id == channel_id)
            .order_by(Conhecimento.embedding.cosine_distance(embedding_consulta))
            .limit(limite)
            .all()
        )
    finally:
        db.close()
