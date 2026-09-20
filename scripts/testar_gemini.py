import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv()

from core.ai_providers.gemini_provider import GeminiProvider

if __name__ == "__main__":
    provider = GeminiProvider()
    resultado = provider.gerar_roteiro(tema="GTA 6 - o que sabemos ate agora", duracao_segundos=30)

    print("TITULO:", resultado.titulo)
    print("ROTEIRO:", resultado.roteiro)
    print("HASHTAGS:", resultado.hashtags)
    print("PROVIDER:", resultado.provider)
