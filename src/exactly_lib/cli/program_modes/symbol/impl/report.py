from abc import ABC, abstractmethod
from typing import Sequence

from exactly_lib.cli.program_modes.symbol.impl.reports.symbol_info import DefinitionsResolver
from exactly_lib.util.simple_textstruct.structure import MajorBlock


class ReportBlock(ABC):
    @abstractmethod
    def render(self) -> MajorBlock:
        pass


class Report(ABC):
    @property
    @abstractmethod
    def is_success(self) -> bool:
        pass

    @abstractmethod
    def blocks(self) -> Sequence[ReportBlock]:
        pass


class ReportGenerator(ABC):
    @abstractmethod
    def generate(self, definitions_resolver: DefinitionsResolver) -> Report:
        pass
