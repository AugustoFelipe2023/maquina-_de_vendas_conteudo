from core.ai_providers.gemini_provider import GeminiProvider
from core.content.conhecimento_service import buscar_conhecimento_relevante, salvar_conhecimento
from core.shared.database import SessionLocal
from core.shared.models import Channel, ContentPiece, ContentVersion, StatusConteudo


def criar_roteiro(channel_slug: str, tema: str, duracao_segundos: int = 30) -> ContentVersion:
    db = SessionLocal()
    try:
        channel = db.query(Channel).filter_by(slug=channel_slug).first()
        if channel is None:
            raise ValueError(f"Canal '{channel_slug}' nao encontrado")

        piece = ContentPiece(channel_id=channel.id, tema=tema, status=StatusConteudo.ROTEIRIZACAO)
        db.add(piece)
        db.flush()

        try:
            relevantes = buscar_conhecimento_relevante(channel.id, tema)
            contexto_adicional = "\n---\n".join(f"{c.titulo}: {c.conteudo}" for c in relevantes)

            provider = GeminiProvider()
            resultado = provider.gerar_roteiro(
                tema=tema, duracao_segundos=duracao_segundos, contexto_adicional=contexto_adicional
            )
        except Exception as exc:
            piece.status = StatusConteudo.COM_ERRO
            db.commit()
            raise RuntimeError(f"Falha ao gerar roteiro: {exc}") from exc

        version = ContentVersion(
            content_piece_id=piece.id,
            numero_versao=1,
            roteiro=resultado.roteiro,
            titulo_sugerido=resultado.titulo,
            hashtags=", ".join(resultado.hashtags),
            fontes=resultado.fontes,
        )
        db.add(version)
        db.commit()
        db.refresh(version)

        try:
            salvar_conhecimento(
                channel_id=channel.id,
                titulo=resultado.titulo,
                conteudo=resultado.roteiro,
                fontes=resultado.fontes,
            )
        except Exception:
            pass  # roteiro ja foi salvo com sucesso; falha em salvar conhecimento nao deve quebrar o fluxo


        return version
    finally:
        db.close()
