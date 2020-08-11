import unittest
from contextlib import contextmanager
from typing import List, ContextManager

from exactly_lib.actors.program import actor as sut
from exactly_lib.test_case.actor import ParseException
from exactly_lib.util.str_.misc_formatting import lines_content
from exactly_lib_test.actors.program.test_resources import ConfigurationWithPythonProgramBase, \
    valid_source_variants, tmp_dir_in_path_with_files, invalid_source_variants
from exactly_lib_test.actors.test_resources import integration_check
from exactly_lib_test.actors.test_resources.action_to_check import suite_for_execution, TestCaseSourceSetup
from exactly_lib_test.actors.test_resources.integration_check import Arrangement, Expectation
from exactly_lib_test.execution.test_resources import eh_assertions as asrt_eh
from exactly_lib_test.symbol.test_resources.string import StringConstantSymbolContext
from exactly_lib_test.test_case.result.test_resources import svh_assertions as asrt_svh
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_case.test_resources.arrangements import ProcessExecutionArrangement
from exactly_lib_test.test_case_utils.program.test_resources import arguments_building as args
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.file_structure import DirContents
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.process_execution.test_resources.proc_exe_env import proc_exe_env_for_test
from exactly_lib_test.util.test_resources import py_program


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    configuration = TheConfiguration()

    ret_val.addTest(TestInvalidSyntax())
    ret_val.addTest(TestHardErrorWhenInvalidProgram())
    ret_val.addTest(TestSymbolReferencesAndSourceVariants())
    ret_val.addTest(suite_for_execution(configuration))

    return ret_val


class TheConfiguration(ConfigurationWithPythonProgramBase):
    @contextmanager
    def _instructions_for_executing_py_source(self, py_src: List[str]) -> ContextManager[TestCaseSourceSetup]:
        exe_file_in_path = fs.python_executable_file('the-program',
                                                     lines_content(py_src))
        with tmp_dir_in_path_with_files(DirContents([exe_file_in_path])) as environ:
            program_line = args.system_program_command_line(exe_file_in_path.name).as_str

            yield TestCaseSourceSetup(
                act_phase_instructions=[instr([program_line])],
                environ=environ
            )


class TestInvalidSyntax(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        valid_program_line = args.system_program_command_line('system-program').as_str
        # ACT & ASSERT #
        for case in invalid_source_variants(valid_program_line):
            with self.subTest(case.name):
                with self.assertRaises(ParseException) as ctx:
                    sut.actor().parse(case.value)

                asrt_svh.is_validation_error().apply_with_message(
                    self,
                    ctx.exception.cause,
                    'error info'
                )


class TestHardErrorWhenInvalidProgram(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        program_line = args.system_program_command_line('non-existing-system-program').as_str
        # ACT & ASSERT #
        integration_check.check_execution(
            self,
            sut.actor(),
            [instr([program_line])],
            Arrangement(),
            Expectation.hard_error_from_execute(),
        )


class TestSymbolReferencesAndSourceVariants(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        exit_code_from_program = 0
        exe_file_in_path = fs.python_executable_file(
            'the-program',
            lines_content(py_program.exit_with_code(exit_code_from_program)),
        )
        program_symbol = StringConstantSymbolContext(
            'PROGRAM_NAME_SYMBOL',
            exe_file_in_path.name,
        )
        program_line = args.system_program_command_line(program_symbol.name__sym_ref_syntax).as_str

        with tmp_dir_in_path_with_files(DirContents([exe_file_in_path])) as environ:
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
                            )
                        ),
                        Expectation(
                            symbol_usages=asrt.matches_singleton_sequence(
                                program_symbol.reference_assertion__string_made_up_of_just_strings
                            ),
                            execute=asrt_eh.is_exit_code(exit_code_from_program)
                        ),
                    )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())