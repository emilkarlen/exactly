from exactly_lib.execution.execution_mode import ExecutionMode
from exactly_lib.processing.parse.act_phase_source_parser import SourceCodeInstruction
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import common as instrs
from exactly_lib.test_case.phases.act import ActPhaseInstruction
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.before_assert import BeforeAssertPhaseInstruction
from exactly_lib.test_case.phases.cleanup import CleanupPhaseInstruction, PreviousPhase
from exactly_lib.test_case.phases.configuration import ConfigurationPhaseInstruction, ConfigurationBuilder
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction, SetupSettingsBuilder
from exactly_lib.util.line_source import LineSequence


def do_return(x):
    def ret_val(*args):
        return x

    return ret_val


def do_raise(ex: Exception):
    def ret_val(*args):
        raise ex

    return ret_val


class ImplementationErrorTestException(Exception):
    pass


def configuration_phase_instruction_that(main=do_return(sh.SuccessOrHardError),
                                         main_initial_action=None) -> ConfigurationPhaseInstruction:
    return _ConfigurationPhaseInstructionThat(main=_action_of(main_initial_action, main))


def setup_phase_instruction_that(validate_pre_sds=do_return(svh.new_svh_success()),
                                 validate_pre_eds_initial_action=None,
                                 validate_post_setup=do_return(svh.new_svh_success()),
                                 validate_post_setup_initial_action=None,
                                 main=do_return(sh.new_sh_success()),
                                 main_initial_action=None) -> SetupPhaseInstruction:
    return _SetupPhaseInstructionThat(_action_of(validate_pre_eds_initial_action, validate_pre_sds),
                                      _action_of(validate_post_setup_initial_action, validate_post_setup),
                                      _action_of(main_initial_action, main))


def act_phase_instruction_with_source(source_code: LineSequence = LineSequence(72, (
        'Dummy source code from act_phase_instruction_with_source',))) -> ActPhaseInstruction:
    return SourceCodeInstruction(source_code)


def before_assert_phase_instruction_that(validate_pre_sds=do_return(svh.new_svh_success()),
                                         validate_pre_eds_initial_action=None,
                                         validate_post_setup=do_return(svh.new_svh_success()),
                                         validate_post_setup_initial_action=None,
                                         main=do_return(sh.new_sh_success()),
                                         main_initial_action=None) -> AssertPhaseInstruction:
    return _BeforeAssertPhaseInstructionThat(_action_of(validate_pre_eds_initial_action, validate_pre_sds),
                                             _action_of(validate_post_setup_initial_action, validate_post_setup),
                                             _action_of(main_initial_action, main))


def assert_phase_instruction_that(validate_pre_sds=do_return(svh.new_svh_success()),
                                  validate_pre_eds_initial_action=None,
                                  validate_post_setup=do_return(svh.new_svh_success()),
                                  validate_post_setup_initial_action=None,
                                  main=do_return(pfh.new_pfh_pass()),
                                  main_initial_action=None) -> AssertPhaseInstruction:
    return _AssertPhaseInstructionThat(_action_of(validate_pre_eds_initial_action, validate_pre_sds),
                                       _action_of(validate_post_setup_initial_action, validate_post_setup),
                                       _action_of(main_initial_action, main))


def cleanup_phase_instruction_that(validate_pre_sds=do_return(svh.new_svh_success()),
                                   validate_pre_eds_initial_action=None,
                                   main=do_return(sh.new_sh_success()),
                                   main_initial_action=None) -> CleanupPhaseInstruction:
    return _CleanupPhaseInstructionThat(_action_of(validate_pre_eds_initial_action, validate_pre_sds),
                                        _action_of(main_initial_action, main))


class ConfigurationPhaseInstructionThatSetsExecutionMode(ConfigurationPhaseInstruction):
    def __init__(self,
                 value_to_set: ExecutionMode):
        self.value_to_set = value_to_set

    def main(self, configuration_builder: ConfigurationBuilder) -> sh.SuccessOrHardError:
        configuration_builder.set_execution_mode(self.value_to_set)
        return sh.new_sh_success()


class _ConfigurationPhaseInstructionThat(ConfigurationPhaseInstruction):
    def __init__(self,
                 main):
        self.do_main = main

    def main(self, configuration_builder: ConfigurationBuilder) -> sh.SuccessOrHardError:
        return self.do_main(configuration_builder)


class _SetupPhaseInstructionThat(SetupPhaseInstruction):
    def __init__(self,
                 validate_pre_sds,
                 validate_post_setup,
                 main):
        self._validate_pre_eds = validate_pre_sds
        self._validate_post_setup = validate_post_setup
        self._main = main

    def validate_pre_sds(self,
                         environment: instrs.InstructionEnvironmentForPreSdsStep) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return self._validate_pre_eds(environment)

    def main(self,
             environment: instrs.InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        return self._main(environment, os_services, settings_builder)

    def validate_post_setup(self,
                            environment: instrs.InstructionEnvironmentForPostSdsStep) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return self._validate_post_setup(environment)


class _BeforeAssertPhaseInstructionThat(BeforeAssertPhaseInstruction):
    def __init__(self,
                 validate_pre_sds,
                 validate_post_setup,
                 main):
        self._validate_pre_eds = validate_pre_sds
        self._validate_post_setup = validate_post_setup
        self._main = main

    def validate_pre_sds(self,
                         environment: instrs.InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        return self._validate_pre_eds(environment)

    def validate_post_setup(self,
                            environment: instrs.InstructionEnvironmentForPostSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        return self._validate_post_setup(environment)

    def main(self,
             environment: instrs.InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> sh.SuccessOrHardError:
        return self._main(environment, os_services)


class _AssertPhaseInstructionThat(AssertPhaseInstruction):
    def __init__(self,
                 validate_pre_sds,
                 validate_post_setup,
                 main):
        self._validate_pre_eds = validate_pre_sds
        self._validate_post_setup = validate_post_setup
        self._main = main

    def validate_pre_sds(self,
                         environment: instrs.InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        return self._validate_pre_eds(environment)

    def validate_post_setup(self,
                            environment: instrs.InstructionEnvironmentForPostSdsStep) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return self._validate_post_setup(environment)

    def main(self,
             environment: instrs.InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        return self._main(environment, os_services)


class _CleanupPhaseInstructionThat(CleanupPhaseInstruction):
    def __init__(self,
                 validate_pre_sds,
                 main):
        self.do_validate_pre_eds = validate_pre_sds
        self.do_main = main

    def validate_pre_sds(self,
                         environment: instrs.InstructionEnvironmentForPreSdsStep) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return self.do_validate_pre_eds(environment)

    def main(self,
             environment: instrs.InstructionEnvironmentForPostSdsStep,
             previous_phase: PreviousPhase,
             os_services: OsServices) -> sh.SuccessOrHardError:
        return self.do_main(environment, previous_phase, os_services)


def _action_of(initial_action, action_that_returns):
    if initial_action:
        def complete_action(*args):
            initial_action(*args)
            return action_that_returns(*args)

        return complete_action
    else:
        return action_that_returns
