import os
import pathlib
import unittest

from shelltest.exec_abs_syn import success_or_validation_hard_or_error_construction
from shelltest.exec_abs_syn.success_or_hard_error_construction import new_success
from shelltest.execution.execution_directory_structure import ExecutionDirectoryStructure
from shelltest import phases
from shelltest.exec_abs_syn import py_cmd_gen, instructions
from shelltest.exec_abs_syn.config import Configuration
from shelltest_test.execution.util import utils
from shelltest_test.execution.util.py_unit_test_case import UnitTestCaseForPy3Language
from shelltest_test.execution.util import python_code_gen as py


def standard_phase_file_path_eds(eds: ExecutionDirectoryStructure,
                                 phase: phases.Phase) -> pathlib.Path:
    return standard_phase_file_path(eds.test_root_dir, phase)


def standard_phase_file_path(test_root_dir: pathlib.Path, phase: phases.Phase) -> pathlib.Path:
    return test_root_dir / standard_phase_file_base_name(phase)


def standard_phase_file_base_name(phase: phases.Phase) -> str:
    return 'testfile-for-phase-' + phase.name


class PyCommandThatWritesToStandardPhaseFile(py_cmd_gen.PythonCommand):
    def __init__(self,
                 phase: phases.Phase):
        super().__init__()
        self.__phase = phase

    def apply(self, configuration: Configuration):
        file_path = standard_phase_file_path(configuration.test_root_dir, self.__phase)
        with open(str(file_path), 'w') as f:
            contents = os.linesep.join(self.file_lines(configuration)) + os.linesep
            f.write(contents)

    def file_lines(self, configuration) -> list:
        raise NotImplementedError()


class InternalInstructionThatWritesToStandardPhaseFile(instructions.InternalInstruction):
    def __init__(self,
                 phase: phases.Phase):
        super().__init__()
        self.__phase = phase

    def execute(self, phase_name: str,
                global_environment: instructions.GlobalEnvironmentForNamedPhase,
                phase_environment: instructions.PhaseEnvironmentForInternalCommands):
        file_path = standard_phase_file_path(global_environment.eds.test_root_dir, self.__phase)
        with open(str(file_path), 'w') as f:
            contents = os.linesep.join(self._file_lines(global_environment)) + os.linesep
            f.write(contents)

    def _file_lines(self, global_environment: instructions.GlobalEnvironmentForNamedPhase) -> list:
        raise NotImplementedError()


class ModulesAndStatements:
    def __init__(self,
                 used_modules: set,
                 statements: list):
        self.__used_modules = used_modules
        self.__statements = statements

    @property
    def used_modules(self) -> set:
        return self.__used_modules

    @property
    def statements(self) -> list:
        return self.__statements


class ActPhaseInstructionThatWritesToStandardPhaseFile(instructions.ActPhaseInstruction):

    def __init__(self,
                 phase: phases.Phase):
        super().__init__()
        self.__phase = phase

    def validate(self, global_environment: instructions.GlobalEnvironmentForNamedPhase) \
            -> instructions.SuccessOrValidationErrorOrHardError:
        return success_or_validation_hard_or_error_construction.new_success()

    def update_phase_environment(
            self,
            phase_name: str,
            global_environment: instructions.GlobalEnvironmentForNamedPhase,
            phase_environment: instructions.PhaseEnvironmentForScriptGeneration) -> instructions.SuccessOrHardError:
        file_path = standard_phase_file_path(global_environment.eds.test_root_dir, self.__phase)
        file_name = str(file_path)
        file_var = '_file_var'
        mas = self.code_using_file_opened_for_writing(file_var)
        all_statements = py.with_opened_file(file_name,
                                             file_var,
                                             'w',
                                             mas.statements)

        program = py.program_lines(mas.used_modules,
                                   all_statements)
        # print(os.linesep.join(statements))
        phase_environment.append.raw_script_statements(program)
        return new_success()

    def code_using_file_opened_for_writing(self,
                                           file_variable: str) -> ModulesAndStatements:
        raise NotImplementedError()


class UnitTestCaseForPy3LanguageThatWritesAFileToTestRootForEachPhase(UnitTestCaseForPy3Language):
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
        self.__assert_file_contents_for(phases.ACT,
                                        self._expected_content_for_apply())
        self.__assert_file_contents_for(phases.ASSERT,
                                        self._expected_content_for_assert())
        self.__assert_file_contents_for(phases.CLEANUP,
                                        self._expected_content_for_cleanup())

    def _expected_content_for_setup(self) -> str:
        return self._expected_content_for(phases.SETUP)

    def _expected_content_for_apply(self) -> str:
        return self._expected_content_for(phases.ACT)

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
