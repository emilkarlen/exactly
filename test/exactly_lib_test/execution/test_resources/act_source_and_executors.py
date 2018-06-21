import pathlib
from typing import Sequence

from exactly_lib.symbol.symbol_usage import SymbolUsage
from exactly_lib.test_case.act_phase_handling import ActSourceAndExecutor
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.result import svh, sh
from exactly_lib.test_case.result.eh import ExitCodeOrHardError, new_eh_exit_code
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.util.std import StdFiles
from exactly_lib_test.execution.test_resources import test_actions
from exactly_lib_test.test_resources import actions
from exactly_lib_test.test_resources.actions import do_nothing


class ActSourceAndExecutorThatJustReturnsSuccess(ActSourceAndExecutor):
    def parse(self, environment: InstructionEnvironmentForPreSdsStep):
        pass

    def validate_pre_sds(self, home_dir_path: pathlib.Path) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def validate_post_setup(self, home_and_sds: HomeAndSds) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def prepare(self, home_and_sds: HomeAndSds, script_output_dir_path: pathlib.Path) -> sh.SuccessOrHardError:
        return sh.new_sh_success()

    def execute(self, home_and_sds: HomeAndSds, script_output_dir_path: pathlib.Path,
                std_files: StdFiles) -> ExitCodeOrHardError:
        return new_eh_exit_code(0)


class ActSourceAndExecutorWrapperWithActions(ActSourceAndExecutor):
    def __init__(self,
                 wrapped: ActSourceAndExecutor,
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

    def parse(self, environment: InstructionEnvironmentForPreSdsStep):
        self.before_wrapped_parse(environment)
        self.__wrapped.parse(environment)

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
                script_output_dir_path: pathlib.Path) -> sh.SuccessOrHardError:
        self.before_wrapped_prepare(environment, script_output_dir_path)
        return self.__wrapped.prepare(environment, script_output_dir_path)

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                script_output_dir_path: pathlib.Path,
                std_files: StdFiles) -> ExitCodeOrHardError:
        self.before_wrapped_execute(environment, script_output_dir_path, std_files)
        return self.__wrapped.execute(environment, script_output_dir_path, std_files)


class ActSourceAndExecutorThatRunsConstantActions(ActSourceAndExecutor):
    def __init__(self,
                 parse_action=actions.do_nothing,
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
        self.__parse_action = parse_action
        self.__validate_pre_sds_initial_action = validate_pre_sds_initial_action
        self.__validate_pre_sds_action = validate_pre_sds_action
        self.__validate_post_setup_initial_action = validate_post_setup_initial_action
        self.__validate_post_setup_action = validate_post_setup_action
        self.__prepare_initial_action = prepare_initial_action
        self.__prepare_action = prepare_action
        self.__execute_initial_action = execute_initial_action
        self.__execute_action = execute_action
        self.__symbol_usages_action = symbol_usages_action

    def parse(self, environment: InstructionEnvironmentForPreSdsStep):
        self.__parse_action(environment)

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

    def prepare(self, environment: InstructionEnvironmentForPostSdsStep,
                script_output_dir_path: pathlib.Path) -> sh.SuccessOrHardError:
        self.__prepare_initial_action(environment, script_output_dir_path)
        return self.__prepare_action(environment, script_output_dir_path)

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                script_output_dir_path: pathlib.Path,
                std_files: StdFiles) -> ExitCodeOrHardError:
        self.__execute_initial_action(environment, script_output_dir_path, std_files)
        return self.__execute_action(environment, script_output_dir_path, std_files)
