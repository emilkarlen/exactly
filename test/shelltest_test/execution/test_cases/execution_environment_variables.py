__author__ = 'emil'

import os
import unittest

from shelltest import phases
from shelltest.exec_abs_syn import instructions
from shelltest.execution import execution
from shelltest_test.execution.util import python_code_gen as py
from shelltest_test.execution.util.py_unit_test_case_with_file_output import \
    ModulesAndStatements, UnitTestCaseForPyLanguageThatWritesAFileToTestRootForEachPhase2, \
    InternalInstructionThatWritesToStandardPhaseFile, ActPhaseInstructionThatWritesToStandardPhaseFile
from shelltest_test.execution.util.utils import format_header_value_line, un_lines


class TestCase(UnitTestCaseForPyLanguageThatWritesAFileToTestRootForEachPhase2):
    def __init__(self,
                 unittest_case: unittest.TestCase,
                 dbg_do_not_delete_dir_structure=False):
        super().__init__(unittest_case, dbg_do_not_delete_dir_structure)

    def _default_instructions_for_setup_assert_cleanup(self, phase: phases.Phase) -> list:
        return [
            InternalInstructionThatWritesEnvironmentVariables(phase)
        ]

    def _act_phase(self) -> list:
        return [
            self._next_instruction_line(ActPhaseInstructionThatWritesEnvironmentVariables(phases.ACT))
        ]

    def _expected_content_for(self, phase: phases.Phase) -> str:
        return un_lines([
            format_header_value_line(execution.ENV_VAR_HOME, str(self.test_case_execution.configuration.home_dir)),
            format_header_value_line(execution.ENV_VAR_TEST, str(self.eds.test_root_dir))
        ])


class InternalInstructionThatWritesEnvironmentVariables(InternalInstructionThatWritesToStandardPhaseFile):
    def __init__(self,
                 phase: phases.Phase):
        super().__init__(phase)

    def _file_lines(self, global_environment: instructions.GlobalEnvironmentForNamedPhase) -> list:
        def format_environment_variable(var_name: str) -> str:
            return format_header_value_line(var_name, os.environ[var_name])

        return [format_environment_variable(var_name) for var_name in execution.ALL_ENV_VARS]


class ActPhaseInstructionThatWritesEnvironmentVariables(ActPhaseInstructionThatWritesToStandardPhaseFile):
    def __init__(self,
                 phase: phases.Phase):
        super().__init__(phase)
        self.__phase = phase

    def code_using_file_opened_for_writing(self,
                                           file_variable: str) -> ModulesAndStatements:
        print_env_statements = [py.print_header_value(py.string_expr(env_var),
                                                      py.env_var_expr(env_var),
                                                      file_variable)
                                for env_var in execution.ALL_ENV_VARS]
        return ModulesAndStatements({'os'},
                                    print_env_statements)
