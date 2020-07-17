from abc import ABC, abstractmethod
from typing import Sequence, TypeVar, Generic

from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.symbol.sdv_validation import SdvValidator
from exactly_lib.test_case.actor import ActionToCheck, Actor, AtcOsProcessExecutor
from exactly_lib.test_case.phases.act import ActPhaseInstruction
from exactly_lib.test_case.phases.common import SymbolUser
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.result import sh, svh
from exactly_lib.test_case.result.eh import ExitCodeOrHardError
from exactly_lib.test_case_utils.validators import PreOrPostSdsSvhValidationErrorValidator
from exactly_lib.util.file_utils.std import StdFiles


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
                ) -> sh.SuccessOrHardError:
        return sh.new_sh_success()

    @abstractmethod
    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                std_files: StdFiles) -> ExitCodeOrHardError:
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
                  process_executor: AtcOsProcessExecutor,
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
    def __init__(self, validator_that_must_validate_pre_sds: SdvValidator):
        self.validator = PreOrPostSdsSvhValidationErrorValidator(validator_that_must_validate_pre_sds)

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        env = environment.path_resolving_environment
        return self.validator.validate_pre_sds_if_applicable(env)

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep
                            ) -> svh.SuccessOrValidationErrorOrHardError:
        env = environment.path_resolving_environment
        return self.validator.validate_post_sds_if_applicable(env)


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
        self.__script_storage_dir = None

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
                os_process_executor: AtcOsProcessExecutor,
                ) -> sh.SuccessOrHardError:
        self._construct_executor(environment, os_process_executor)
        return self._executor.prepare(environment)

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                os_process_executor: AtcOsProcessExecutor,
                std_files: StdFiles) -> ExitCodeOrHardError:
        return self._executor.execute(environment, std_files)

    def _construct_validator(self,
                             environment: InstructionEnvironmentForPreSdsStep):
        self.__validator = self.validator_constructor.construct(environment,
                                                                self.object_to_execute)
        assert isinstance(self.__validator, Validator), \
            'Constructed validator must be instance of ' + str(Validator)

    def _construct_executor(self,
                            environment: InstructionEnvironmentForPostSdsStep,
                            os_process_executor: AtcOsProcessExecutor,
                            ):
        self.__executor = self.executor_constructor.construct(environment,
                                                              os_process_executor,
                                                              self.object_to_execute)
        assert isinstance(self.__executor, Executor), \
            'Constructed executor must be instance of ' + str(Executor)

    @property
    def _validator(self) -> Validator:
        return self.__validator

    @property
    def _executor(self) -> Executor:
        return self.__executor
