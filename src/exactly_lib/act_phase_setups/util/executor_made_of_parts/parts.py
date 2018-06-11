import pathlib
from typing import Sequence, Callable

from exactly_lib.symbol.symbol_usage import SymbolUsage
from exactly_lib.test_case.act_phase_handling import ActSourceAndExecutor, ActSourceAndExecutorConstructor, \
    ActPhaseOsProcessExecutor
from exactly_lib.test_case.phases.act import ActPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep, SymbolUser
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator, \
    PreOrPostSdsSvhValidationErrorValidator
from exactly_lib.test_case.result import sh, svh
from exactly_lib.test_case.result.eh import ExitCodeOrHardError
from exactly_lib.util.std import StdFiles


class Validator:
    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep
                         ) -> svh.SuccessOrValidationErrorOrHardError:
        raise NotImplementedError(str(type(self)))

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep
                            ) -> svh.SuccessOrValidationErrorOrHardError:
        raise NotImplementedError(str(type(self)))


class UnconditionallySuccessfulValidator(Validator):
    def __init__(self, *args, **kwargs):
        pass

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()


class PartsValidatorFromPreOrPostSdsValidator(Validator):
    def __init__(self, validator_that_must_validate_pre_sds: PreOrPostSdsValidator):
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


class Executor:
    def prepare(self,
                environment: InstructionEnvironmentForPostSdsStep,
                script_output_dir_path: pathlib.Path) -> sh.SuccessOrHardError:
        return sh.new_sh_success()

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                script_output_dir_path: pathlib.Path,
                std_files: StdFiles) -> ExitCodeOrHardError:
        raise NotImplementedError(str(type(self)))


ExecutableObject = SymbolUser

ValidatorConstructorType = Callable[[InstructionEnvironmentForPreSdsStep,
                                     ExecutableObject],
                                    Validator]

ExecutorConstructorType = Callable[[ActPhaseOsProcessExecutor,
                                    InstructionEnvironmentForPreSdsStep,
                                    ExecutableObject],
                                   Executor]


class Parser:
    def apply(self, act_phase_instructions: Sequence[ActPhaseInstruction]) -> ExecutableObject:
        """
        :raises ParseException

        :return: An object that can be given as argument to constructors of validator and executor designed
        to be used together with the parser.  The object also reports symbol usages known after parse.
        """
        raise NotImplementedError(str(type(self)))


class Constructor(ActSourceAndExecutorConstructor):
    def __init__(self,
                 parser: Parser,
                 validator_constructor: ValidatorConstructorType,
                 executor_constructor: ExecutorConstructorType):
        self.parser = parser
        self.validator_constructor = validator_constructor
        self.executor_constructor = executor_constructor

    def apply(self,
              os_process_executor: ActPhaseOsProcessExecutor,
              environment: InstructionEnvironmentForPreSdsStep,
              act_phase_instructions: Sequence[ActPhaseInstruction]) -> ActSourceAndExecutor:
        return ActSourceAndExecutorMadeFromParserValidatorAndExecutor(self.parser,
                                                                      self.validator_constructor,
                                                                      self.executor_constructor,
                                                                      os_process_executor,
                                                                      environment,
                                                                      act_phase_instructions)


class ActSourceAndExecutorMadeFromParserValidatorAndExecutor(ActSourceAndExecutor):
    """
    An ActSourceAndExecutor that can be used once to process the given act phase instructions.
    """

    def __init__(self,
                 parser: Parser,
                 validator_constructor: ValidatorConstructorType,
                 executor_constructor: ExecutorConstructorType,
                 os_process_executor: ActPhaseOsProcessExecutor,
                 environment: InstructionEnvironmentForPreSdsStep,
                 act_phase_instructions: Sequence[ActPhaseInstruction]):
        self.parser = parser
        self.validator_constructor = validator_constructor
        self.executor_constructor = executor_constructor
        self.os_process_executor = os_process_executor
        self.environment = environment
        self.act_phase_instructions = act_phase_instructions

        self.__validator = None
        self.__executor = None

        self.__symbol_usages = []

    def parse(self, environment: InstructionEnvironmentForPreSdsStep):
        self._parse_and_construct_validator_and_executor()

    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return self.__symbol_usages

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        return self._validator.validate_pre_sds(environment)

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep
                            ) -> svh.SuccessOrValidationErrorOrHardError:
        return self._validator.validate_post_setup(environment)

    def prepare(self,
                environment: InstructionEnvironmentForPostSdsStep,
                script_output_dir_path: pathlib.Path) -> sh.SuccessOrHardError:
        return self._executor.prepare(environment, script_output_dir_path)

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                script_output_dir_path: pathlib.Path,
                std_files: StdFiles) -> ExitCodeOrHardError:
        return self._executor.execute(environment, script_output_dir_path, std_files)

    def _parse_and_construct_validator_and_executor(self) -> svh.SuccessOrValidationErrorOrHardError:
        object_to_execute = self.parser.apply(self.act_phase_instructions)
        self.__symbol_usages = object_to_execute.symbol_usages()
        self.__validator = self.validator_constructor(self.environment, object_to_execute)
        assert isinstance(self.__validator, Validator), \
            'Constructed validator must be instance of ' + str(Validator)
        self.__executor = self.executor_constructor(self.os_process_executor, self.environment, object_to_execute)
        assert isinstance(self.__executor, Executor), \
            'Constructed executor must be instance of ' + str(Executor)
        return svh.new_svh_success()

    @property
    def _validator(self) -> Validator:
        return self.__validator

    @property
    def _executor(self) -> Executor:
        return self.__executor
