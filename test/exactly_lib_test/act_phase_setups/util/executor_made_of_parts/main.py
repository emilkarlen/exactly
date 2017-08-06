import pathlib
import pathlib
import unittest

from exactly_lib.act_phase_setups.util.executor_made_of_parts import parts as sut
from exactly_lib.execution.phase_step_identifiers import phase_step
from exactly_lib.symbol.restrictions.reference_restrictions import no_restrictions
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case import eh
from exactly_lib.test_case.act_phase_handling import ParseException
from exactly_lib.test_case.os_services import ACT_PHASE_OS_PROCESS_EXECUTOR
from exactly_lib.test_case.phases.act import ActPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep, SymbolUser
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.util.std import StdFiles
from exactly_lib_test.act_phase_setups.test_resources.act_phase_execution import Arrangement, simple_success, \
    check_execution, Expectation
from exactly_lib_test.symbol.test_resources.symbol_reference_assertions import equals_symbol_references
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_hds


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestConstructor))
    return ret_val


class TestConstructor(unittest.TestCase):
    def test_WHEN_parser_raises_exception_THEN_parse_SHOULD_raise_this_exception(self):
        # ARRANGE #
        parser_error = svh.new_svh_validation_error('msg')
        constructor = sut.Constructor(ParserThatRaisesException(parser_error),
                                      validator_constructor_that_raises,
                                      executor_constructor_that_raises)
        environment = _environment()
        act_phase_instructions = []
        # ACT #
        executor = constructor.apply(ACT_PHASE_OS_PROCESS_EXECUTOR, environment, act_phase_instructions)
        with self.assertRaises(ParseException) as ex:
            executor.parse(environment)
            # ASSERT #
            self.assertIs(parser_error, ex)

    def test_full_sequence_of_steps(self):
        # ARRANGE #
        step_recorder = dict()
        parser = ParserThatExpectsSingleInstructionAndRecordsAndReturnsTheTextOfThatInstruction(step_recorder)

        def validator_constructor(environment, x):
            return ValidatorThatRecordsSteps(step_recorder, x)

        def executor_constructor(os_process_executor, environment, x):
            return ExecutorThatRecordsSteps(step_recorder, x)

        constructor = sut.Constructor(parser,
                                      validator_constructor,
                                      executor_constructor)
        act_phase_instructions = [instr(['act phase source'])]
        arrangement = Arrangement()
        expectation = simple_success()
        # ACT (and assert that all methods indicate success) #
        check_execution(self, constructor,
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
        expected_symbol_references = [
            SymbolReference('symbol_name',
                            no_restrictions())
        ]
        constructor = sut.Constructor(ParserWithConstantResult(
            SymbolUserWithConstantSymbolReferences(expected_symbol_references)),
            lambda *x: sut.UnconditionallySuccessfulValidator(),
            lambda *x: UnconditionallySuccessfulExecutor())
        # ACT & ASSERT #
        check_execution(self, constructor,
                        [],
                        Arrangement(),
                        Expectation(
                            symbol_usages=equals_symbol_references(expected_symbol_references)
                        ))


def _environment() -> InstructionEnvironmentForPreSdsStep:
    hds = fake_hds()
    return InstructionEnvironmentForPreSdsStep(hds, {})


class ParserThatRaisesException(sut.Parser):
    def __init__(self, cause: svh.SuccessOrValidationErrorOrHardError):
        self.cause = cause

    def apply(self, act_phase_instructions: list):
        raise ParseException(self.cause)


class ParserThatExpectsSingleInstructionAndRecordsAndReturnsTheTextOfThatInstruction(sut.Parser):
    def __init__(self, recorder: dict):
        self.recorder = recorder

    def apply(self, act_phase_instructions: list):
        instruction = act_phase_instructions[0]
        assert isinstance(instruction, ActPhaseInstruction)
        source_text = instruction.source_code().text
        self.recorder[phase_step.ACT__PARSE] = source_text
        return SymbolThatRemembersSource(source_text)


class SymbolThatRemembersSource(SymbolUser):
    def __init__(self, source: str):
        self._source = source

    def symbol_usages(self) -> list:
        return []

    @property
    def source(self) -> str:
        return self._source


class SymbolUserWithConstantSymbolReferences(SymbolUser):
    def __init__(self, symbol_usages: list):
        self._symbol_usages = symbol_usages

    def symbol_usages(self) -> list:
        return self._symbol_usages


class ParserWithConstantResult(sut.Parser):
    def __init__(self, constant_result: SymbolUser):
        self._constant_result = constant_result

    def apply(self, act_phase_instructions: list) -> SymbolUser:
        return self._constant_result


def validator_constructor_that_raises(*args):
    raise ValueError('validator_constructor_that_raises')


def executor_constructor_that_raises(*args):
    raise ValueError('executor_constructor_that_raises')


class UnconditionallySuccessfulExecutor(sut.Executor):
    def execute(self,
                environment: sut.InstructionEnvironmentForPostSdsStep,
                script_output_dir_path: pathlib.Path,
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

    def validate_post_setup(self, home_and_sds: HomeAndSds) -> svh.SuccessOrValidationErrorOrHardError:
        self.recorder[phase_step.ACT__VALIDATE_POST_SETUP] = self.act_phase_source
        return svh.new_svh_success()


class ExecutorThatRecordsSteps(sut.Executor):
    def __init__(self, recorder: dict,
                 object_with_act_phase_source: SymbolThatRemembersSource):
        self.recorder = recorder
        self.act_phase_source = object_with_act_phase_source.source

    def prepare(self, home_and_sds: HomeAndSds, script_output_dir_path: pathlib.Path) -> sh.SuccessOrHardError:
        self.recorder[phase_step.ACT__PREPARE] = self.act_phase_source
        return sh.new_sh_success()

    def execute(self, home_and_sds: HomeAndSds, script_output_dir_path: pathlib.Path,
                std_files: StdFiles) -> eh.ExitCodeOrHardError:
        self.recorder[phase_step.ACT__EXECUTE] = self.act_phase_source
        return eh.new_eh_exit_code(0)
