import unittest

from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import ParseExpectation
from exactly_lib_test.impls.types.matcher.test_resources.run_program import test_cases
from exactly_lib_test.impls.types.program.test_resources import arguments_building as program_args
from exactly_lib_test.impls.types.string_matcher.test_resources import arguments_building2 as args
from exactly_lib_test.impls.types.string_matcher.test_resources import integration_check
from exactly_lib_test.impls.types.string_model.test_resources import model_constructor
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.data.test_resources.symbol_reference_assertions import \
    is_reference_to_data_type_symbol
from exactly_lib_test.type_val_deps.types.test_resources.program import is_reference_to_program


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def test_result_SHOULD_be_true_iff_exit_code_is_0(self):
        # ARRANGE #
        program_symbol_name = 'PROGRAM_THAT_EXECUTES_PY_FILE'
        exit_code_symbol_name = 'EXIT_CODE_SYMBOL'

        # ACT && ASSERT #

        integration_check.CHECKER__PARSE_FULL.check_multi(
            self,
            args.RunProgram(
                program_args.symbol_ref_command_elements(
                    program_symbol_name,
                    arguments=[symbol_reference_syntax_for_name(exit_code_symbol_name)],
                )
            ).as_arguments,
            ParseExpectation(
                source=asrt_source.is_at_end_of_line(1),
                symbol_references=asrt.matches_sequence([
                    is_reference_to_program(program_symbol_name),
                    is_reference_to_data_type_symbol(exit_code_symbol_name),
                ]),
            ),
            model_constructor.arbitrary(self),
            test_cases.exit_code_exe_cases(
                program_symbol_name,
                exit_code_symbol_name,
            ),
        )
