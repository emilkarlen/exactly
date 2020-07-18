import unittest

from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.symbol.test_resources.program import is_reference_to_program
from exactly_lib_test.test_case_utils.file_matcher.test_resources import argument_building as args
from exactly_lib_test.test_case_utils.file_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.logic.test_resources.integration_check import ParseExpectation
from exactly_lib_test.test_case_utils.program.test_resources import arguments_building as program_args
from exactly_lib_test.test_case_utils.program.test_resources import validation_cases
from exactly_lib_test.test_case_utils.string_transformers.test_resources import \
    validation_cases as str_trans_validation_cases
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
                source=asrt_source.is_at_end_of_line(1),
                symbol_references=asrt.matches_sequence([
                    is_reference_to_program(program_symbol_name),
                ]),
            ),
            integration_check.ARBITRARY_MODEL,
            [
                validation_cases.validation_exe_case(
                    validation_case,
                    program_symbol_name,
                )
                for validation_case in str_trans_validation_cases.failing_validation_cases(transformer_symbol_name)
            ],
        )
