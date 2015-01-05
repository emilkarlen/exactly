__author__ = 'emil'

import os
import pathlib
import unittest

from shelltest import phases
from shelltest.exec_abs_syn import py_cmd_gen
from shelltest.exec_abs_syn.config import Configuration
from shelltest.execution import execution
from shelltest.phase_instr import line_source
from shelltest_test.execution.util import utils
from shelltest_test.execution.util.py_unit_test_case import UnitTestCaseForPyLanguage


def standard_phase_file_path_eds(eds: execution.ExecutionDirectoryStructure,
                                 phase: phases.Phase) -> pathlib.Path:
    return standard_phase_file_path(eds.test_root_dir, phase)


def standard_phase_file_path(test_root_dir: pathlib.Path, phase: phases.Phase) -> pathlib.Path:
    return test_root_dir / standard_phase_file_base_name(phase)


def standard_phase_file_base_name(phase: phases.Phase) -> str:
    return 'testfile-for-phase-' + phase.name


class PyCommandThatWritesToStandardPhaseFile(py_cmd_gen.PythonCommand):
    def __init__(self,
                 source_line: line_source.Line,
                 phase: phases.Phase):
        super().__init__(source_line)
        self.__phase = phase

    def apply(self, configuration: Configuration):
        file_path = standard_phase_file_path(configuration.test_root_dir, self.__phase)
        with open(str(file_path), 'w') as f:
            contents = os.linesep.join(self.file_lines(configuration)) + os.linesep
            f.write(contents)

    def file_lines(self, configuration) -> list:
        raise NotImplementedError()


class UnitTestCaseForPyLanguageThatWritesAFileToTestRootForEachPhase(UnitTestCaseForPyLanguage):
    """
    Base class for tests where each phase is expected to write some output to a single file
    in the test root directory.

    The assertions consist of checking that these files exist and have expected content.
    """

    def __init__(self,
                 unittest_case: unittest.TestCase,
                 dbg_do_not_delete_dir_structure=False):
        super().__init__(unittest_case, dbg_do_not_delete_dir_structure)

    def _assertions(self):
        self.__assert_file_contents_for(phases.SETUP,
                                        self._expected_content_for_setup())
        self.__assert_file_contents_for(phases.APPLY,
                                        self._expected_content_for_apply())
        self.__assert_file_contents_for(phases.ASSERT,
                                        self._expected_content_for_assert())
        self.__assert_file_contents_for(phases.CLEANUP,
                                        self._expected_content_for_cleanup())

    def _expected_content_for_setup(self) -> str:
        return self._expected_content_for(phases.SETUP)

    def _expected_content_for_apply(self) -> str:
        return self._expected_content_for(phases.APPLY)

    def _expected_content_for_assert(self) -> str:
        return self._expected_content_for(phases.ASSERT)

    def _expected_content_for_cleanup(self) -> str:
        return self._expected_content_for(phases.CLEANUP)

    def _expected_content_for(self, phase: phases.Phase) -> str:
        raise NotImplementedError('Should not be used in this test')

    def __assert_file_contents_for(self,
                                   phase: phases.Phase,
                                   expected_content: str):
        utils.assert_is_file_with_contents(self.unittest_case,
                                                          standard_phase_file_path_eds(self.eds, phase),
                                                          expected_content)
