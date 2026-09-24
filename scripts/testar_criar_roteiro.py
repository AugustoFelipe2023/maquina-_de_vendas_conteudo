import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv()

from core.content.roteiro_service import criar_roteiro

if __name__ == "__main__":
    versao = criar_roteiro(channel_slug="cultura-games", tema="Os melhores jogos de terror de 2026")
    print("ContentVersion ID:", versao.id)
    print("Titulo:", versao.titulo_sugerido)
    print("Roteiro:", versao.roteiro)
    print("Hashtags:", versao.hashtags)
