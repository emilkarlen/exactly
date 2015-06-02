import types
from pathlib import Path

from shellcheck_lib_test.execution.util import python_code_gen as py
from shellcheck_lib.execution import phase_step
from shellcheck_lib.execution.phase_step import PhaseStep
from shellcheck_lib.test_case import instructions as i
from shellcheck_lib.test_case import success_or_validation_hard_or_error_construction as validation_result
from shellcheck_lib.test_case import success_or_hard_error_construction as execution_result
from shellcheck_lib.test_case import assert_instruction_result as assert_result
from shellcheck_lib.document.model import Instruction
from shellcheck_lib_test.execution.util.test_case_generation import TestCaseGeneratorBase


def do_nothing__anonymous_phase(phase_step: PhaseStep,
                                phase_environment: i.PhaseEnvironmentForAnonymousPhase):
    pass


def do_nothing__without_eds(phase_step: PhaseStep,
                            home_dir: Path):
    pass


def do_nothing__with_eds(phase_step: PhaseStep,
                         global_environment: i.GlobalEnvironmentForPostEdsPhase):
    pass


def do_nothing__generate_script(global_environment: i.GlobalEnvironmentForPostEdsPhase,
                                phase_environment: i.PhaseEnvironmentForScriptGeneration):
    pass


class TestCaseSetup(tuple):
    def __new__(cls,
                ret_val_from_validate: i.SuccessOrValidationErrorOrHardError=validation_result.new_success(),
                ret_val_from_execute: i.SuccessOrHardError=execution_result.new_success(),
                ret_val_from_assert_execute: i.PassOrFailOrHardError=assert_result.new_pass(),
                validation_action__without_eds: types.FunctionType=do_nothing__without_eds,
                anonymous_phase_action: types.FunctionType=do_nothing__anonymous_phase,
                validation_action__with_eds: types.FunctionType=do_nothing__with_eds,
                execution_action__with_eds: types.FunctionType=do_nothing__with_eds,
                execution__generate_script: types.FunctionType=do_nothing__generate_script,
                ):
        return tuple.__new__(cls, (ret_val_from_validate,
                                   ret_val_from_execute,
                                   ret_val_from_assert_execute,
                                   validation_action__without_eds,
                                   anonymous_phase_action,
                                   validation_action__with_eds,
                                   execution_action__with_eds,
                                   execution__generate_script,
                                   ))

    def as_anonymous_phase_instruction(self) -> i.AnonymousPhaseInstruction:
        return _AnonymousInstruction(self)

    def as_setup_phase_instruction(self) -> i.SetupPhaseInstruction:
        return _SetupInstruction(self)

    def as_act_phase_instruction(self) -> i.ActPhaseInstruction:
        return _ActInstruction(self)

    def as_assert_phase_instruction(self) -> i.AssertPhaseInstruction:
        return _AssertInstruction(self)

    def as_cleanup_phase_instruction(self) -> i.CleanupPhaseInstruction:
        return _CleanupInstruction(self)

    @property
    def ret_val_from_validate(self) -> i.SuccessOrValidationErrorOrHardError:
        return self[0]

    @property
    def ret_val_from_execute(self) -> i.SuccessOrHardError:
        return self[1]

    @property
    def ret_val_from_assert_execute(self) -> i.PassOrFailOrHardError:
        return self[2]

    @property
    def validation_action__without_eds(self) -> types.FunctionType:
        return self[3]

    @property
    def anonymous_phase_action(self) -> types.FunctionType:
        return self[4]

    @property
    def validation_action__with_eds(self) -> types.FunctionType:
        return self[5]

    @property
    def execution_action__with_eds(self) -> types.FunctionType:
        return self[6]

    @property
    def execution__generate_script(self) -> types.FunctionType:
        return self[7]


class TestCaseGeneratorForTestCaseSetup(TestCaseGeneratorBase):
    """
    Generation of a Test Case from a TestCaseSetup.

    The generated Test Case will have a single instruction for each phase.
    """

    def __init__(self,
                 setup: TestCaseSetup):
        super().__init__()
        self.setup = setup

    def _anonymous_phase(self) -> list:
        return self.__for(self.setup.as_anonymous_phase_instruction())

    def _setup_phase(self) -> list:
        return self.__for(self.setup.as_setup_phase_instruction())

    def _act_phase(self) -> list:
        return self.__for(self.setup.as_act_phase_instruction())

    def _assert_phase(self) -> list:
        return self.__for(self.setup.as_assert_phase_instruction())

    def _cleanup_phase(self) -> list:
        return self.__for(self.setup.as_cleanup_phase_instruction())

    def __for(self,
              instruction: Instruction) -> list:
        return [self._next_instruction_line(instruction)]


class _AnonymousInstruction(i.AnonymousPhaseInstruction):
    def __init__(self,
                 configuration: TestCaseSetup):
        self.__configuration = configuration

    def main(self,
             global_environment,
             phase_environment: i.PhaseEnvironmentForAnonymousPhase) -> i.SuccessOrHardError:
        self.__configuration.anonymous_phase_action(phase_step.ANONYMOUS_EXECUTE,
                                                    phase_environment)
        return self.__configuration.ret_val_from_execute


def print_to_file__generate_script(code_using_file_opened_for_writing: types.FunctionType,
                                   file_name: str,
                                   global_environment: i.GlobalEnvironmentForPostEdsPhase,
                                   phase_environment: i.PhaseEnvironmentForScriptGeneration):
    """
    Function that is designed as the execution__generate_script argument to TestCaseSetup, after
    giving the first two arguments using partial application.

    :param code_using_file_opened_for_writing: function: file_variable: str -> ModulesAndStatements
    :param file_name: the name of the file to output to.
    :param global_environment: Environment from act instruction
    :param phase_environment: Environment from act instruction
    """
    file_path = global_environment.eds.test_root_dir / file_name
    file_name = str(file_path)
    file_var = '_file_var'
    mas = code_using_file_opened_for_writing(file_var)
    all_statements = py.with_opened_file(file_name,
                                         file_var,
                                         'w',
                                         mas.statements)

    program = py.program_lines(mas.used_modules,
                               all_statements)
    # print(os.linesep.join(statements))
    phase_environment.append.raw_script_statements(program)


class _SetupInstruction(i.SetupPhaseInstruction):
    def __init__(self,
                 configuration: TestCaseSetup):
        self.__configuration = configuration

    def pre_validate(self,
                     global_environment: i.GlobalEnvironmentForPreEdsStep) -> i.SuccessOrValidationErrorOrHardError:
        self.__configuration.validation_action__without_eds(phase_step.SETUP_PRE_VALIDATE,
                                                            global_environment.home_directory)
        return self.__configuration.ret_val_from_execute

    def main(self,
             global_environment: i.GlobalEnvironmentForPostEdsPhase,
             settings_builder: i.SetupSettingsBuilder) -> i.SuccessOrHardError:
        self.__configuration.execution_action__with_eds(phase_step.SETUP_EXECUTE,
                                                        global_environment)
        return self.__configuration.ret_val_from_execute

    def post_validate(self,
                      global_environment: i.GlobalEnvironmentForPostEdsPhase) -> i.SuccessOrValidationErrorOrHardError:
        self.__configuration.validation_action__without_eds(phase_step.SETUP_POST_VALIDATE,
                                                            global_environment.home_directory)
        return self.__configuration.ret_val_from_execute


class _ActInstruction(i.ActPhaseInstruction):
    def __init__(self,
                 configuration: TestCaseSetup):
        self.__configuration = configuration

    def validate(self, global_environment: i.GlobalEnvironmentForPostEdsPhase) -> i.SuccessOrValidationErrorOrHardError:
        self.__configuration.validation_action__with_eds(phase_step.ACT_VALIDATE,
                                                         global_environment)
        return self.__configuration.ret_val_from_validate

    def main(self,
             global_environment: i.GlobalEnvironmentForPostEdsPhase,
             phase_environment: i.PhaseEnvironmentForScriptGeneration) -> i.SuccessOrHardError:
        self.__configuration.execution_action__with_eds(phase_step.ACT_SCRIPT_GENERATION,
                                                        global_environment)
        self.__configuration.execution__generate_script(global_environment,
                                                        phase_environment)
        return self.__configuration.ret_val_from_execute


class _AssertInstruction(i.AssertPhaseInstruction):
    def __init__(self,
                 configuration: TestCaseSetup):
        self.__configuration = configuration

    def validate(self,
                 global_environment: i.GlobalEnvironmentForPostEdsPhase) -> i.SuccessOrValidationErrorOrHardError:
        self.__configuration.validation_action__with_eds(phase_step.ASSERT_VALIDATE,
                                                         global_environment)
        return self.__configuration.ret_val_from_validate

    def main(self,
             global_environment: i.GlobalEnvironmentForPostEdsPhase,
             phase_environment: i.PhaseEnvironmentForInternalCommands) -> i.PassOrFailOrHardError:
        self.__configuration.execution_action__with_eds(phase_step.ASSERT_EXECUTE,
                                                        global_environment)
        return self.__configuration.ret_val_from_assert_execute


class _CleanupInstruction(i.CleanupPhaseInstruction):
    def __init__(self,
                 configuration: TestCaseSetup):
        self.__configuration = configuration

    def main(self,
             global_environment: i.GlobalEnvironmentForPostEdsPhase,
             phase_environment: i.PhaseEnvironmentForInternalCommands) -> i.SuccessOrHardError:
        self.__configuration.execution_action__with_eds(phase_step.CLEANUP_EXECUTE,
                                                        global_environment)
        return self.__configuration.ret_val_from_execute

