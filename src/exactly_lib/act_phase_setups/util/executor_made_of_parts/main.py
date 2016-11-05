import pathlib

from exactly_lib.execution.act_phase import ActSourceAndExecutor, ExitCodeOrHardError, ActSourceAndExecutorConstructor
from exactly_lib.test_case.phases.common import HomeAndEds, InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh
from exactly_lib.util.std import StdFiles


class Validator:
    def validate_pre_sds(self, home_dir_path: pathlib.Path) -> svh.SuccessOrValidationErrorOrHardError:
        raise NotImplementedError(str(type(self)))

    def validate_post_setup(self, home_and_eds: HomeAndEds) -> svh.SuccessOrValidationErrorOrHardError:
        raise NotImplementedError(str(type(self)))


class UnconditionallySuccessfulValidator(Validator):
    def __init__(self, *args, **kwargs):
        pass

    def validate_pre_sds(self, home_dir_path: pathlib.Path) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def validate_post_setup(self, home_and_eds: HomeAndEds) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()


class Executor:
    def prepare(self, home_and_eds: HomeAndEds, script_output_dir_path: pathlib.Path) -> sh.SuccessOrHardError:
        raise NotImplementedError(str(type(self)))

    def execute(self,
                home_and_eds: HomeAndEds,
                script_output_dir_path: pathlib.Path,
                std_files: StdFiles) -> ExitCodeOrHardError:
        raise NotImplementedError(str(type(self)))


class ParseException(Exception):
    def __init__(self, cause: svh.SuccessOrValidationErrorOrHardError):
        self.cause = cause
        if cause.is_success:
            raise ValueError('A {} cannot represent SUCCESS'.format(str(type(self))))


class Parser:
    def apply(self, act_phase_instructions: list):
        """
        :raises ParseException

        :return: An object that can be given as argument to constructors of validator and executor designed
        to be used together with the parser.
        """
        raise NotImplementedError(str(type(self)))


class Constructor(ActSourceAndExecutorConstructor):
    def __init__(self,
                 parser: Parser,
                 validator_constructor,
                 executor_constructor):
        self.parser = parser
        self.validator_constructor = validator_constructor
        self.executor_constructor = executor_constructor

    def apply(self,
              environment: InstructionEnvironmentForPreSdsStep,
              act_phase_instructions: list) -> ActSourceAndExecutor:
        return ActSourceAndExecutorMadeFromParserValidatorAndExecutor(self.parser,
                                                                      self.validator_constructor,
                                                                      self.executor_constructor,
                                                                      environment,
                                                                      act_phase_instructions)


class ActSourceAndExecutorMadeFromParserValidatorAndExecutor(ActSourceAndExecutor):
    """
    An ActSourceAndExecutor that can be used once to process the given act phase instructions.
    """

    def __init__(self,
                 parser: Parser,
                 validator_constructor,
                 executor_constructor,
                 environment: InstructionEnvironmentForPreSdsStep,
                 act_phase_instructions: list):
        self.parser = parser
        self.validator_constructor = validator_constructor
        self.executor_constructor = executor_constructor
        self.environment = environment
        self.act_phase_instructions = act_phase_instructions

        self.__validator = None
        self.__executor = None

    def validate_pre_sds(self, home_dir_path: pathlib.Path) -> svh.SuccessOrValidationErrorOrHardError:
        status = self._parse_and_construct_validator_and_executor()
        if not status.is_success:
            return status
        return self._validator.validate_pre_sds(home_dir_path)

    def validate_post_setup(self, home_and_eds: HomeAndEds) -> svh.SuccessOrValidationErrorOrHardError:
        return self._validator.validate_post_setup(home_and_eds)

    def prepare(self, home_and_eds: HomeAndEds, script_output_dir_path: pathlib.Path) -> sh.SuccessOrHardError:
        return self._executor.prepare(home_and_eds, script_output_dir_path)

    def execute(self,
                home_and_eds: HomeAndEds,
                script_output_dir_path: pathlib.Path,
                std_files: StdFiles) -> ExitCodeOrHardError:
        return self._executor.execute(home_and_eds, script_output_dir_path, std_files)

    def _parse_and_construct_validator_and_executor(self) -> svh.SuccessOrValidationErrorOrHardError:
        try:
            object_to_execute = self.parser.apply(self.act_phase_instructions)
            self.__validator = self.validator_constructor(self.environment, object_to_execute)
            assert isinstance(self.__validator, Validator), \
                'Constructed validator must be instance of ' + str(Validator)
            self.__executor = self.executor_constructor(self.environment, object_to_execute)
            assert isinstance(self.__executor, Executor), \
                'Constructed executor must be instance of ' + str(Executor)
            return svh.new_svh_success()
        except ParseException as ex:
            return ex.cause

    @property
    def _validator(self) -> Validator:
        return self.__validator

    @property
    def _executor(self) -> Executor:
        return self.__executor
