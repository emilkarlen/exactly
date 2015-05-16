import os
import pathlib
import unittest

from shelltest.exec_abs_syn.success_or_hard_error_construction import new_success
from shelltest.exec_abs_syn import success_or_validation_hard_or_error_construction
from shelltest import phases
from shelltest.exec_abs_syn import instructions
from shelltest_test.execution.util import python_code_gen as py
from shelltest_test.execution.util.py_unit_test_case_with_file_output import \
    ModulesAndStatements, UnitTestCaseForPy3LanguageThatWritesAFileToTestRootForEachPhase, \
    InternalInstructionThatWritesToStandardPhaseFile, ActPhaseInstructionThatWritesToStandardPhaseFile
from shelltest_test.execution.util.utils import un_lines


class TestCase(UnitTestCaseForPy3LanguageThatWritesAFileToTestRootForEachPhase):
    def __init__(self,
                 unittest_case: unittest.TestCase,
                 dbg_do_not_delete_dir_structure=False):
        super().__init__(unittest_case, dbg_do_not_delete_dir_structure)

    def _default_instructions_for_setup_assert_cleanup(self, phase: phases.Phase) -> list:
        return [
            InternalInstructionThatWritesCurrentWorkingDirectory(phase),
            InternalInstructionThatChangesCwdToHomeDir(),
        ]

    def _act_phase(self) -> list:
        import_statements_generator = ActPhaseInstructionForImportStatements()
        return [
            self._next_instruction_line(
                import_statements_generator),
            self._next_instruction_line(
                ActPhaseInstructionThatWritesCurrentWorkingDirectory(phases.ACT,
                                                                     import_statements_generator)),
            self._next_instruction_line(
                ActPhaseInstructionThatChangesCwdToHomeDir(import_statements_generator)),
        ]

    def _expected_content_for(self, phase: phases.Phase) -> str:
        return un_lines([str(self.eds.test_root_dir)])


class InternalInstructionThatWritesCurrentWorkingDirectory(InternalInstructionThatWritesToStandardPhaseFile):
    def __init__(self,
                 phase: phases.Phase):
        super().__init__(phase)

    def _file_lines(self, global_environment: instructions.GlobalEnvironmentForNamedPhase) -> list:
        cwd_path = pathlib.Path().resolve()
        return [str(cwd_path)]


class InternalInstructionThatChangesCwdToHomeDir(instructions.InternalInstruction):
    def __init__(self):
        super().__init__()

    def execute(self, phase_name: str,
                global_environment: instructions.GlobalEnvironmentForNamedPhase,
                phase_environment: instructions.PhaseEnvironmentForInternalCommands):
        os.chdir(str(global_environment.home_directory))
        # print(os.getcwd())


class ActPhaseInstructionForImportStatements(instructions.ActPhaseInstruction):
    """
    Pseudo-instruction for outputting Python import statements at the top of the program.

    Later instructions add their used modules to an object of this class.
    """

    def __init__(self):
        super().__init__()
        self.__modules = set()

    def append_module(self, module_name: str):
        self.__modules.add(module_name)

    def validate(self, global_environment: instructions.GlobalEnvironmentForNamedPhase) \
            -> instructions.SuccessOrValidationErrorOrHardError:
        return success_or_validation_hard_or_error_construction.new_success()

    def update_phase_environment(self, phase_name: str,
                                 global_environment: instructions.GlobalEnvironmentForNamedPhase,
                                 phase_environment: instructions.PhaseEnvironmentForScriptGeneration) \
            -> instructions.SuccessOrHardError:
        import_statements = ['import %s' % module_name
                             for module_name in self.__modules]
        phase_environment.append.raw_script_statements(import_statements)
        return new_success()


class ActPhaseInstructionThatWritesCurrentWorkingDirectory(ActPhaseInstructionThatWritesToStandardPhaseFile):
    def __init__(self,
                 phase: phases.Phase,
                 module_container: ActPhaseInstructionForImportStatements):
        super().__init__(phase)
        self.__phase = phase
        module_container.append_module('pathlib')

    def code_using_file_opened_for_writing(self,
                                           file_variable: str) -> ModulesAndStatements:
        print_statements = [py.print_value('pathlib.Path().resolve()',
                                           file_variable)]
        return ModulesAndStatements(
            set(),
            print_statements)


class ActPhaseInstructionThatChangesCwdToHomeDir(instructions.ActPhaseInstruction):
    def __init__(self,
                 module_container: ActPhaseInstructionForImportStatements):
        super().__init__()
        module_container.append_module('os')

    def validate(self, global_environment: instructions.GlobalEnvironmentForNamedPhase) \
            -> instructions.SuccessOrValidationErrorOrHardError:
        return success_or_validation_hard_or_error_construction.new_success()

    def update_phase_environment(self, phase_name: str,
                                 global_environment: instructions.GlobalEnvironmentForNamedPhase,
                                 phase_environment: instructions.PhaseEnvironmentForScriptGeneration) -> instructions.SuccessOrHardError:
        statements = [
            'os.chdir(%s)' % py.string_expr(str(global_environment.home_directory)),
            # 'print(os.getcwd())'
        ]
        phase_environment.append.raw_script_statements(statements)
        return new_success()
