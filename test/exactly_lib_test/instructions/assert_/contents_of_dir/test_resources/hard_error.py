from typing import Sequence

from exactly_lib.symbol.logic.files_matcher import FilesMatcherSdv
from exactly_lib.symbol.symbol_usage import SymbolUsage
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import ExecutionExpectation
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.symbol.test_resources.arguments_building import SymbolReferenceArgument
from exactly_lib_test.symbol.test_resources.files_matcher import is_reference_to_files_matcher
from exactly_lib_test.test_case.result.test_resources import pfh_assertions as asrt_pfh
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct2
from exactly_lib_test.test_case_file_structure.test_resources.arguments_building import PathArgument, RelOptPathArgument
from exactly_lib_test.test_case_file_structure.test_resources.ds_construction import TcdsArrangementPostAct
from exactly_lib_test.test_case_file_structure.test_resources.tcds_populators import TcdsPopulatorForRelOptionType
from exactly_lib_test.test_case_utils.file_matcher.contents_of_dir.test_resources import invalid_model
from exactly_lib_test.test_case_utils.matcher.test_resources import matchers
from exactly_lib_test.test_resources.arguments_building import ArgumentElementsRenderer
from exactly_lib_test.test_resources.test_utils import NExArr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class HardErrorHelper:
    UNCONDITIONALLY_CONSTANT_TRUE = FilesMatcherSdv(
        matchers.sdv_from_bool(True)
    )

    def __init__(self,
                 name_of_referenced_symbol: str = 'FILES_MATCHER_SYMBOL',
                 err_msg_from_validator: str = 'error from validator',
                 checked_file_name: str = 'actual-dir',
                 checked_file_location: RelOptionType = RelOptionType.REL_TMP,
                 ):
        self.name_of_referenced_symbol = name_of_referenced_symbol
        self.err_msg_from_validator = err_msg_from_validator
        self.checked_file_name = checked_file_name
        self.checked_file_location = checked_file_location
        self.symbols = symbol_utils.symbol_table_from_name_and_sdv_mapping({
            self.name_of_referenced_symbol: self.UNCONDITIONALLY_CONSTANT_TRUE
        })
        self.expectation = ExecutionExpectation(
            main_result=asrt_pfh.is_hard_error__with_arbitrary_message(),
        )

    def path_argument(self) -> PathArgument:
        return RelOptPathArgument(self.checked_file_name,
                                  self.checked_file_location)

    def files_matcher_reference_argument(self) -> ArgumentElementsRenderer:
        return SymbolReferenceArgument(self.name_of_referenced_symbol)

    def expected_symbol_usages(self) -> ValueAssertion[Sequence[SymbolUsage]]:
        return asrt.matches_singleton_sequence(
            is_reference_to_files_matcher(self.name_of_referenced_symbol)
        )

    def arrangement(self, tcds: TcdsArrangementPostAct) -> ArrangementPostAct2:
        return ArrangementPostAct2(
            symbols=self.symbols,
            tcds=tcds,
        )

    def execution_cases(self) -> Sequence[NExArr[ExecutionExpectation, ArrangementPostAct2]]:
        return [
            NExArr(
                case.name,
                self.expectation,
                self.arrangement(
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
