from abc import ABC, abstractmethod
from typing import List

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


class PropertyDescription:
    def __init__(self,
                 name: str,
                 object_description_lines: List[str]):
        self._name = name
        self._details_lines = object_description_lines

    @property
    def name(self) -> str:
        return self._name

    @property
    def object_description_lines(self) -> List[str]:
        return self._details_lines


class PropertyDescriptor:
    def description(self) -> PropertyDescription:
        raise NotImplementedError('abstract method')


class FilePropertyDescriptorConstructor:
    def construct_for_contents_attribute(self, contents_attribute: str) -> PropertyDescriptor:
        raise NotImplementedError('abstract method')
