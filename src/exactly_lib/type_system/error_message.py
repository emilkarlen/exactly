from abc import ABC, abstractmethod
from typing import List, Optional

from exactly_lib.common.report_rendering import print
from exactly_lib.common.report_rendering import text_docs
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.test_case_file_structure import sandbox_directory_structure as _sds
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.util.symbol_table import SymbolTable


class ErrorMessageResolvingEnvironment:
    def __init__(self,
                 tcds: HomeAndSds,
                 symbols: Optional[SymbolTable] = None):
        self._tcds = tcds
        self._symbols = SymbolTable() if symbols is None else symbols

    @property
    def tcds(self) -> HomeAndSds:
        return self._tcds

    @property
    def sds(self) -> _sds.SandboxDirectoryStructure:
        return self._tcds.sds

    @property
    def symbols(self) -> SymbolTable:
        return self._symbols


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
