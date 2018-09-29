from typing import List

from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPostSds, \
    PathResolvingEnvironmentPreOrPostSds
from exactly_lib.test_case.result import pfh
from exactly_lib.test_case_file_structure import sandbox_directory_structure as _sds
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.util.string import line_separated
from exactly_lib.util.symbol_table import SymbolTable


class ErrorMessageResolvingEnvironment:
    def __init__(self,
                 tcds: HomeAndSds,
                 symbols: SymbolTable = None):
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

    @property
    def path_resolving_environment(self) -> PathResolvingEnvironmentPostSds:
        return PathResolvingEnvironmentPostSds(self.sds, self.symbols)

    @property
    def path_resolving_environment_pre_or_post_sds(self) -> PathResolvingEnvironmentPreOrPostSds:
        return PathResolvingEnvironmentPreOrPostSds(self.tcds, self.symbols)


class ErrorInfo:
    def error_message(self) -> str:
        raise NotImplementedError('abstract method')

    def as_pfh_fail(self) -> pfh.PassOrFailOrHardError:
        return pfh.new_pfh_fail(self.error_message())


class ExplanationErrorInfo(ErrorInfo):
    def __init__(self,
                 explanation: str,
                 object_description_lines: List[str]):
        """
        :param object_description_lines: Describes the object that the failure relates to.
        :param explanation: A single line explanation of the cause of the failure.
        """
        self.explanation = explanation
        self.object_description_lines = object_description_lines

    def error_message(self) -> str:
        lines = [self.explanation]
        if self.object_description_lines:
            lines.append('')
            lines.extend(self.object_description_lines)

        return line_separated(lines)


class ErrorMessagePartConstructor:
    """Constructs lines that are a part of an error message."""

    def lines(self, environment: ErrorMessageResolvingEnvironment) -> List[str]:
        """
        :return: empty list if there is nothing to say
        """
        raise NotImplementedError('abstract method')


class NoErrorMessagePartConstructor(ErrorMessagePartConstructor):
    def lines(self, environment: ErrorMessageResolvingEnvironment) -> List[str]:
        return []


class MultipleErrorMessagePartConstructor(ErrorMessagePartConstructor):
    def __init__(self,
                 separator_lines: List[str],
                 constructors: List[ErrorMessagePartConstructor]):
        self.separator_lines = tuple(separator_lines)
        self.constructors = tuple(constructors)

    def lines(self, environment: ErrorMessageResolvingEnvironment) -> List[str]:

        ret_val = []

        for constructor in self.constructors:
            lines = constructor.lines(environment)
            if lines:
                if ret_val:
                    ret_val.extend(self.separator_lines)
                ret_val.extend(lines)

        return ret_val
