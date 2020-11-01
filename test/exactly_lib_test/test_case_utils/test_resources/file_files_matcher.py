from abc import ABC
from typing import Sequence, List

from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.type_val_deps.types.files_matcher import FilesMatcherSdv
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_case_utils.files_matcher.test_resources import arguments_building as fms_args
from exactly_lib_test.test_case_utils.files_matcher.test_resources.arguments_building import FilesMatcherArg
from exactly_lib_test.test_case_utils.files_matcher.test_resources.symbol_context import FilesMatcherSymbolContext
from exactly_lib_test.test_case_utils.logic.test_resources.intgr_arr_exp import Arrangement, arrangement_w_tcds, \
    ParseExpectation, ExecutionExpectation, Expectation
from exactly_lib_test.test_case_utils.test_resources.dir_arg_helper import DirArgumentHelper
from exactly_lib_test.test_resources.files.file_structure import FileSystemElement
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_val_deps.types.test_resources.files_matcher import is_reference_to_files_matcher


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
        return is_reference_to_files_matcher(self.files_matcher_name)

    def symbol_references_expectation(self) -> ValueAssertion[Sequence[SymbolReference]]:
        return asrt.matches_singleton_sequence(
            self.symbol_reference_assertion
        )

    def arrangement_for_contents_of_model(self,
                                          checked_dir_contents: List[FileSystemElement],
                                          files_matcher_symbol_value: FilesMatcherSdv,
                                          additional_symbols: Sequence[SymbolContext] = (),
                                          ) -> Arrangement:
        symbols = [
            FilesMatcherSymbolContext.of_sdv(self.files_matcher_name,
                                             files_matcher_symbol_value)
        ]
        symbols += additional_symbols

        return arrangement_w_tcds(
            tcds_contents=self._dir_arg_helper.tcds_populator_for_dir_with_contents(
                checked_dir_contents
            ),
            symbols=SymbolContext.symbol_table_of_contexts(symbols)
        )

    def parse_expectation_of_symbol_references(self) -> ParseExpectation:
        return ParseExpectation(
            symbol_references=self.symbol_references_expectation()
        )

    def expectation(self, execution: ExecutionExpectation) -> Expectation:
        return Expectation(
            ParseExpectation(
                symbol_references=asrt.matches_singleton_sequence(
                    is_reference_to_files_matcher(self.files_matcher_name)
                ),
            ),
            execution
        )
