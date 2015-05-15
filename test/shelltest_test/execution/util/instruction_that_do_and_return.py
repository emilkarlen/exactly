from pathlib import Path
import types

from shelltest.execution.phase_step import PhaseStep
from shelltest.exec_abs_syn import instructions as i
from shelltest.exec_abs_syn import success_or_validation_hard_or_error_construction as validation_result
from shelltest.exec_abs_syn import success_or_hard_error_construction as execution_result
from shelltest.exec_abs_syn import assert_instruction_result as assert_result


def do_nothing__with_eds(phase_step: PhaseStep,
                         global_environment: i.GlobalEnvironmentForNamedPhase):
    pass


def do_nothing__with_only_home_dir(phase_step: PhaseStep,
                                   home_dir: Path):
    pass


class Configuration(tuple):
    """
    Class for enumeration of phase constants
    """

    def __new__(cls,
                ret_val_from_validate: i.SuccessOrValidationErrorOrHardError=validation_result.new_success(),
                ret_val_from_execute: i.SuccessOrHardError=execution_result.new_success(),
                ret_val_from_assert_execute: i.PassOrFailOrHardError=assert_result.new_pass(),
                validation_action__without_eds: types.FunctionType=do_nothing__with_only_home_dir,
                execution_action__without_eds: types.FunctionType=do_nothing__with_only_home_dir,
                validation_action__with_eds: types.FunctionType=do_nothing__with_eds,
                execution_action__with_eds: types.FunctionType=do_nothing__with_eds,
                ):
        return tuple.__new__(cls, (ret_val_from_validate,
                                   ret_val_from_execute,
                                   ret_val_from_assert_execute,
                                   validation_action__without_eds,
                                   execution_action__without_eds,
                                   validation_action__with_eds,
                                   execution_action__with_eds,
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
    def execution_action__without_eds(self) -> types.FunctionType:
        return self[4]

    @property
    def validation_action__with_eds(self) -> types.FunctionType:
        return self[5]

    @property
    def execution_action__with_eds(self) -> types.FunctionType:
        return self[6]


class _AnonymousInstruction(i.AnonymousPhaseInstruction):
    def __init__(self,
                 configuration: Configuration):
        self.__configuration = configuration

    def execute(self, phase_name: str,
                global_environment,
                phase_environment: i.PhaseEnvironmentForAnonymousPhase) -> i.SuccessOrHardError:
        self.__configuration.execution_action__without_eds(global_environment.home_directory)
        return self.__configuration.ret_val_from_execute


class _SetupInstruction(i.SetupPhaseInstruction):
    def __init__(self,
                 configuration: Configuration):
        self.__configuration = configuration

    def validate(self,
                 global_environment: i.GlobalEnvironmentForPreEdsStep) -> i.SuccessOrValidationErrorOrHardError:
        self.__configuration.validation_action__without_eds(global_environment.home_directory)
        return self.__configuration.ret_val_from_execute

    def execute(self, phase_name: str,
                global_environment: i.GlobalEnvironmentForNamedPhase,
                phase_environment: i.PhaseEnvironmentForInternalCommands) -> i.SuccessOrHardError:
        self.__configuration.execution_action__with_eds(global_environment)
        return self.__configuration.ret_val_from_execute


class _ActInstruction(i.ActPhaseInstruction):
    def __init__(self,
                 configuration: Configuration):
        self.__configuration = configuration

    def validate(self, global_environment: i.GlobalEnvironmentForNamedPhase) -> i.SuccessOrValidationErrorOrHardError:
        self.__configuration.validation_action__with_eds(global_environment)
        return self.__configuration.ret_val_from_validate

    def update_phase_environment(self,
                                 phase_name: str,
                                 global_environment: i.GlobalEnvironmentForNamedPhase,
                                 phase_environment: i.PhaseEnvironmentForScriptGeneration) -> i.SuccessOrHardError:
        self.__configuration.execution_action__with_eds(global_environment)
        return self.__configuration.ret_val_from_execute


class _AssertInstruction(i.AssertPhaseInstruction):
    def __init__(self,
                 configuration: Configuration):
        self.__configuration = configuration

    def validate(self,
                 global_environment: i.GlobalEnvironmentForNamedPhase) -> i.SuccessOrValidationErrorOrHardError:
        self.__configuration.validation_action__with_eds(global_environment)
        return self.__configuration.ret_val_from_validate

    def execute(self,
                phase_name: str,
                global_environment: i.GlobalEnvironmentForNamedPhase,
                phase_environment: i.PhaseEnvironmentForInternalCommands) -> i.PassOrFailOrHardError:
        self.__configuration.execution_action__with_eds(global_environment)
        return self.__configuration.ret_val_from_assert_execute


class _CleanupInstruction(i.CleanupPhaseInstruction):
    def __init__(self,
                 configuration: Configuration):
        self.__configuration = configuration

    def execute(self,
                phase_name: str,
                global_environment: i.GlobalEnvironmentForNamedPhase,
                phase_environment: i.PhaseEnvironmentForInternalCommands) -> i.SuccessOrHardError:
        self.__configuration.execution_action__with_eds(global_environment)
        return self.__configuration.ret_val_from_execute

