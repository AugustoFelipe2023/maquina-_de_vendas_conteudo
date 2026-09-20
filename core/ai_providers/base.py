from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class RoteiroResult:
    titulo: str
    roteiro: str
    hashtags: list[str]
    provider: str


class AIProvider(ABC):
    """Contrato comum para qualquer provedor de IA de geração de roteiro."""

    @abstractmethod
    def gerar_roteiro(self, tema: str, duracao_segundos: int = 30) -> RoteiroResult:
        ...
