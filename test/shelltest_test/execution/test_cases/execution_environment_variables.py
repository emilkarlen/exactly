__author__ = 'emil'

import os
import unittest

from shelltest import phases
from shelltest.exec_abs_syn import abs_syn_gen, script_stmt_gen
from shelltest.exec_abs_syn.config import Configuration
from shelltest.execution import execution
from shelltest.phase_instr import line_source
from shelltest_test.execution.util import python_code_gen as py
from shelltest_test.execution.util.py_unit_test_case_with_file_output import \
    UnitTestCaseForPyLanguageThatWritesAFileToTestRootForEachPhase, \
    PyCommandThatWritesToStandardPhaseFile, \
    standard_phase_file_path
from shelltest_test.execution.util.utils import format_header_value_line, un_lines


class TestEnvironmentVariablesShouldBeAccessibleInEveryPhase(
    UnitTestCaseForPyLanguageThatWritesAFileToTestRootForEachPhase):
    def __init__(self,
                 unittest_case: unittest.TestCase,
                 dbg_do_not_delete_dir_structure=False):
        super().__init__(unittest_case, dbg_do_not_delete_dir_structure)

    def _phase_env_for_py_cmd_phase(self, phase: phases.Phase) -> abs_syn_gen.PhaseEnvironmentForPythonCommands:
        return \
            abs_syn_gen.PhaseEnvironmentForPythonCommands([
                PyCommandThatWritesEnvironmentVariablesToStandardPhaseStandardPhaseFile(
                    self._next_line(),
                    phase)
            ])

    def _phase_env_apply(self) -> abs_syn_gen.PhaseEnvironmentForScriptGeneration:
        return \
            abs_syn_gen.PhaseEnvironmentForScriptGeneration([
                StatementsGeneratorThatWritesEnvironmentVariablesToStandardPhaseFile(
                    self._next_line(),
                    phases.APPLY)
            ])

    def _expected_content_for(self, phase: phases.Phase) -> str:
        return un_lines([
            format_header_value_line(execution.ENV_VAR_HOME, str(self.test_case_execution.home_dir)),
            format_header_value_line(execution.ENV_VAR_TEST, str(self.eds.test_root_dir))
        ])


class PyCommandThatWritesEnvironmentVariablesToStandardPhaseStandardPhaseFile(PyCommandThatWritesToStandardPhaseFile):
    def __init__(self,
                 source_line: line_source.Line,
                 phase: phases.Phase):
        super().__init__(source_line, phase)

    def file_lines(self, configuration) -> list:
        def format_environment_variable(var_name: str) -> str:
            return format_header_value_line(var_name, os.environ[var_name])

        return [format_environment_variable(var_name) for var_name in execution.ALL_ENV_VARS]


class StatementsGeneratorThatWritesEnvironmentVariablesToStandardPhaseFile(
    script_stmt_gen.StatementsGeneratorForInstruction):
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
        print_env_stmts = [py.print_header_value(py.string_expr(env_var),
                                                 py.env_var_expr(env_var),
                                                 file_var)
                           for env_var in execution.ALL_ENV_VARS]
        open_file_and_print_stmts = py.with_opened_file(file_name, file_var, 'w', print_env_stmts)
        statements = ['import os'] + \
                     open_file_and_print_stmts

        # print(os.linesep.join(statements))

        return script_language.raw_script_statements(statements)