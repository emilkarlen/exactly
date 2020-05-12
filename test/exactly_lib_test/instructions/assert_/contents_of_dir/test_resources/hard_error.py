from abc import ABC
from typing import Sequence

from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.common.test_resources.text_doc_assertions import is_string_for_test_that_equals
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import ExecutionExpectation, Expectation
from exactly_lib_test.symbol.test_resources.arguments_building import SymbolReferenceArgument
from exactly_lib_test.symbol.test_resources.files_matcher import is_reference_to_files_matcher
from exactly_lib_test.test_case.result.test_resources import pfh_assertions as asrt_pfh
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct2, ArrangementPostAct
from exactly_lib_test.test_case_file_structure.test_resources.arguments_building import PathArgument, RelOptPathArgument
from exactly_lib_test.test_case_file_structure.test_resources.ds_construction import TcdsArrangementPostAct
from exactly_lib_test.test_case_file_structure.test_resources.tcds_populators import TcdsPopulatorForRelOptionType
from exactly_lib_test.test_case_utils.file_matcher.contents_of_dir.test_resources import invalid_model
from exactly_lib_test.test_case_utils.files_matcher.test_resources.symbol_context import FilesMatcherSymbolContext
from exactly_lib_test.test_case_utils.matcher.test_resources import matchers
from exactly_lib_test.test_resources.arguments_building import ArgumentElementsRenderer
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_dir
from exactly_lib_test.test_resources.test_utils import NExArr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class _HelperBase(ABC):
    def __init__(self,
                 name_of_referenced_symbol: str = 'FILES_MATCHER_SYMBOL',
                 error_message: str = 'the error message',
                 checked_file_name: str = 'actual-dir',
                 checked_file_location: RelOptionType = RelOptionType.REL_TMP,
                 ):
        self.name_of_referenced_symbol = name_of_referenced_symbol
        self.error_message = error_message
        self.checked_file_name = checked_file_name
        self.checked_file_location = checked_file_location

    def path_argument(self) -> PathArgument:
        return RelOptPathArgument(self.checked_file_name,
                                  self.checked_file_location)

    def files_matcher_reference_argument(self) -> ArgumentElementsRenderer:
        return SymbolReferenceArgument(self.name_of_referenced_symbol)

    def expected_symbol_usages(self) -> ValueAssertion[Sequence[SymbolUsage]]:
        return asrt.matches_singleton_sequence(
            is_reference_to_files_matcher(self.name_of_referenced_symbol)
        )


class HardErrorDueToInvalidPathArgumentHelper(_HelperBase):
    UNCONDITIONALLY_CONSTANT_TRUE = matchers.sdv_from_bool(True)

    def symbols(self) -> SymbolTable:
        return FilesMatcherSymbolContext.of_primitive_constant(self.name_of_referenced_symbol,
                                                               True
                                                               ).symbol_table

    def expectation(self) -> ExecutionExpectation:
        return ExecutionExpectation(
            main_result=asrt_pfh.is_hard_error__with_arbitrary_message(),
        )

    def _arrangement(self, tcds: TcdsArrangementPostAct) -> ArrangementPostAct2:
        return ArrangementPostAct2(
            symbols=self.symbols(),
            tcds=tcds,
        )

    def execution_cases(self) -> Sequence[NExArr[ExecutionExpectation, ArrangementPostAct2]]:
        return [
            NExArr(
                case.name,
                self.expectation(),
                self._arrangement(
                    TcdsArrangementPostAct(
                        tcds_contents=TcdsPopulatorForRelOptionType(
                            self.checked_file_location,
                            case.value,
                        )
                    ),
                )
            )
            for case in invalid_model.cases(self.checked_file_name)
        ]


class HardErrorDueToHardErrorFromFilesMatcherHelper(_HelperBase):
    def arrangement(self) -> ArrangementPostAct:
        return ArrangementPostAct(
            tcds_contents=TcdsPopulatorForRelOptionType(
                self.checked_file_location,
                DirContents([empty_dir(self.checked_file_name)])
            ),
            symbols=FilesMatcherSymbolContext.of_primitive(
                self.name_of_referenced_symbol,
                matchers.MatcherThatReportsHardError(self.error_message)
            ).symbol_table,
        )

    def expectation(self) -> Expectation:
        return Expectation(
            symbol_usages=asrt.matches_singleton_sequence(
                is_reference_to_files_matcher(self.name_of_referenced_symbol)
            ),
            main_result=asrt_pfh.is_hard_error(
                is_string_for_test_that_equals(self.error_message)
            ),
        )
