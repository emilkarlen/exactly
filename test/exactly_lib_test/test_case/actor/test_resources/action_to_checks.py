import pathlib
from typing import Sequence

from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.actor import ActionToCheck
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.result import svh, sh
from exactly_lib.test_case.result.eh import ExitCodeOrHardError, new_eh_exit_code
from exactly_lib.util.file_utils.std import StdFiles
from exactly_lib_test.test_case.actor.test_resources import test_actions
from exactly_lib_test.test_resources import actions
from exactly_lib_test.test_resources.actions import do_nothing


class ActionToCheckThatJustReturnsSuccess(ActionToCheck):
    def validate_pre_sds(self, home_dir_path: pathlib.Path) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def validate_post_setup(self, tcds: TestCaseDs) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def prepare(self,
                environment: InstructionEnvironmentForPostSdsStep,
                os_services: OsServices,
                ) -> sh.SuccessOrHardError:
        return sh.new_sh_success()

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                os_services: OsServices,
                std_files: StdFiles,
                ) -> ExitCodeOrHardError:
        return new_eh_exit_code(0)


class ActionToCheckWrapperWithActions(ActionToCheck):
    def __init__(self,
                 wrapped: ActionToCheck,
                 before_wrapped_parse=do_nothing,
                 before_wrapped_validate=do_nothing,
                 before_wrapped_prepare=do_nothing,
                 before_wrapped_execute=do_nothing,
                 before_wrapped_validate_pre_sds=do_nothing
                 ):
        self.__wrapped = wrapped
        self.before_wrapped_parse = before_wrapped_parse
        self.before_wrapped_validate = before_wrapped_validate
        self.before_wrapped_validate_pre_sds = before_wrapped_validate_pre_sds
        self.before_wrapped_prepare = before_wrapped_prepare
        self.before_wrapped_execute = before_wrapped_execute

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep
                         ) -> svh.SuccessOrValidationErrorOrHardError:
        self.before_wrapped_validate_pre_sds(environment)
        return self.__wrapped.validate_pre_sds(environment)

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep
                            ) -> svh.SuccessOrValidationErrorOrHardError:
        self.before_wrapped_validate(environment)
        return self.__wrapped.validate_post_setup(environment)

    def prepare(self,
                environment: InstructionEnvironmentForPostSdsStep,
                os_services: OsServices,
                ) -> sh.SuccessOrHardError:
        self.before_wrapped_prepare(environment)
        return self.__wrapped.prepare(environment, os_services)

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                os_services: OsServices,
                std_files: StdFiles,
                ) -> ExitCodeOrHardError:
        self.before_wrapped_execute(environment, std_files)
        return self.__wrapped.execute(environment, os_services, std_files)


class ActionToCheckThatRunsConstantActions(ActionToCheck):
    def __init__(self,
                 validate_pre_sds_action=test_actions.validate_action_that_returns(svh.new_svh_success()),
                 validate_pre_sds_initial_action=actions.do_nothing,
                 validate_post_setup_action=test_actions.validate_action_that_returns(svh.new_svh_success()),
                 validate_post_setup_initial_action=actions.do_nothing,
                 prepare_action=test_actions.prepare_action_that_returns(sh.new_sh_success()),
                 prepare_initial_action=actions.do_nothing,
                 execute_action=test_actions.execute_action_that_returns_exit_code(0),
                 execute_initial_action=actions.do_nothing,
                 symbol_usages_action=actions.do_return([])
                 ):
        self.__validate_pre_sds_initial_action = validate_pre_sds_initial_action
        self.__validate_pre_sds_action = validate_pre_sds_action
        self.__validate_post_setup_initial_action = validate_post_setup_initial_action
        self.__validate_post_setup_action = validate_post_setup_action
        self.__prepare_initial_action = prepare_initial_action
        self.__prepare_action = prepare_action
        self.__execute_initial_action = execute_initial_action
        self.__execute_action = execute_action
        self.__symbol_usages_action = symbol_usages_action

    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return self.__symbol_usages_action()

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep
                         ) -> svh.SuccessOrValidationErrorOrHardError:
        self.__validate_pre_sds_initial_action(environment)
        return self.__validate_pre_sds_action(environment)

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep
                            ) -> svh.SuccessOrValidationErrorOrHardError:
        self.__validate_post_setup_initial_action(environment)
        return self.__validate_post_setup_action(environment)

    def prepare(self,
                environment: InstructionEnvironmentForPostSdsStep,
                os_services: OsServices,
                ) -> sh.SuccessOrHardError:
        self.__prepare_initial_action(environment)
        return self.__prepare_action(environment)

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                os_services: OsServices,
                std_files: StdFiles,
                ) -> ExitCodeOrHardError:
        self.__execute_initial_action(environment, std_files)
        return self.__execute_action(environment, std_files)
