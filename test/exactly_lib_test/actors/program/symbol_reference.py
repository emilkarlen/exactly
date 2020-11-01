import unittest
from contextlib import contextmanager
from typing import List, ContextManager

from exactly_lib.actors.program import actor as sut
from exactly_lib.tcfs.path_relativity import RelOptionType, RelHdsOptionType
from exactly_lib.test_case.actor import ParseException
from exactly_lib.type_val_deps.types.path import path_sdvs
from exactly_lib.type_val_deps.types.string import string_sdvs
from exactly_lib.util.str_.misc_formatting import lines_content
from exactly_lib_test.actors.program.test_resources import ConfigurationWithPythonProgramBase, \
    valid_source_variants, tmp_dir_in_path_with_files, invalid_source_variants
from exactly_lib_test.actors.test_resources import integration_check
from exactly_lib_test.actors.test_resources.action_to_check import suite_for_execution, TestCaseSourceSetup
from exactly_lib_test.actors.test_resources.integration_check import Arrangement, Expectation
from exactly_lib_test.actors.test_resources.validation_pre_or_post_sds import VALIDATION_CASES
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.execution.test_resources import eh_assertions as asrt_eh
from exactly_lib_test.tcfs.test_resources import hds_populators
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_case.test_resources.arrangements import ProcessExecutionArrangement
from exactly_lib_test.test_case_utils.program.test_resources import arguments_building as args
from exactly_lib_test.test_case_utils.program.test_resources import program_sdvs
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.file_structure import DirContents
from exactly_lib_test.type_val_deps.types.test_resources.program import ProgramSymbolContext
from exactly_lib_test.util.process_execution.test_resources.proc_exe_env import proc_exe_env_for_test
from exactly_lib_test.util.test_resources import py_program


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    configuration = TheConfiguration()

    ret_val.addTest(TestInvalidSyntax())
    ret_val.addTest(TestFailingValidation())
    ret_val.addTest(TestHardErrorWhenInvalidProgram())
    ret_val.addTest(TestSourceVariants())
    ret_val.addTest(suite_for_execution(configuration))

    return ret_val


class TheConfiguration(ConfigurationWithPythonProgramBase):
    @contextmanager
    def _instructions_for_executing_py_source(self, py_src: List[str]) -> ContextManager[TestCaseSourceSetup]:
        py_file = fs.File('the-program.py',
                          lines_content(py_src))
        symbol = ProgramSymbolContext.of_sdv(
            'PROGRAM_SYMBOL',
            program_sdvs.interpret_py_source_file_that_must_exist(
                path_sdvs.of_rel_option_with_const_file_name(
                    RelOptionType.REL_HDS_ACT,
                    py_file.name,
                )
            )
        )
        program_line = args.symbol_ref_command_line(symbol.name).as_str
        yield TestCaseSourceSetup(
            act_phase_instructions=[instr([program_line])],
            home_act_dir_contents=DirContents([py_file]),
            symbols=symbol.symbol_table,
            symbol_usages=symbol.usages_assertion
        )


class TestInvalidSyntax(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        valid_program_line = args.symbol_ref_command_line('PROGRAM_SYMBOL').as_str
        # ACT & ASSERT #
        for case in invalid_source_variants(valid_program_line):
            with self.subTest(case.name):
                with self.assertRaises(ParseException) as ctx:
                    sut.actor().parse(case.value)

                asrt_text_doc.is_any_text().apply_with_message(
                    self,
                    ctx.exception.cause,
                    'error info'
                )


class TestFailingValidation(unittest.TestCase):
    def runTest(self):
        for case in VALIDATION_CASES:
            with self.subTest(case.name):
                program_sdv = program_sdvs.ref_to_exe_file(
                    path_sdvs.of_rel_option_with_const_file_name(case.path_relativity, 'non-existing')
                )
                program_symbol = ProgramSymbolContext.of_sdv(
                    'PROGRAM_SYMBOL',
                    program_sdv
                )
                integration_check.check_execution(
                    self,
                    sut.actor(),
                    [instr([args.symbol_ref_command_line(program_symbol.name).as_str])],
                    Arrangement(
                        symbol_table=program_symbol.symbol_table,
                    ),
                    Expectation(
                        symbol_usages=program_symbol.usages_assertion,
                        validation=case.expectation
                    ),
                )


class TestHardErrorWhenInvalidProgram(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        symbol = ProgramSymbolContext.of_sdv(
            'PROGRAM_SYMBOL',
            program_sdvs.system_program(
                string_sdvs.str_constant('non-existing-system-program')
            )
        )
        program_line = args.symbol_ref_command_line(symbol.name).as_str
        # ACT & ASSERT #
        integration_check.check_execution(
            self,
            sut.actor(),
            [instr([program_line])],
            Arrangement(
                symbol_table=symbol.symbol_table
            ),
            Expectation.hard_error_from_execute(
                symbol_usages=symbol.usages_assertion
            ),
        )


class TestSourceVariants(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        exit_code_from_program = 0
        py_file = fs.File(
            'the-program',
            lines_content(py_program.exit_with_code(exit_code_from_program)),
        )
        program_symbol = ProgramSymbolContext.of_sdv(
            'PROGRAM_SYMBOL',
            program_sdvs.interpret_py_source_file_that_must_exist(
                path_sdvs.of_rel_option_with_const_file_name(
                    RelOptionType.REL_HDS_CASE,
                    py_file.name,
                )
            )
        )
        program_line = args.symbol_ref_command_line(program_symbol.name).as_str

        with tmp_dir_in_path_with_files(DirContents([py_file])) as environ:
            for source_case in valid_source_variants(program_line):
                with self.subTest(source_case.name):
                    # ACT & ASSERT #
                    integration_check.check_execution(
                        self,
                        sut.actor(),
                        [instr([program_line])],
                        Arrangement(
                            symbol_table=program_symbol.symbol_table,
                            process_execution=ProcessExecutionArrangement(
                                process_execution_settings=proc_exe_env_for_test(
                                    environ=environ
                                )
                            ),
                            hds_contents=hds_populators.contents_in(
                                RelHdsOptionType.REL_HDS_CASE,
                                DirContents([py_file])
                            ),
                        ),
                        Expectation(
                            symbol_usages=program_symbol.usages_assertion,
                            execute=asrt_eh.is_exit_code(exit_code_from_program)
                        ),
                    )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
