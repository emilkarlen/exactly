import unittest
from abc import ABC, abstractmethod
from typing import Sequence

from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.types.file_matcher.contents_of_dir.test_resources.case_generator import \
    SingleCaseGenerator, MultipleExecutionCasesGenerator


class ExecutorOfCaseGenerator(ABC):
    """
    Executes cases (defined by `TestCaseGenerator`), for a particular use case,
    e.g. dir-contents.
    The generator is designed to be useful in many use cases, e.g. for executing as
    a matcher and as an instruction.  And since these use cases use slightly
    different source - different source arguments - the generator must give
    only arguments that are common to both cases.  And it is up to the Executor
    to format the arguments appropriately.
    """

    @abstractmethod
    def execute_single(self,
                       put: unittest.TestCase,
                       case: SingleCaseGenerator,
                       ):
        pass

    @abstractmethod
    def execute_list(self,
                     put: unittest.TestCase,
                     cases: Sequence[NameAndValue[SingleCaseGenerator]]):
        pass

    @abstractmethod
    def execute_multi(self,
                      put: unittest.TestCase,
                      generator: MultipleExecutionCasesGenerator):
        pass
