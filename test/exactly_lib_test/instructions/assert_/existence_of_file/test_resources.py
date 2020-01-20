from abc import ABC, abstractmethod
from typing import List, Optional

from exactly_lib.definitions import expression
from exactly_lib.instructions.assert_ import existence_of_file
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib_test.test_case_file_structure.test_resources.arguments_building import PathArgument
from exactly_lib_test.test_case_utils.file_matcher.test_resources.argument_building import FileMatcherArg


class Argument(ABC):
    """Generate source using __str__"""
    pass

    def __str__(self):
        return ' '.join([str(element) for element in self.elements])

    @property
    @abstractmethod
    def elements(self) -> List:
        pass


class PathArg(Argument):
    """Generate source using __str__"""

    def __init__(self, path: PathArgument):
        self.path = path

    @property
    def elements(self) -> List:
        return list(self.path.elements)


class CompleteInstructionArg(Argument):
    def __init__(self,
                 expectation_type: ExpectationType,
                 path: PathArg,
                 file_matcher: Optional[FileMatcherArg] = None):
        self.expectation_type = expectation_type
        self.path = path
        self.file_matcher = file_matcher

    @property
    def elements(self) -> List:
        ret_val = []

        if self.expectation_type is ExpectationType.NEGATIVE:
            ret_val += [expression.NOT_OPERATOR_NAME]

        ret_val += self.path.elements

        if self.file_matcher is not None:
            ret_val += [existence_of_file.PROPERTIES_SEPARATOR]
            ret_val += self.file_matcher.elements

        return ret_val


class WithOptionalNegation:
    def __init__(self,
                 path: PathArg,
                 file_matcher: Optional[FileMatcherArg] = None):
        self.path = path
        self.file_matcher = file_matcher

    def get(self, expectation_type: ExpectationType) -> CompleteInstructionArg:
        return CompleteInstructionArg(expectation_type,
                                      self.path,
                                      self.file_matcher)
