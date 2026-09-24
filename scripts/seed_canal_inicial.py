import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv()

from core.shared.database import SessionLocal
from core.shared.models import Channel

if __name__ == "__main__":
    db = SessionLocal()
    try:
        existente = db.query(Channel).filter_by(slug="cultura-games").first()
        if existente:
            print("Canal já existe:", existente.id)
        else:
            canal = Channel(
                slug="cultura-games",
                nome="Cultura, Games e Entretenimento",
                descricao="Games, filmes, series, livros, cultura pop, curiosidades e historia.",
            )
            db.add(canal)
            db.commit()
            db.refresh(canal)
            print("Canal criado:", canal.id)
    finally:
        db.close()
