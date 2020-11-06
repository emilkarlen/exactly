from typing import Sequence, Dict, Generic, Callable, Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.execution import phase_step
from exactly_lib.impls.actors.util.actor_from_parts import parts as sut
from exactly_lib.impls.actors.util.actor_from_parts.parts import EXECUTABLE_OBJECT, Validator, Executor
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.actor import ParseException
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.act import ActPhaseInstruction
from exactly_lib.test_case.phases.common import SymbolUser
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.result import svh
from exactly_lib.type_val_prims.string_model import StringModel
from exactly_lib.util.file_utils.std import StdOutputFiles
from exactly_lib_test.test_case.actor.test_resources.execute_methods import BeforeExecuteMethod, ExecuteFunction
from exactly_lib_test.test_resources.actions import do_nothing, do_return


class ParserThatRaisesException(sut.ExecutableObjectParser):
    def __init__(self, cause: TextRenderer):
        self.cause = cause

    def apply(self, instructions: Sequence[ActPhaseInstruction]):
        raise ParseException(self.cause)


class ParserThatExpectsSingleInstructionAndRecordsAndReturnsTheTextOfThatInstruction(sut.ExecutableObjectParser):
    def __init__(self, recorder: Dict[phase_step.PhaseStep, str]):
        self.recorder = recorder

    def apply(self, instructions: Sequence[ActPhaseInstruction]):
        instruction = instructions[0]
        assert isinstance(instruction, ActPhaseInstruction)
        source_text = instruction.source_code().text
        self.recorder[phase_step.ACT__PARSE] = source_text
        return SymbolThatRemembersSource(source_text)


class SymbolThatRemembersSource(SymbolUser):
    def __init__(self, source: str):
        self._source = source

    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return []

    @property
    def source(self) -> str:
        return self._source


class SymbolUserWithConstantSymbolReferences(SymbolUser):
    def __init__(self, symbol_usages: Sequence[SymbolUsage]):
        self._symbol_usages = symbol_usages

    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return self._symbol_usages


class ParserWithConstantResult(sut.ExecutableObjectParser):
    def __init__(self, constant_result: SymbolUser):
        self._constant_result = constant_result

    def apply(self, instructions: Sequence[ActPhaseInstruction]) -> SymbolUser:
        return self._constant_result


class ValidatorConstructorThatRaises(Generic[EXECUTABLE_OBJECT], sut.ValidatorConstructor[EXECUTABLE_OBJECT]):
    def construct(self,
                  environment: InstructionEnvironmentForPreSdsStep,
                  executable_object: EXECUTABLE_OBJECT,
                  ) -> Validator:
        raise ValueError('validator_constructor_that_raises')


class ExecutorConstructorThatRaises(Generic[EXECUTABLE_OBJECT], sut.ExecutorConstructor[EXECUTABLE_OBJECT]):
    def construct(self,
                  environment: InstructionEnvironmentForPostSdsStep,
                  os_services: OsServices,
                  executable_object: EXECUTABLE_OBJECT,
                  ) -> Executor:
        raise ValueError('validator_constructor_that_raises')


class ValidatorConstructorThatRecordsStep(Generic[EXECUTABLE_OBJECT],
                                          sut.ValidatorConstructor[EXECUTABLE_OBJECT]):
    def __init__(self, step_recorder: dict):
        self._step_recorder = step_recorder

    def construct(self,
                  environment: InstructionEnvironmentForPreSdsStep,
                  executable_object: EXECUTABLE_OBJECT,
                  ) -> Validator:
        return ValidatorThatRecordsSteps(self._step_recorder, executable_object)


class ExecutorConstructorThatRecordsStep(Generic[EXECUTABLE_OBJECT],
                                         sut.ExecutorConstructor[EXECUTABLE_OBJECT]):
    def __init__(self, step_recorder: dict):
        self._step_recorder = step_recorder

    def construct(self,
                  environment: InstructionEnvironmentForPostSdsStep,
                  os_services: OsServices,
                  executable_object: EXECUTABLE_OBJECT,
                  ) -> Executor:
        return ExecutorThatRecordsSteps(self._step_recorder, executable_object)


class _ExecutorConstructorForConstant(Generic[EXECUTABLE_OBJECT], sut.ExecutorConstructor[EXECUTABLE_OBJECT]):
    def __init__(self, constant: sut.Executor):
        self._constant = constant

    def construct(self,
                  environment: InstructionEnvironmentForPostSdsStep,
                  os_services: OsServices,
                  executable_object: EXECUTABLE_OBJECT,
                  ) -> sut.Executor:
        return self._constant


class UnconditionallySuccessfulExecutor(sut.Executor):
    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                stdin: Optional[StringModel],
                output: StdOutputFiles,
                ) -> int:
        return 0


class ExecutorThat(sut.Executor):
    def __init__(self,
                 prepare: Callable = do_nothing,
                 execute_initial_action: BeforeExecuteMethod = do_nothing,
                 execute: ExecuteFunction = do_return(0),
                 ):
        self._prepare = prepare
        self._execute_initial_action = execute_initial_action
        self._execute = execute

    def prepare(self,
                environment: InstructionEnvironmentForPostSdsStep,
                ):
        self._prepare(environment)

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                stdin: Optional[StringModel],
                output: StdOutputFiles,
                ) -> int:
        self._execute_initial_action(environment, stdin, output)
        return self._execute(environment, stdin, output)


class ValidatorThatRecordsSteps(sut.Validator):
    def __init__(self, recorder: dict,
                 object_with_act_phase_source: SymbolThatRemembersSource):
        self.recorder = recorder
        self.act_phase_source = object_with_act_phase_source.source

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        self.recorder[phase_step.ACT__VALIDATE_PRE_SDS] = self.act_phase_source
        return svh.new_svh_success()

    def validate_post_setup(self, tcds: TestCaseDs) -> svh.SuccessOrValidationErrorOrHardError:
        self.recorder[phase_step.ACT__VALIDATE_POST_SETUP] = self.act_phase_source
        return svh.new_svh_success()


class ExecutorThatRecordsSteps(sut.Executor):
    def __init__(self,
                 recorder: dict,
                 object_with_act_phase_source: SymbolThatRemembersSource):
        self.recorder = recorder
        self.act_phase_source = object_with_act_phase_source.source

    def prepare(self,
                environment: InstructionEnvironmentForPostSdsStep,
                ):
        self.recorder[phase_step.ACT__PREPARE] = self.act_phase_source

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                stdin: Optional[StringModel],
                output: StdOutputFiles,
                ) -> int:
        self.recorder[phase_step.ACT__EXECUTE] = self.act_phase_source
        return 0
