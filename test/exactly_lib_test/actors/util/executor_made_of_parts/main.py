import unittest
from typing import Sequence, Dict, Generic

from exactly_lib.actors.util.executor_made_of_parts import parts as sut
from exactly_lib.actors.util.executor_made_of_parts.parts import EXECUTABLE_OBJECT, Executor, Validator
from exactly_lib.execution import phase_step
from exactly_lib.symbol.data.restrictions.reference_restrictions import is_any_data_type
from exactly_lib.symbol.sdv_structure import SymbolUsage, SymbolReference
from exactly_lib.test_case.actor import ParseException, AtcOsProcessExecutor
from exactly_lib.test_case.phases.act import ActPhaseInstruction
from exactly_lib.test_case.phases.common import SymbolUser
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.result import sh, svh, eh
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.util.file_utils.std import StdFiles
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib_test.actors.test_resources.integration_check import Arrangement, simple_success, \
    check_execution, Expectation
from exactly_lib_test.symbol.data.restrictions.test_resources import concrete_restriction_assertion
from exactly_lib_test.symbol.test_resources import symbol_reference_assertions as asrt_sym_ref
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_hds
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestConstructor))
    return ret_val


class TestConstructor(unittest.TestCase):
    def test_WHEN_parser_raises_exception_THEN_parse_SHOULD_raise_this_exception(self):
        # ARRANGE #
        parser_error = svh.new_svh_validation_error__str('msg')
        parser = sut.ActorFromParts(ParserThatRaisesException(parser_error),
                                    ValidatorConstructorThatRaises(),
                                    ExecutorConstructorThatRaises())
        act_phase_instructions = []
        # ACT #
        with self.assertRaises(ParseException) as ex:
            executor = parser.parse(act_phase_instructions)
            # ASSERT #
            self.assertIs(parser_error, ex)

    def test_full_sequence_of_steps(self):
        # ARRANGE #
        step_recorder = dict()
        parser = ParserThatExpectsSingleInstructionAndRecordsAndReturnsTheTextOfThatInstruction(step_recorder)

        parser = sut.ActorFromParts(parser,
                                    ValidatorConstructorThatRecordsStep(step_recorder),
                                    ExecutorConstructorThatRecordsStep(step_recorder))
        act_phase_instructions = [instr(['act phase source'])]
        arrangement = Arrangement()
        expectation = simple_success()
        # ACT (and assert that all methods indicate success) #
        check_execution(self,
                        parser,
                        act_phase_instructions,
                        arrangement,
                        expectation)
        # ASSERT #
        expected_recordings = {
            phase_step.ACT__PARSE: 'act phase source',
            phase_step.ACT__VALIDATE_PRE_SDS: 'act phase source',
            phase_step.ACT__VALIDATE_POST_SETUP: 'act phase source',
            phase_step.ACT__PREPARE: 'act phase source',
            phase_step.ACT__EXECUTE: 'act phase source',
        }
        self.assertDictEqual(expected_recordings,
                             step_recorder)

    def test_symbol_usages_of_object_returned_by_parser_SHOULD_be_reported(self):
        # ARRANGE #
        symbol_reference = NameAndValue('symbol_name',
                                        is_any_data_type())
        expected_symbol_references = [
            SymbolReference(symbol_reference.name,
                            symbol_reference.value)
        ]
        parser = sut.ActorFromParts(
            ParserWithConstantResult(
                SymbolUserWithConstantSymbolReferences(expected_symbol_references)
            ),
            sut.UnconditionallySuccessfulValidatorConstructor(),
            _ExecutorConstructorForConstant(UnconditionallySuccessfulExecutor()),
        )
        # ACT & ASSERT #
        check_execution(self,
                        parser,
                        [],
                        Arrangement(),
                        Expectation(
                            symbol_usages=asrt.matches_sequence([
                                asrt_sym_ref.matches_reference_2(
                                    symbol_reference.name,
                                    concrete_restriction_assertion.equals_data_type_reference_restrictions(
                                        symbol_reference.value)
                                )
                            ])
                        ))


def _environment() -> InstructionEnvironmentForPreSdsStep:
    hds = fake_hds()
    return InstructionEnvironmentForPreSdsStep(hds, ProcessExecutionSettings.with_empty_environ())


class ParserThatRaisesException(sut.ExecutableObjectParser):
    def __init__(self, cause: svh.SuccessOrValidationErrorOrHardError):
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
                  process_executor: AtcOsProcessExecutor,
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
                  process_executor: AtcOsProcessExecutor,
                  executable_object: EXECUTABLE_OBJECT,
                  ) -> Executor:
        return ExecutorThatRecordsSteps(self._step_recorder, executable_object)


class _ExecutorConstructorForConstant(Generic[EXECUTABLE_OBJECT], sut.ExecutorConstructor[EXECUTABLE_OBJECT]):
    def __init__(self, constant: sut.Executor):
        self._constant = constant

    def construct(self,
                  environment: InstructionEnvironmentForPostSdsStep,
                  process_executor: AtcOsProcessExecutor,
                  executable_object: EXECUTABLE_OBJECT,
                  ) -> sut.Executor:
        return self._constant


class UnconditionallySuccessfulExecutor(sut.Executor):
    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                std_files: StdFiles) -> eh.ExitCodeOrHardError:
        return eh.new_eh_exit_code(0)


class ValidatorThatRecordsSteps(sut.Validator):
    def __init__(self, recorder: dict,
                 object_with_act_phase_source: SymbolThatRemembersSource):
        self.recorder = recorder
        self.act_phase_source = object_with_act_phase_source.source

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        self.recorder[phase_step.ACT__VALIDATE_PRE_SDS] = self.act_phase_source
        return svh.new_svh_success()

    def validate_post_setup(self, tcds: Tcds) -> svh.SuccessOrValidationErrorOrHardError:
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
                ) -> sh.SuccessOrHardError:
        self.recorder[phase_step.ACT__PREPARE] = self.act_phase_source
        return sh.new_sh_success()

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                std_files: StdFiles,
                ) -> eh.ExitCodeOrHardError:
        self.recorder[phase_step.ACT__EXECUTE] = self.act_phase_source
        return eh.new_eh_exit_code(0)
