from abc import ABC
from typing import List, Optional

from exactly_lib.definitions import logic
from exactly_lib.impls.instructions.assert_ import existence_of_file
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib_test.impls.types.file_matcher.test_resources.argument_building import FileMatcherArg
from exactly_lib_test.tcfs.test_resources.path_arguments import PathArgument
from exactly_lib_test.test_resources.argument_renderer import ArgumentElementsRenderer


class Argument(ArgumentElementsRenderer, ABC):
    """Generate source using __str__"""
    pass


class CompleteInstructionArg(Argument):
    def __init__(self,
                 expectation_type: ExpectationType,
                 path: PathArgument,
                 file_matcher: Optional[FileMatcherArg] = None):
        self.expectation_type = expectation_type
        self.path = path
        self.file_matcher = file_matcher

    @property
    def elements(self) -> List:
        ret_val = []

        if self.expectation_type is ExpectationType.NEGATIVE:
            ret_val += [logic.NOT_OPERATOR_NAME]

        ret_val += self.path.elements

        if self.file_matcher is not None:
            ret_val += [existence_of_file.PROPERTIES_SEPARATOR]
            ret_val += self.file_matcher.elements

        return ret_val


class WithOptionalNegation:
    def __init__(self,
                 path: PathArgument,
                 file_matcher: Optional[FileMatcherArg] = None):
        self.path = path
        self.file_matcher = file_matcher

    def get(self, expectation_type: ExpectationType) -> CompleteInstructionArg:
        return CompleteInstructionArg(expectation_type,
                                      self.path,
                                      self.file_matcher)
