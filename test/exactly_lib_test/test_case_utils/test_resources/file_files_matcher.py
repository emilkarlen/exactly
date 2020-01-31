from abc import ABC
from typing import Sequence, List, Mapping, Optional

from exactly_lib.symbol.logic.files_matcher import FilesMatcherSdv
from exactly_lib.symbol.sdv_structure import SymbolDependentValue
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.symbol.test_resources.files_matcher import is_reference_to_files_matcher__ref
from exactly_lib_test.test_case_utils.files_matcher.test_resources import arguments_building as fms_args
from exactly_lib_test.test_case_utils.files_matcher.test_resources.arguments_building import FilesMatcherArg
from exactly_lib_test.test_case_utils.matcher.test_resources.integration_check import Expectation, ParseExpectation, \
    ExecutionExpectation, Arrangement, arrangement_w_tcds
from exactly_lib_test.test_case_utils.test_resources.dir_arg_helper import DirArgumentHelper
from exactly_lib_test.test_resources.files.file_structure import FileSystemElement
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class IntegrationCheckWFilesMatcherHelperBase(ABC):
    def __init__(self,
                 files_matcher_name: str = 'the_files_matcher',
                 checked_dir_location: RelOptionType = RelOptionType.REL_TMP,
                 checked_dir_name: str = 'checked-dir',
                 ):
        self.files_matcher_name = files_matcher_name
        self._dir_arg_helper = DirArgumentHelper(checked_dir_location,
                                                 checked_dir_name)

    @property
    def dir_arg(self) -> DirArgumentHelper:
        return self._dir_arg_helper

    def files_matcher_sym_ref_arg(self) -> FilesMatcherArg:
        return fms_args.SymbolReference(self.files_matcher_name)

    @property
    def symbol_reference_assertion(self) -> ValueAssertion[SymbolReference]:
        return is_reference_to_files_matcher__ref(self.files_matcher_name)

    def symbol_references_expectation(self) -> ValueAssertion[Sequence[SymbolReference]]:
        return asrt.matches_singleton_sequence(
            self.symbol_reference_assertion
        )

    def arrangement_for_contents_of_model(self,
                                          checked_dir_contents: List[FileSystemElement],
                                          files_matcher_symbol_value: FilesMatcherSdv,
                                          additional_symbols: Optional[Mapping[str, SymbolDependentValue]] = None,
                                          ) -> Arrangement:
        symbols = {
            self.files_matcher_name:
                files_matcher_symbol_value
        }
        if additional_symbols:
            symbols.update(additional_symbols)

        return arrangement_w_tcds(
            tcds_contents=self._dir_arg_helper.tcds_populator_for_dir_with_contents(
                checked_dir_contents
            ),
            symbols=symbol_utils.symbol_table_from_name_and_sdv_mapping(symbols)
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
