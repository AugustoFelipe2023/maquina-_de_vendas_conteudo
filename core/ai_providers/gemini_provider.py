import os
from datetime import date

from google import genai

from core.ai_providers.base import AIProvider, RoteiroResult

PROMPT_TEMPLATE = """Você é um roteirista de vídeos curtos para redes sociais (Instagram/TikTok/YouTube Shorts), especializado em games, cultura pop, filmes e tecnologia.
Data de hoje: {data_hoje}
Tema: {tema}
Duração alvo: {duracao} segundos de narração.
{contexto_bloco}
REGRAS DE PRECISÃO (muito importantes):
- Use a ferramenta de busca para confirmar fatos atuais antes de escrever qualquer informação específica (datas, parcerias, nomes de projetos, declarações).
- Nunca invente ou presuma datas de lançamento, plataformas, parcerias ou detalhes tecnicos que não estejam confirmados pela busca.
- Se uma informação for rumor, especulação ou ainda não oficial, deixe isso EXPLÍCITO no roteiro (ex.: "segundo rumores", "ainda sem data oficial confirmada").
- Prefira não mencionar um detalhe a mencionar um detalhe errado.

Gere:
1. Um título chamativo (máx. 60 caracteres)
2. Um roteiro de narração seguindo a estrutura Gancho -> Contexto -> Desenvolvimento -> Virada/Call to action
3. 5 hashtags relevantes

Responda EXATAMENTE neste formato:
TITULO: <titulo>
ROTEIRO: <roteiro>
HASHTAGS: <hashtag1>, <hashtag2>, <hashtag3>, <hashtag4>, <hashtag5>
"""

VERIFICACAO_PROMPT_TEMPLATE = """Você é um verificador de fatos rigoroso, checando um roteiro de vídeo sobre "{tema}" (data de hoje: {data_hoje}).

ROTEIRO ORIGINAL:
{roteiro_original}

Tarefa:
1. Identifique cada afirmação factual específica no roteiro (datas, nomes de projetos, parcerias, plataformas, declarações).
2. Use a busca para confirmar cada uma com fontes atuais e confiáveis.
3. Reescreva o roteiro corrigindo qualquer afirmação incorreta e adicionando qualificadores claros ("segundo rumores", "ainda sem confirmação oficial") em qualquer informação não 100% confirmada.
4. Mantenha o mesmo tom, estrutura e duração aproximada. Não adicione novas afirmações não verificadas.

Responda EXATAMENTE neste formato:
TITULO: <titulo revisado ou o mesmo, se já estiver correto>
ROTEIRO: <roteiro revisado>
HASHTAGS: <hashtag1>, <hashtag2>, <hashtag3>, <hashtag4>, <hashtag5>
"""


class GeminiProvider(AIProvider):
    def __init__(
        self,
        api_key: str | None = None,
        model_name: str = "gemini-3.8-flash",
        model_verificacao: str = "gemini-3.5-flash-lite",
    ):
        chave = api_key or os.getenv("GEMINI_API_KEY")
        if not chave:
            raise ValueError("GEMINI_API_KEY não configurada")
        self._client = genai.Client(api_key=chave)
        self._model_name = model_name
        self._model_verificacao = model_verificacao

    def gerar_roteiro(self, tema: str, duracao_segundos: int = 30, contexto_adicional: str = "") -> RoteiroResult:
        data_hoje = date.today().isoformat()
        contexto_bloco = (
            f"\nCONTEXTO DE ROTEIROS ANTERIORES DO CANAL (evite repetir temas, mantenha consistência):\n{contexto_adicional}\n"
            if contexto_adicional
            else ""
        )

        rascunho = self._gerar(
            PROMPT_TEMPLATE.format(
                tema=tema, duracao=duracao_segundos, data_hoje=data_hoje, contexto_bloco=contexto_bloco
            ),
            model=self._model_name,
        )

        revisado = self._gerar(
            VERIFICACAO_PROMPT_TEMPLATE.format(
                tema=tema, data_hoje=data_hoje, roteiro_original=rascunho.roteiro
            ),
            model=self._model_verificacao,
        )
        return revisado


    def _gerar(self, prompt: str, model: str) -> RoteiroResult:
        interaction = self._client.interactions.create(
            model=model,
            input=prompt,
            tools=[{"type": "google_search"}],
        )
        resultado = self._parse(interaction.output_text)
        resultado.fontes = self._extrair_fontes(interaction)
        return resultado

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

    def _extrair_fontes(self, interaction) -> list[dict]:
        fontes = []
        for step in getattr(interaction, "steps", []) or []:
            if getattr(step, "type", None) != "model_output":
                continue
            for content_block in getattr(step, "content", []) or []:
                if getattr(content_block, "type", None) != "text":
                    continue
                for annotation in getattr(content_block, "annotations", None) or []:
                    if getattr(annotation, "type", None) == "url_citation":
                        fontes.append(
                            {
                                "titulo": getattr(annotation, "title", ""),
                                "url": getattr(annotation, "url", ""),
                            }
                        )
        return fontes
