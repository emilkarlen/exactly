import unittest
from abc import ABC, abstractmethod
from typing import Optional, List, Sequence

from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.type_val_deps.types.path import path_sdvs
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.impls.types.file_matcher.test_resources.argument_building import FileMatcherArg
from exactly_lib_test.impls.types.files_matcher.test_resources import arguments_building as fms_args
from exactly_lib_test.impls.types.files_matcher.test_resources.arguments_building import FilesMatcherArg, \
    SymbolReference
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import Arrangement
from exactly_lib_test.impls.types.test_resources import validation
from exactly_lib_test.tcfs.test_resources import tcds_populators
from exactly_lib_test.tcfs.test_resources.ds_construction import TcdsArrangement
from exactly_lib_test.test_resources.argument_renderer import ArgumentElementsRenderer
from exactly_lib_test.test_resources.files.file_structure import FileSystemElement, DirContents, Dir
from exactly_lib_test.test_resources.strings import WithToString
from exactly_lib_test.test_resources.test_utils import NExArr
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_val_deps.types.test_resources.files_matcher import is_reference_to_files_matcher


class ModelFile:
    def __init__(self,
                 location: RelOptionType,
                 name: str,
                 ):
        self.location = location
        self.name = name

    @property
    def path(self) -> PathSdv:
        return path_sdvs.of_rel_option_with_const_file_name(
            self.location,
            self.name,
        )


DEFAULT_MODEL_FILE = ModelFile(RelOptionType.REL_TMP, 'checked-dir')


class ExecutionResult(ABC):
    pass


class FullExecutionResult(ExecutionResult):
    def __init__(self, match: bool):
        self.is_match = match


class ValidationFailure(ExecutionResult):
    def __init__(self, expectation: validation.Expectation):
        self.expectation = expectation


RESULT__MATCHES = FullExecutionResult(True)
RESULT__NOT_MATCHES = FullExecutionResult(False)


class RecWLimArguments:
    def __init__(self,
                 files_matcher: ArgumentElementsRenderer,
                 min_depth: Optional[WithToString],
                 max_depth: Optional[WithToString],
                 ):
        self.files_matcher = files_matcher
        self.min_depth = min_depth
        self.max_depth = max_depth


class Helper:
    def __init__(self,
                 model_file: ModelFile,
                 files_matcher_name,
                 ):
        self.model_file = model_file
        self.files_matcher_name = files_matcher_name

    def model_file_path(self) -> PathSdv:
        return path_sdvs.of_rel_option_with_const_file_name(self.model_file.location,
                                                            self.model_file.name)

    def files_matcher_sym_ref_arg(self) -> FilesMatcherArg:
        return fms_args.SymbolReference(self.files_matcher_name)

    def files_matcher_sym_assertion(self) -> ValueAssertion[SymbolReference]:
        return is_reference_to_files_matcher(self.files_matcher_name)

    def tcds_arrangement_for_contents_of_checked_dir(self,
                                                     contents: List[FileSystemElement],
                                                     ) -> TcdsArrangement:
        return TcdsArrangement(
            tcds_contents=tcds_populators.TcdsPopulatorForRelOptionType(
                self.model_file.location,
                DirContents([
                    Dir(self.model_file.name, contents)
                ])
            ),
        )


class TestCaseGenerator(ABC):
    def __init__(self,
                 model_file: ModelFile = DEFAULT_MODEL_FILE,
                 files_matcher_name: str = 'the_files_matcher',
                 ):
        self.model_file = model_file
        self.files_matcher_name = files_matcher_name
        self._helper = Helper(model_file, files_matcher_name)

    @abstractmethod
    def arguments(self) -> FileMatcherArg:
        pass

    @abstractmethod
    def expected_symbols(self) -> Sequence[ValueAssertion[SymbolReference]]:
        pass


class SingleCaseGenerator(TestCaseGenerator, ABC):

    @abstractmethod
    def tcds_arrangement(self) -> Optional[TcdsArrangement]:
        pass

    def symbols(self, put: unittest.TestCase) -> SymbolTable:
        return SymbolTable()

    @abstractmethod
    def execution_result(self) -> ExecutionResult:
        pass


class MultipleExecutionCasesGenerator(TestCaseGenerator, ABC):
    @abstractmethod
    def execution_cases(self) -> Sequence[NExArr[ExecutionResult, Arrangement]]:
        pass
