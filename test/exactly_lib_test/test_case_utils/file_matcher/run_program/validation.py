import unittest

from exactly_lib.symbol.data import string_sdvs
from exactly_lib.test_case_utils.string_transformer.sdvs import StringTransformerSdvReference
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTrace
from exactly_lib.type_system.logic.matching_result import MatchingResult
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.symbol.test_resources.program import ProgramSymbolContext, is_reference_to_program
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolContext
from exactly_lib_test.test_case_utils.file_matcher.test_resources import argument_building as args
from exactly_lib_test.test_case_utils.file_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.logic.test_resources.integration_check import ParseExpectation
from exactly_lib_test.test_case_utils.logic.test_resources.integration_check import PrimAndExeExpectation, Arrangement, \
    arrangement_wo_tcds
from exactly_lib_test.test_case_utils.program.test_resources import arguments_building as program_args
from exactly_lib_test.test_case_utils.program.test_resources import program_sdvs
from exactly_lib_test.test_case_utils.string_transformers.test_resources import \
    validation_cases as str_trans_validation_cases
from exactly_lib_test.test_resources.test_utils import NExArr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestValidation()
    ])


class TestValidation(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        program_symbol_name = 'PROGRAM_SYMBOL'
        transformer_symbol_name = 'TRANSFORMER_SYMBOL'

        # ACT && ASSERT #

        integration_check.CHECKER.check_multi(
            self,
            args.RunProgram(
                program_args.symbol_ref_command_elements(program_symbol_name)
            ).as_arguments,
            ParseExpectation(
                source=asrt_source.source_is_at_end,
                symbol_references=asrt.matches_sequence([
                    is_reference_to_program(program_symbol_name),
                ]),
            ),
            integration_check.ARBITRARY_MODEL,
            [
                validation_exe_case(validation_case,
                                    program_symbol_name)
                for validation_case in str_trans_validation_cases.failing_validation_cases(transformer_symbol_name)
            ],
        )


def validation_exe_case(validation_case: NameAndValue[str_trans_validation_cases.ValidationCase],
                        program_symbol_name: str,
                        ) -> NExArr[PrimAndExeExpectation[MatcherWTrace[FileMatcherModel], MatchingResult],
                                    Arrangement]:
    program_w_transformer = program_sdvs.with_ref_to_program(
        string_sdvs.str_constant('system-program')
    ).new_with_appended_transformations([
        StringTransformerSdvReference(validation_case.value.symbol_context.name)
    ])

    program_symbol = ProgramSymbolContext.of_sdv(
        program_symbol_name,
        program_w_transformer
    )
    return NExArr(
        validation_case.name,
        PrimAndExeExpectation.of_exe(
            validation=validation_case.value.expectation,
        ),
        arrangement_wo_tcds(
            symbols=SymbolContext.symbol_table_of_contexts([
                program_symbol,
                validation_case.value.symbol_context,
            ]),
        )
    )
