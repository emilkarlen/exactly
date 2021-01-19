import unittest

from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import MultiSourceExpectation
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__for_consume_until_end_of_last_line__s__nsc
from exactly_lib_test.impls.types.program.parse_program.test_resources import pgm_and_args_cases
from exactly_lib_test.impls.types.program.parse_program.test_resources.integration_checker import CHECKER_WO_EXECUTION
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_prims.program.test_resources import command_assertions as asrt_command, \
    program_assertions as asrt_pgm_val


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([TestPlainForms()])


class TestPlainForms(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        for pgm_and_args_case in pgm_and_args_cases.cases_w_and_wo_argument_list__including_program_reference():
            with self.subTest(command=pgm_and_args_case.name):
                # ACT & ASSERT #
                CHECKER_WO_EXECUTION.check__abs_stx__std_layouts__mk_source_variants__wo_input(
                    self,
                    equivalent_source_variants__for_consume_until_end_of_last_line__s__nsc,
                    pgm_and_args_case.pgm_and_args,
                    pgm_and_args_case.mk_arrangement(SymbolContext.symbol_table_of_contexts(pgm_and_args_case.symbols)),
                    MultiSourceExpectation(
                        symbol_references=SymbolContext.references_assertion_of_contexts(pgm_and_args_case.symbols),
                        primitive=lambda env: (
                            asrt_pgm_val.matches_program(
                                asrt_command.matches_command(
                                    driver=pgm_and_args_case.expected_command_driver(env),
                                    arguments=asrt.is_empty_sequence
                                ),
                                stdin=asrt_pgm_val.is_no_stdin(),
                                transformer=asrt_pgm_val.is_no_transformation(),
                            )
                        )
                    )
                )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
