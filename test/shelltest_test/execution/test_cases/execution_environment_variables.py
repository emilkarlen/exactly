__author__ = 'emil'

import os
import unittest

from shelltest import phases
from shelltest.exec_abs_syn import abs_syn_gen
from shelltest.execution import execution
from shelltest.phase_instr import line_source
from shelltest_test.execution.util import python_code_gen as py
from shelltest_test.execution.util.py_unit_test_case_with_file_output import \
    UnitTestCaseForPyLanguageThatWritesAFileToTestRootForEachPhase, \
    PyCommandThatWritesToStandardPhaseFile, \
    StatementsGeneratorThatWritesToStandardPhaseFile, \
    ModulesAndStatements
from shelltest_test.execution.util.utils import format_header_value_line, un_lines


class TestCase(UnitTestCaseForPyLanguageThatWritesAFileToTestRootForEachPhase):
    def __init__(self,
                 unittest_case: unittest.TestCase,
                 dbg_do_not_delete_dir_structure=False):
        super().__init__(unittest_case, dbg_do_not_delete_dir_structure)

    def _phase_env_for_py_cmd_phase(self, phase: phases.Phase) -> abs_syn_gen.PhaseEnvironmentForPythonCommands:
        return \
            abs_syn_gen.PhaseEnvironmentForPythonCommands([
                PyCommandThatWritesEnvironmentVariables(
                    self._next_line(),
                    phase)
            ])

    def _phase_env_apply(self) -> abs_syn_gen.PhaseEnvironmentForScriptGeneration:
        return \
            abs_syn_gen.PhaseEnvironmentForScriptGeneration([
                StatementsGeneratorThatWritesEnvironmentVariables(
                    self._next_line(),
                    phases.ACT)
            ])

    def _expected_content_for(self, phase: phases.Phase) -> str:
        return un_lines([
            format_header_value_line(execution.ENV_VAR_HOME, str(self.test_case_execution.home_dir)),
            format_header_value_line(execution.ENV_VAR_TEST, str(self.eds.test_root_dir))
        ])


class PyCommandThatWritesEnvironmentVariables(PyCommandThatWritesToStandardPhaseFile):
    def __init__(self,
                 source_line: line_source.Line,
                 phase: phases.Phase):
        super().__init__(source_line, phase)

    def file_lines(self, configuration) -> list:
        def format_environment_variable(var_name: str) -> str:
            return format_header_value_line(var_name, os.environ[var_name])

        return [format_environment_variable(var_name) for var_name in execution.ALL_ENV_VARS]


class StatementsGeneratorThatWritesEnvironmentVariables(StatementsGeneratorThatWritesToStandardPhaseFile):
    def __init__(self,
                 source_line: line_source.Line,
                 phase: phases.Phase):
        super().__init__(source_line, phase)
        self.__phase = phase

    def code_using_file_opened_for_writing(self,
                                           file_variable: str) -> ModulesAndStatements:
        print_env_statements = [py.print_header_value(py.string_expr(env_var),
                                                      py.env_var_expr(env_var),
                                                      file_variable)
                                for env_var in execution.ALL_ENV_VARS]
        return ModulesAndStatements({'os'},
                                    print_env_statements)
