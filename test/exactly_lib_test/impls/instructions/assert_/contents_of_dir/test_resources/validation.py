from typing import Sequence

from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.impls.instructions.assert_.test_resources.instruction_check import ExecutionExpectation
from exactly_lib_test.impls.types.matcher.test_resources import sdv_ddv
from exactly_lib_test.symbol.test_resources.arguments_building import SymbolReferenceArgument
from exactly_lib_test.tcfs.test_resources import path_arguments as args
from exactly_lib_test.tcfs.test_resources.path_arguments import PathArgument
from exactly_lib_test.test_case.result.test_resources import svh_assertions as asrt_svh, pfh_assertions as asrt_pfh
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct2
from exactly_lib_test.test_resources.argument_renderer import ArgumentElementsRenderer
from exactly_lib_test.test_resources.test_utils import NExArr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.dep_variants.ddv.test_resources.ddv_validators import DdvValidatorThat
from exactly_lib_test.type_val_deps.types.files_matcher.test_resources.references import \
    is_reference_to_files_matcher__usage
from exactly_lib_test.type_val_deps.types.files_matcher.test_resources.symbol_context import FilesMatcherSymbolContext


class ValidationHelper:
    def __init__(self,
                 name_of_referenced_symbol: str = 'FILES_MATCHER_SYMBOL',
                 err_msg_from_validator: str = 'error from validator',
                 checked_dir_name: str = 'actual-dir',
                 ):
        self.name_of_referenced_symbol = name_of_referenced_symbol
        self.err_msg_from_validator = err_msg_from_validator
        self.checked_dir_name = checked_dir_name

    def path_argument(self) -> PathArgument:
        return args.path_argument(self.checked_dir_name)

    def files_matcher_reference_argument(self) -> ArgumentElementsRenderer:
        return SymbolReferenceArgument(self.name_of_referenced_symbol)

    def expected_symbol_usages(self) -> Assertion[Sequence[SymbolUsage]]:
        return asrt.matches_singleton_sequence(
            is_reference_to_files_matcher__usage(self.name_of_referenced_symbol)
        )

    def _arrangement(self, validator: DdvValidator) -> ArrangementPostAct2:
        return ArrangementPostAct2(
            symbols=FilesMatcherSymbolContext.of_sdv(
                self.name_of_referenced_symbol,
                sdv_ddv.sdv_from_bool(
                    unconditional_result=True,
                    validator=validator,
                )).symbol_table,
        )

    def execution_cases(self) -> Sequence[NExArr[ExecutionExpectation, ArrangementPostAct2]]:
        return [
            NExArr('pre sds validation',
                   ExecutionExpectation(
                       validation_pre_sds=asrt_svh.is_validation_error(
                           asrt_text_doc.is_string_for_test_that_equals(self.err_msg_from_validator)
                       ),
                   ),
                   self._arrangement(
                       DdvValidatorThat(
                           pre_sds_return_value=asrt_text_doc.new_single_string_text_for_test(
                               self.err_msg_from_validator)
                       ))
                   ),
            NExArr('post sds validation',
                   ExecutionExpectation(
                       main_result=asrt_pfh.is_hard_error(
                           asrt_text_doc.is_string_for_test_that_equals(self.err_msg_from_validator)
                       ),
                   ),
                   self._arrangement(
                       DdvValidatorThat(
                           post_setup_return_value=asrt_text_doc.new_single_string_text_for_test(
                               self.err_msg_from_validator)
                       )
                   )
                   ),
        ]
