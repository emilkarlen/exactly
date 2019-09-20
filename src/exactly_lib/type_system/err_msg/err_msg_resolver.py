from abc import ABC, abstractmethod

from exactly_lib.common.report_rendering import print
from exactly_lib.common.report_rendering import text_docs
from exactly_lib.common.report_rendering.text_doc import TextRenderer


class ErrorMessageResolver(ABC):
    @abstractmethod
    def resolve(self) -> str:
        pass

    def resolve__tr(self) -> TextRenderer:
        return text_docs.single_pre_formatted_line_object(self.resolve())


class ConstantErrorMessageResolver(ErrorMessageResolver):
    def __init__(self, constant: str):
        self._constant = constant

    def resolve(self) -> str:
        return self._constant


class OfTextDoc(ErrorMessageResolver):
    def __init__(self, message: TextRenderer):
        self._message = message

    def resolve(self) -> str:
        return print.print_to_str(self._message.render_sequence())
