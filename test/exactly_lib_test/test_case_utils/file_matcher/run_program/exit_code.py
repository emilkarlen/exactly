import unittest

from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.symbol.data.test_resources.symbol_reference_assertions import is_reference_to_data_type_symbol
from exactly_lib_test.symbol.test_resources.program import ProgramSymbolContext
from exactly_lib_test.symbol.test_resources.string import StringIntConstantSymbolContext
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolContext
from exactly_lib_test.test_case_utils.file_matcher.run_program.test_resources import is_result_for_py_interpreter
from exactly_lib_test.test_case_utils.file_matcher.test_resources import argument_building as args
from exactly_lib_test.test_case_utils.file_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.logic.test_resources.integration_check import PrimAndExeExpectation
from exactly_lib_test.test_case_utils.logic.test_resources.integration_check import arrangement_w_tcds, \
    ParseExpectation
from exactly_lib_test.test_case_utils.program.test_resources import arguments_building as program_args
from exactly_lib_test.test_case_utils.program.test_resources import program_sdvs
from exactly_lib_test.test_case_utils.test_resources import relativity_options as rel_opt
from exactly_lib_test.test_resources.files.file_structure import File, DirContents
from exactly_lib_test.test_resources.programs import py_programs
from exactly_lib_test.test_resources.test_utils import NExArr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def test_result_SHOULD_be_true_iff_exit_code_is_0(self):
        # ARRANGE #

        py_file = File('exit-with-value-on-command-line.py',
                       py_programs.py_pgm_that_exits_with_1st_value_on_command_line(''))

        py_file_rel_opt_conf = rel_opt.conf_rel_any(RelOptionType.REL_TMP)
        py_file_conf = py_file_rel_opt_conf.named_file_conf(py_file.name)

        program_symbol = ProgramSymbolContext.of_sdv(
            'PROGRAM_THAT_EXECUTES_PY_FILE',
            program_sdvs.interpret_py_source_file_that_must_exist(py_file_conf.path_sdv)
        )
        exit_code_symbol_name = 'EXIT_CODE_SYMBOL'
        exit_code_cases = [0, 1, 3, 69, 72]

        # ACT && ASSERT #

        integration_check.CHECKER.check_multi(
            self,
            args.RunProgram(
                program_args.symbol_ref_command_elements(
                    program_symbol.name,
                    arguments=[symbol_reference_syntax_for_name(exit_code_symbol_name)],
                )
            ).as_arguments,
            ParseExpectation(
                source=asrt_source.source_is_at_end,
                symbol_references=asrt.matches_sequence([
                    program_symbol.reference_assertion,
                    is_reference_to_data_type_symbol(exit_code_symbol_name),
                ]),
            ),
            integration_check.ARBITRARY_MODEL,
            [
                NExArr(
                    'Exit code {}'.format(exit_code),
                    PrimAndExeExpectation.of_exe(
                        main_result=is_result_for_py_interpreter(exit_code)
                    ),
                    arrangement_w_tcds(
                        tcds_contents=py_file_rel_opt_conf.populator_for_relativity_option_root(
                            DirContents([py_file])
                        ),
                        symbols=SymbolContext.symbol_table_of_contexts([
                            program_symbol,
                            StringIntConstantSymbolContext(exit_code_symbol_name, exit_code)
                        ]),
                    )
                )
                for exit_code in exit_code_cases
            ],
        )
