import unittest

from exactly_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, SingleInstructionParserSource
from exactly_lib.execution import phases
from exactly_lib.test_case.os_services import OsServices, new_default
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.before_assert import BeforeAssertPhaseInstruction
from exactly_lib.test_case.phases.common import GlobalEnvironmentForPostEdsPhase, GlobalEnvironmentForPreEdsStep
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.test_case.phases.result import svh
from shellcheck_lib_test.instructions.test_resources import sh_check__va
from shellcheck_lib_test.instructions.test_resources import svh_check__va
from shellcheck_lib_test.instructions.test_resources.arrangements import ArrangementPostAct, ActResultProducer, \
    ActEnvironment
from shellcheck_lib_test.instructions.test_resources.expectations import ExpectationBase
from shellcheck_lib_test.instructions.test_resources.instruction_check_utils import InstructionExecutionBase
from shellcheck_lib_test.test_resources import file_structure
from shellcheck_lib_test.test_resources import value_assertion as va
from shellcheck_lib_test.test_resources.execution import eds_populator, utils
from shellcheck_lib_test.test_resources.execution.utils import write_act_result


def arrangement(home_dir_contents: file_structure.DirContents = file_structure.DirContents([]),
                eds_contents_before_main: eds_populator.EdsPopulator = eds_populator.empty(),
                act_result_producer: ActResultProducer = ActResultProducer(),
                os_services: OsServices = new_default()
                ) -> ArrangementPostAct:
    return ArrangementPostAct(home_dir_contents,
                              eds_contents_before_main,
                              act_result_producer,
                              os_services)


class Expectation(ExpectationBase):
    def __init__(self, validation_pre_eds: va.ValueAssertion = svh_check__va.is_success(),
                 validation_post_setup: va.ValueAssertion = svh_check__va.is_success(),
                 main_result: va.ValueAssertion = sh_check__va.is_success(),
                 main_side_effects_on_files: va.ValueAssertion = va.anything_goes(),
                 home_and_eds: va.ValueAssertion = va.anything_goes()):
        super().__init__(validation_pre_eds, main_side_effects_on_files, home_and_eds)
        self.validation_post_setup = validation_post_setup
        self.main_result = sh_check__va.is_sh_and(main_result)


is_success = Expectation


class TestCaseBase(unittest.TestCase):
    def _check(self,
               parser: SingleInstructionParser,
               source: SingleInstructionParserSource,
               arrangement: ArrangementPostAct,
               expectation: Expectation):
        check(self, parser, source, arrangement, expectation)


def check(put: unittest.TestCase,
          parser: SingleInstructionParser,
          source: SingleInstructionParserSource,
          arrangement: ArrangementPostAct,
          expectation: Expectation):
    Executor(put, arrangement, expectation).execute(parser, source)


class Executor(InstructionExecutionBase):
    def __init__(self,
                 put: unittest.TestCase,
                 arrangement: ArrangementPostAct,
                 expectation: Expectation):
        super().__init__(put, arrangement, expectation)
        self.put = put
        self.arrangement = arrangement
        self.expectation = expectation
        self.message_builder = va.MessageBuilder()

    def _check(self,
               component: str,
               assertion: va.ValueAssertion,
               actual):
        assertion.apply(self.put,
                        actual,
                        va.MessageBuilder(component))
        return actual

    def execute(self,
                parser: SingleInstructionParser,
                source: SingleInstructionParserSource):
        instruction = parser.apply(source)
        self._check_instruction(BeforeAssertPhaseInstruction, instruction)
        assert isinstance(instruction, BeforeAssertPhaseInstruction)
        with utils.home_and_eds_and_test_as_curr_dir(
                home_dir_contents=self.arrangement.home_contents,
                eds_contents=self.arrangement.eds_contents) as home_and_eds:
            environment = i.GlobalEnvironmentForPreEdsStep(home_and_eds.home_dir_path)
            validate_result = self._execute_validate_pre_eds(environment, instruction)
            if not validate_result.is_success:
                return
            environment = i.GlobalEnvironmentForPostEdsPhase(home_and_eds.home_dir_path,
                                                             home_and_eds.eds,
                                                             phases.BEFORE_ASSERT.identifier)
            validate_result = self._execute_validate_post_setup(environment, instruction)
            if not validate_result.is_success:
                return

            act_result = self.arrangement.act_result_producer.apply(ActEnvironment(home_and_eds))
            write_act_result(home_and_eds.eds, act_result)

            self._execute_main(environment, instruction)
            self._check_main_side_effects_on_files(home_and_eds)
            self._check_side_effects_on_home_and_eds(home_and_eds)

    def _execute_validate_pre_eds(
            self,
            global_environment: GlobalEnvironmentForPreEdsStep,
            instruction: BeforeAssertPhaseInstruction) -> svh.SuccessOrValidationErrorOrHardError:
        result = instruction.validate_pre_eds(global_environment)
        self._check_result_of_validate_pre_eds(result)
        return result

    def _execute_validate_post_setup(
            self,
            global_environment: GlobalEnvironmentForPostEdsPhase,
            instruction: BeforeAssertPhaseInstruction) -> svh.SuccessOrValidationErrorOrHardError:
        result = instruction.validate_post_setup(global_environment)
        self._check('result from validate/post-setup',
                    self.expectation.validation_post_setup,
                    result)
        return result

    def _execute_main(self,
                      environment: GlobalEnvironmentForPostEdsPhase,
                      instruction: BeforeAssertPhaseInstruction) -> pfh.PassOrFailOrHardError:
        result = instruction.main(environment, self.arrangement.os_services)
        self._check('result from main',
                    self.expectation.main_result,
                    result)
        return result
