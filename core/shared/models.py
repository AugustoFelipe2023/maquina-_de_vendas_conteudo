import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector


from core.shared.database import Base


class StatusConteudo(str, enum.Enum):
    PLANEJAMENTO = "planejamento"
    PESQUISA = "pesquisa"
    ROTEIRIZACAO = "roteirizacao"
    PRODUCAO = "producao"
    EDICAO = "edicao"
    REVISAO = "revisao"
    AGUARDANDO_APROVACAO = "aguardando_aprovacao"
    APROVADO = "aprovado"
    AGUARDANDO_PUBLICACAO = "aguardando_publicacao"
    PUBLICADO = "publicado"
    REJEITADO = "rejeitado"
    CANCELADO = "cancelado"
    COM_ERRO = "com_erro"


class StatusAprovacao(str, enum.Enum):
    PENDENTE = "pendente"
    APROVADO = "aprovado"
    REJEITADO = "rejeitado"
    ALTERACAO_SOLICITADA = "alteracao_solicitada"
    CANCELADO = "cancelado"


class StatusPublicacao(str, enum.Enum):
    PENDENTE = "pendente"
    PUBLICADO = "publicado"
    ERRO = "erro"


class Channel(Base):
    __tablename__ = "channels"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    content_pieces: Mapped[list["ContentPiece"]] = relationship(back_populates="channel")


class ContentPiece(Base):
    __tablename__ = "content_pieces"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    channel_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("channels.id"), nullable=False)
    tema: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[StatusConteudo] = mapped_column(Enum(StatusConteudo), default=StatusConteudo.PLANEJAMENTO)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    channel: Mapped["Channel"] = relationship(back_populates="content_pieces")
    versions: Mapped[list["ContentVersion"]] = relationship(back_populates="content_piece")


class ContentVersion(Base):
    __tablename__ = "content_versions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_piece_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_pieces.id"), nullable=False)
    numero_versao: Mapped[int] = mapped_column(Integer, nullable=False)
    roteiro: Mapped[str | None] = mapped_column(Text, nullable=True)
    caminho_video: Mapped[str | None] = mapped_column(String(500), nullable=True)
    caminho_thumbnail: Mapped[str | None] = mapped_column(String(500), nullable=True)
    titulo_sugerido: Mapped[str | None] = mapped_column(String(200), nullable=True)
    descricao_sugerida: Mapped[str | None] = mapped_column(Text, nullable=True)
    hashtags: Mapped[str | None] = mapped_column(String(500), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    fontes: Mapped[list | None] = mapped_column(JSONB, nullable=True)


    content_piece: Mapped["ContentPiece"] = relationship(back_populates="versions")


class Approval(Base):
    __tablename__ = "approvals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_versions.id"), nullable=False)
    status: Mapped[StatusAprovacao] = mapped_column(Enum(StatusAprovacao), default=StatusAprovacao.PENDENTE)
    plataformas_confirmadas: Mapped[str | None] = mapped_column(String(200), nullable=True)
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)
    respondido_em: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Publication(Base):
    __tablename__ = "publications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_versions.id"), nullable=False)
    plataforma: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[StatusPublicacao] = mapped_column(Enum(StatusPublicacao), default=StatusPublicacao.PENDENTE)
    url_publicada: Mapped[str | None] = mapped_column(String(500), nullable=True)
    erro_mensagem: Mapped[str | None] = mapped_column(Text, nullable=True)
    publicado_em: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Conhecimento(Base):
    __tablename__ = "conhecimento"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    channel_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("channels.id"), nullable=False)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    conteudo: Mapped[str] = mapped_column(Text, nullable=False)
    fontes: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    embedding: Mapped[list[float]] = mapped_column(Vector(768), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
