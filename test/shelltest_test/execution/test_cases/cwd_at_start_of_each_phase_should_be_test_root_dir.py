__author__ = 'emil'

import pathlib
import unittest

from shelltest import phases
from shelltest.exec_abs_syn import abs_syn_gen, script_stmt_gen
from shelltest.exec_abs_syn.config import Configuration
from shelltest.phase_instr import line_source
from shelltest_test.execution.util import python_code_gen as py
from shelltest_test.execution.util.py_unit_test_case_with_file_output import \
    UnitTestCaseForPyLanguageThatWritesAFileToTestRootForEachPhase, \
    PyCommandThatWritesToStandardPhaseFile, \
    standard_phase_file_path
from shelltest_test.execution.util.utils import un_lines


class TestCase(UnitTestCaseForPyLanguageThatWritesAFileToTestRootForEachPhase):
    def __init__(self,
                 unittest_case: unittest.TestCase,
                 dbg_do_not_delete_dir_structure=False):
        super().__init__(unittest_case, dbg_do_not_delete_dir_structure)

    def _phase_env_for_py_cmd_phase(self, phase: phases.Phase) -> abs_syn_gen.PhaseEnvironmentForPythonCommands:
        return \
            abs_syn_gen.PhaseEnvironmentForPythonCommands([
                PyCommandThatWritesCwdToStandardPhaseStandardPhaseFile(
                    self._next_line(),
                    phase)
            ])

    def _phase_env_apply(self) -> abs_syn_gen.PhaseEnvironmentForScriptGeneration:
        return \
            abs_syn_gen.PhaseEnvironmentForScriptGeneration([
                StatementsGeneratorThatWritesCwdToStandardPhaseFile(
                    self._next_line(),
                    phases.APPLY)
            ])

    def _expected_content_for(self, phase: phases.Phase) -> str:
        return un_lines([str(self.eds.test_root_dir)])


class PyCommandThatWritesCwdToStandardPhaseStandardPhaseFile(PyCommandThatWritesToStandardPhaseFile):
    def __init__(self,
                 source_line: line_source.Line,
                 phase: phases.Phase):
        super().__init__(source_line, phase)

    def file_lines(self, configuration) -> list:
        cwd_path = pathlib.Path().resolve()
        return [str(cwd_path)]


class StatementsGeneratorThatWritesCwdToStandardPhaseFile(script_stmt_gen.StatementsGeneratorForInstruction):
    def __init__(self,
                 source_line: line_source.Line,
                 phase: phases.Phase):
        super().__init__(source_line)
        self.__phase = phase

    def instruction_implementation(self,
                                   configuration: Configuration,
                                   script_language: script_stmt_gen.ScriptLanguage) -> list:
        file_path = standard_phase_file_path(configuration.test_root_dir, self.__phase)
        file_name = str(file_path)
        file_var = 'f'
        print_statements = [py.print_value('pathlib.Path().resolve()',
                                           file_var)]
        open_file_and_print_stmts = py.with_opened_file(file_name, file_var, 'w', print_statements)
        program = py.program_lines({'pathlib'},
                                   open_file_and_print_stmts)

        # print(os.linesep.join(statements))

        return script_language.raw_script_statements(program)