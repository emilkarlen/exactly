from typing import Any, Mapping

from exactly_lib.section_document.element_parsers.token_stream_parser import ErrorMessageGenerator


class ConstantErrorMessage(ErrorMessageGenerator):
    def __init__(self, message: str):
        self._message = message

    def message(self) -> str:
        return self._message


class MessageFactory:
    def __init__(self, format_map: Mapping[str, Any]):
        self.format_map = format_map

    def generator_for(self, template: str) -> ErrorMessageGenerator:
        return GeneratorForTemplate(self.format_map, template)


class GeneratorForTemplate(ErrorMessageGenerator):
    def __init__(self,
                 format_map: Mapping[str, Any],
                 template: str,
                 ):
        self._format_map = format_map
        self._template = template

    def message(self) -> str:
        return self._template.format_map(self._format_map)
