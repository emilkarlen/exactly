from exactly_lib.instructions.multi_phase_instructions.utils.instruction_embryo import InstructionEmbryo
from exactly_lib.instructions.utils.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, PhaseLoggingPaths
from exactly_lib_test.instructions.test_resources.pre_or_post_sds_validator import ValidatorThat
from exactly_lib_test.test_resources.actions import do_return, action_of, do_nothing


def instruction_embryo_that(validate_pre_sds_initial_action=do_nothing,
                            validate_pre_sds_return_value=None,
                            validate_post_sds_initial_action=do_nothing,
                            validate_post_sds_return_value=None,
                            main=do_return(None),
                            main_initial_action=None,
                            symbol_usages_initial_action=None,
                            symbol_usages=do_return([])) -> InstructionEmbryo:
    return _InstructionEmbryoThat(ValidatorThat(pre_sds_action=validate_pre_sds_initial_action,
                                                pre_sds_return_value=validate_pre_sds_return_value,
                                                post_setup_action=validate_post_sds_initial_action,
                                                post_setup_return_value=validate_post_sds_return_value),
                                  action_of(main_initial_action, main),
                                  action_of(symbol_usages_initial_action, symbol_usages))


class _InstructionEmbryoThat(InstructionEmbryo):
    def __init__(self,
                 validator: PreOrPostSdsValidator,
                 main,
                 symbol_usages):
        self._validator = validator
        self._main = main
        self._symbol_usages = symbol_usages

    @property
    def symbol_usages(self) -> list:
        return self._symbol_usages()

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return self._validator

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             logging_paths: PhaseLoggingPaths,
             os_services: OsServices):
        return self._main(environment, os_services)
