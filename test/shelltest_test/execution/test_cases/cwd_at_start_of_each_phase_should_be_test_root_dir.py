__author__ = 'emil'

import pathlib
import unittest

from shelltest import phases
from shelltest.exec_abs_syn import abs_syn_gen
from shelltest.phase_instr import line_source
from shelltest_test.execution.util import python_code_gen as py
from shelltest_test.execution.util.py_unit_test_case_with_file_output import \
    UnitTestCaseForPyLanguageThatWritesAFileToTestRootForEachPhase, \
    PyCommandThatWritesToStandardPhaseFile, \
    StatementsGeneratorThatWritesToStandardPhaseFile, \
    ModulesAndStatements
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


class StatementsGeneratorThatWritesCwdToStandardPhaseFile(StatementsGeneratorThatWritesToStandardPhaseFile):
    def __init__(self,
                 source_line: line_source.Line,
                 phase: phases.Phase):
        super().__init__(source_line, phase)
        self.__phase = phase

    def code_using_file_opened_for_writing(self,
                                           file_variable: str) -> ModulesAndStatements:
        print_statements = [py.print_value('pathlib.Path().resolve()',
                                           file_variable)]
        return ModulesAndStatements({'pathlib'},
                                    print_statements)
