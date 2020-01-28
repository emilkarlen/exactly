from typing import Sequence, List, Optional

from exactly_lib.symbol.data import path_sdvs
from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.symbol.logic.files_matcher import FilesMatcherSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.symbol.test_resources.files_matcher import is_reference_to_files_matcher__ref
from exactly_lib_test.test_case_file_structure.test_resources import tcds_populators
from exactly_lib_test.test_case_file_structure.test_resources.ds_construction import TcdsArrangement
from exactly_lib_test.test_case_utils.file_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.file_matcher.test_resources.integration_check import ModelConstructor
from exactly_lib_test.test_case_utils.files_matcher.models.test_resources.test_data import FileElementForTest
from exactly_lib_test.test_case_utils.files_matcher.test_resources import arguments_building as fms_args
from exactly_lib_test.test_case_utils.files_matcher.test_resources.arguments_building import FilesMatcherArg
from exactly_lib_test.test_case_utils.matcher.test_resources.integration_check import Arrangement, arrangement_w_tcds, \
    Expectation, ParseExpectation, ExecutionExpectation
from exactly_lib_test.test_resources.files.file_structure import DirContents, Dir, FileSystemElement
from exactly_lib_test.test_resources.strings import WithToString
from exactly_lib_test.test_resources.test_utils import EA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class DepthArgs:
    def __init__(self,
                 min_depth: Optional[WithToString] = None,
                 max_depth: Optional[WithToString] = None,
                 ):
        self.max_depth = max_depth
        self.min_depth = min_depth

    def min_depth_arg(self):
        raise NotImplementedError('todo')


class LimitationCase:
    def __init__(self,
                 depth_args: DepthArgs,
                 data: EA[List[FileElementForTest], List[FileSystemElement]]
                 ):
        self.depth_args = depth_args
        self.data = data


class IntegrationCheckHelper:
    def __init__(self,
                 files_matcher_name: str = 'the_files_matcher',
                 checked_dir_location: RelOptionType = RelOptionType.REL_TMP,
                 checked_dir_name: str = 'checked-dir',
                 ):
        self.files_matcher_name = files_matcher_name
        self.checked_dir_location = checked_dir_location
        self.checked_dir_name = checked_dir_name

    def checked_dir_path(self) -> PathSdv:
        return path_sdvs.of_rel_option_with_const_file_name(self.checked_dir_location,
                                                            self.checked_dir_name)

    def model_constructor_for_checked_dir(self) -> ModelConstructor:
        return integration_check.file_in_tcds(self.checked_dir_location,
                                              self.checked_dir_name)

    def files_matcher_sym_ref_arg(self) -> FilesMatcherArg:
        return fms_args.SymbolReference(self.files_matcher_name)

    def symbol_references_expectation(self) -> ValueAssertion[Sequence[SymbolReference]]:
        return asrt.matches_singleton_sequence(
            is_reference_to_files_matcher__ref(self.files_matcher_name)
        )

    def arrangement_for_contents_of_model(self,
                                          checked_dir_contents: List[FileSystemElement],
                                          files_matcher_symbol_value: FilesMatcherSdv,
                                          ) -> Arrangement:
        return arrangement_w_tcds(
            tcds_contents=tcds_populators.TcdsPopulatorForRelOptionType(
                self.checked_dir_location,
                DirContents([
                    Dir(self.checked_dir_name, checked_dir_contents)
                ])
            ),
            symbols=symbol_utils.symbol_table_from_name_and_sdv_mapping({
                self.files_matcher_name:
                    files_matcher_symbol_value
            })
        )

    def tcds_arrangement_for_contents_of_model(self,
                                               checked_dir_contents: List[FileSystemElement],
                                               ) -> TcdsArrangement:
        return TcdsArrangement(
            tcds_contents=tcds_populators.TcdsPopulatorForRelOptionType(
                self.checked_dir_location,
                DirContents([
                    Dir(self.checked_dir_name, checked_dir_contents)
                ])
            ),
        )

    def parse_expectation_of_symbol_references(self) -> ParseExpectation:
        return ParseExpectation(
            symbol_references=self.symbol_references_expectation()
        )

    def expectation(self, execution: ExecutionExpectation) -> Expectation:
        return Expectation(
            ParseExpectation(
                symbol_references=asrt.matches_singleton_sequence(
                    is_reference_to_files_matcher__ref(self.files_matcher_name)
                ),
            ),
            execution
        )
