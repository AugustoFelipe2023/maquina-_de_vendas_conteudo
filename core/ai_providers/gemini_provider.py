import os

from google import genai

from core.ai_providers.base import AIProvider, RoteiroResult

PROMPT_TEMPLATE = """Você é um roteirista de vídeos curtos para redes sociais (Instagram/TikTok/YouTube Shorts).
Tema: {tema}
Duração alvo: {duracao} segundos de narração.

Gere:
1. Um título chamativo (máx. 60 caracteres)
2. Um roteiro de narração seguindo a estrutura Gancho -> Contexto -> Desenvolvimento -> Virada/Call to action
3. 5 hashtags relevantes

Responda EXATAMENTE neste formato:
TITULO: <titulo>
ROTEIRO: <roteiro>
HASHTAGS: <hashtag1>, <hashtag2>, <hashtag3>, <hashtag4>, <hashtag5>
"""


class GeminiProvider(AIProvider):
    def __init__(self, api_key: str | None = None, model_name: str = "gemini-3.8-flash"):
        chave = api_key or os.getenv("GEMINI_API_KEY")
        if not chave:
            raise ValueError("GEMINI_API_KEY não configurada")
        self._client = genai.Client(api_key=chave)
        self._model_name = model_name

    def gerar_roteiro(self, tema: str, duracao_segundos: int = 30) -> RoteiroResult:
        prompt = PROMPT_TEMPLATE.format(tema=tema, duracao=duracao_segundos)
        interaction = self._client.interactions.create(
            model=self._model_name,
            input=prompt,
        )
        return self._parse(interaction.output_text)

    def _parse(self, texto: str) -> RoteiroResult:
        titulo = ""
        roteiro = ""
        hashtags: list[str] = []

        for linha in texto.splitlines():
            if linha.startswith("TITULO:"):
                titulo = linha.replace("TITULO:", "").strip()
            elif linha.startswith("ROTEIRO:"):
                roteiro = linha.replace("ROTEIRO:", "").strip()
            elif linha.startswith("HASHTAGS:"):
                bruto = linha.replace("HASHTAGS:", "").strip()
                hashtags = [h.strip() for h in bruto.split(",") if h.strip()]

        return RoteiroResult(titulo=titulo, roteiro=roteiro, hashtags=hashtags, provider="gemini")
