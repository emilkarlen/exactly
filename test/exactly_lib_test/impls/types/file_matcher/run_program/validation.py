import unittest

from exactly_lib_test.impls.types.file_matcher.test_resources import argument_building as args
from exactly_lib_test.impls.types.file_matcher.test_resources import integration_check
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import ParseExpectation
from exactly_lib_test.impls.types.program.test_resources import arguments_building as program_args
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.types.program.test_resources import validation_cases
from exactly_lib_test.type_val_deps.types.program.test_resources.references import is_reference_to_program


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestValidation()
    ])


class TestValidation(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        program_symbol_name = 'PROGRAM_SYMBOL'

        # ACT && ASSERT #

        integration_check.CHECKER__PARSE_FULL.check_multi(
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
                validation_cases.validation_exe_case(validation_case)
                for validation_case in validation_cases.failing_validation_cases(program_symbol_name,
                                                                                 'TRANSFORMER_SYMBOL')
            ],
        )
