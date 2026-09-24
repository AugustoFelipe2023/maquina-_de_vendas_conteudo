from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class RoteiroResult:
    titulo: str
    roteiro: str
    hashtags: list[str]
    provider: str
    fontes: list[dict] = field(default_factory=list)


class AIProvider(ABC):
    """Contrato comum para qualquer provedor de IA de geração de roteiro."""

    @abstractmethod
    def gerar_roteiro(self, tema: str, duracao_segundos: int = 30, contexto_adicional: str = "") -> RoteiroResult:
        ...

