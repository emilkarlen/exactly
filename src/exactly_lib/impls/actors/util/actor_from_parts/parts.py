from abc import ABC, abstractmethod
from typing import Sequence, TypeVar, Generic, Optional

from exactly_lib.impls.actors.util import atc_proc_exe_settings
from exactly_lib.impls.svh_validators import PreOrPostSdsSvhValidationErrorValidator
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.act.actor import ActionToCheck, Actor
from exactly_lib.test_case.phases.act.execution_input import AtcExecutionInput
from exactly_lib.test_case.phases.act.instruction import ActPhaseInstruction
from exactly_lib.test_case.phases.common import SymbolUser
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.result import sh, svh, eh
from exactly_lib.test_case.result.eh import ExitCodeOrHardError
from exactly_lib.test_case.result.failure_details import FailureDetails
from exactly_lib.type_val_deps.dep_variants.sdv.sdv_validation import SdvValidator
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.file_utils.std import StdOutputFiles
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings


class Validator(ABC):
    @abstractmethod
    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep
                         ) -> svh.SuccessOrValidationErrorOrHardError:
        pass

    @abstractmethod
    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep
                            ) -> svh.SuccessOrValidationErrorOrHardError:
        pass


class Executor(ABC):
    def prepare(self,
                environment: InstructionEnvironmentForPostSdsStep,
                ):
        """
        :raises: :class:`HardErrorException`
        :return: Exit code from process execution.
        """
        pass

    @abstractmethod
    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                settings: ProcessExecutionSettings,
                stdin: Optional[StringSource],
                output: StdOutputFiles,
                ) -> int:
        """
        :raises: :class:`HardErrorException`
        :return: Exit code from process execution.
        """
        pass


EXECUTABLE_OBJECT = TypeVar('EXECUTABLE_OBJECT', bound=SymbolUser)


class ValidatorConstructor(Generic[EXECUTABLE_OBJECT], ABC):
    @abstractmethod
    def construct(self,
                  environment: InstructionEnvironmentForPreSdsStep,
                  executable_object: EXECUTABLE_OBJECT,
                  ) -> Validator:
        pass


class ExecutorConstructor(Generic[EXECUTABLE_OBJECT], ABC):
    @abstractmethod
    def construct(self,
                  environment: InstructionEnvironmentForPostSdsStep,
                  os_services: OsServices,
                  executable_object: EXECUTABLE_OBJECT,
                  ) -> Executor:
        pass


class UnconditionallySuccessfulValidatorConstructor(Generic[EXECUTABLE_OBJECT],
                                                    ValidatorConstructor[EXECUTABLE_OBJECT]):
    def construct(self,
                  environment: InstructionEnvironmentForPreSdsStep,
                  executable_object: EXECUTABLE_OBJECT,
                  ) -> Validator:
        return UnconditionallySuccessfulValidator()


class UnconditionallySuccessfulValidator(Validator):
    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep,
                         ) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep,
                            ) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()


class ValidatorFromPreOrPostSdsValidator(Validator):
    def __init__(self, validator: SdvValidator):
        self.validator = PreOrPostSdsSvhValidationErrorValidator(validator)

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        env = environment.path_resolving_environment
        return self.validator.validate_pre_sds_if_applicable(env)

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep
                            ) -> svh.SuccessOrValidationErrorOrHardError:
        env = environment.path_resolving_environment
        return self.validator.validate_post_sds_if_applicable(env)


class ValidatorWithHardErrorFromPostSdsValidation(Validator):
    def __init__(self, validator: SdvValidator):
        self.validator = validator

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        env = environment.path_resolving_environment
        mb_err_msg = self.validator.validate_pre_sds_if_applicable(env)
        return svh.new_maybe_svh_validation_error(mb_err_msg)

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep
                            ) -> svh.SuccessOrValidationErrorOrHardError:
        env = environment.path_resolving_environment
        mb_err_msg = self.validator.validate_post_sds_if_applicable(env)
        return svh.new_maybe_svh_hard_error(mb_err_msg)


class ExecutableObjectParser(Generic[EXECUTABLE_OBJECT], ABC):
    @abstractmethod
    def apply(self, instructions: Sequence[ActPhaseInstruction]) -> EXECUTABLE_OBJECT:
        """
        :raises ParseException

        :return: An object that can be given as argument to constructors of validator and executor designed
        to be used together with the parser.  The object also reports symbol usages known after parse.
        """
        pass


class ActorFromParts(Generic[EXECUTABLE_OBJECT], Actor):
    def __init__(self,
                 parser: ExecutableObjectParser[EXECUTABLE_OBJECT],
                 validator_constructor: ValidatorConstructor[EXECUTABLE_OBJECT],
                 executor_constructor: ExecutorConstructor[EXECUTABLE_OBJECT],
                 ):
        self.parser = parser
        self.validator_constructor = validator_constructor
        self.executor_constructor = executor_constructor

    def parse(self, instructions: Sequence[ActPhaseInstruction]) -> ActionToCheck:
        object_to_execute = self.parser.apply(instructions)
        return ActionToCheckFromParts(
            object_to_execute,
            self.validator_constructor,
            self.executor_constructor,
        )


class ActionToCheckFromParts(Generic[EXECUTABLE_OBJECT], ActionToCheck):
    """
    An ActSourceAndExecutor that can be used once to process the given act phase instructions.
    """

    def __init__(self,
                 object_to_execute: EXECUTABLE_OBJECT,
                 validator_constructor: ValidatorConstructor[EXECUTABLE_OBJECT],
                 executor_constructor: ExecutorConstructor[EXECUTABLE_OBJECT],
                 ):
        self.object_to_execute = object_to_execute
        self.validator_constructor = validator_constructor
        self.executor_constructor = executor_constructor

        self.__validator = None
        self.__executor = None

        self.__symbol_usages = self.object_to_execute.symbol_usages()

    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return self.__symbol_usages

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        self._construct_validator(environment)
        return self._validator.validate_pre_sds(environment)

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep
                            ) -> svh.SuccessOrValidationErrorOrHardError:
        return self._validator.validate_post_setup(environment)

    def prepare(self,
                environment: InstructionEnvironmentForPostSdsStep,
                os_services: OsServices,
                ) -> sh.SuccessOrHardError:
        try:
            self._construct_executor(environment, os_services)
            self._executor.prepare(environment)
        except HardErrorException as ex:
            return sh.new_sh_hard_error(ex.error)
        return sh.new_sh_success()

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                os_services: OsServices,
                atc_input: AtcExecutionInput,
                output: StdOutputFiles,
                ) -> ExitCodeOrHardError:
        settings = atc_proc_exe_settings.for_atc(environment, atc_input)
        try:
            exit_code = self._executor.execute(environment, settings, atc_input.stdin, output)
            return eh.new_eh_exit_code(exit_code)
        except HardErrorException as ex:
            return eh.new_eh_hard_error(FailureDetails.new_message(ex.error))

    def _construct_validator(self,
                             environment: InstructionEnvironmentForPreSdsStep):
        self.__validator = self.validator_constructor.construct(environment,
                                                                self.object_to_execute)
        assert isinstance(self.__validator, Validator), \
            'Constructed validator must be instance of ' + str(Validator)

    def _construct_executor(self,
                            environment: InstructionEnvironmentForPostSdsStep,
                            os_services: OsServices,
                            ):
        self.__executor = self.executor_constructor.construct(environment,
                                                              os_services,
                                                              self.object_to_execute)
        assert isinstance(self.__executor, Executor), \
            'Constructed executor must be instance of ' + str(Executor)

    @property
    def _validator(self) -> Validator:
        return self.__validator

    @property
    def _executor(self) -> Executor:
        return self.__executor
