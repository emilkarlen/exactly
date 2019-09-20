from abc import ABC, abstractmethod

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.common.report_rendering.text_doc import TextRenderer


class ErrorMessageResolver(ABC):
    @abstractmethod
    def resolve(self) -> str:
        pass

    def resolve__tr(self) -> TextRenderer:
        return text_docs.single_pre_formatted_line_object(self.resolve())
