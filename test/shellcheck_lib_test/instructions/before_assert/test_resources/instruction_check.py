import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, SingleInstructionParserSource
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections import common as i
from shellcheck_lib.test_case.sections.before_assert import BeforeAssertPhaseInstruction
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase, GlobalEnvironmentForPreEdsStep
from shellcheck_lib.test_case.sections.result import pfh
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib_test.instructions.test_resources import eds_populator
from shellcheck_lib_test.instructions.test_resources import sh_check__va
from shellcheck_lib_test.instructions.test_resources import svh_check__va
from shellcheck_lib_test.instructions.test_resources import utils
from shellcheck_lib_test.instructions.test_resources.arrangement import ArrangementPostAct, ActResultProducer, \
    ActEnvironment
from shellcheck_lib_test.instructions.test_resources.utils import write_act_result
from shellcheck_lib_test.test_resources import file_structure
from shellcheck_lib_test.test_resources import value_assertion as va


def arrangement(home_dir_contents: file_structure.DirContents = file_structure.DirContents([]),
                eds_contents_before_main: eds_populator.EdsPopulator = eds_populator.empty(),
                act_result_producer: ActResultProducer = ActResultProducer()
                ) -> ArrangementPostAct:
    return ArrangementPostAct(home_dir_contents,
                              eds_contents_before_main,
                              act_result_producer)


class Expectation:
    def __init__(self,
                 validation_pre_eds: va.ValueAssertion = svh_check__va.is_success(),
                 validation_post_setup: va.ValueAssertion = svh_check__va.is_success(),
                 main_result: va.ValueAssertion = sh_check__va.is_success(),
                 main_side_effects_on_files: va.ValueAssertion = va.anything_goes(),
                 home_and_eds: va.ValueAssertion = va.anything_goes(),
                 ):
        self.validation_pre_eds = svh_check__va.is_svh_and(validation_pre_eds)
        self.validation_post_setup = svh_check__va.is_svh_and(validation_post_setup)
        self.main_result = sh_check__va.is_sh_and(main_result)
        self.main_side_effects_on_files = main_side_effects_on_files
        self.side_effects_check = home_and_eds


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


class Executor:
    def __init__(self,
                 put: unittest.TestCase,
                 arrangement: ArrangementPostAct,
                 expectation: Expectation):
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
        self._check('instruction',
                    va.IsInstance(BeforeAssertPhaseInstruction),
                    instruction)
        assert isinstance(instruction, BeforeAssertPhaseInstruction)
        with utils.home_and_eds_and_test_as_curr_dir(
                home_dir_contents=self.arrangement.home_contents,
                eds_contents=self.arrangement.eds_contents) as home_and_eds:
            environment = i.GlobalEnvironmentForPreEdsStep(home_and_eds.home_dir_path)
            validate_result = self._execute_validate_pre_eds(environment, instruction)
            if not validate_result.is_success:
                return
            environment = i.GlobalEnvironmentForPostEdsPhase(home_and_eds.home_dir_path,
                                                             home_and_eds.eds)
            validate_result = self._execute_validate_post_setup(environment, instruction)
            if not validate_result.is_success:
                return

            act_result = self.arrangement.act_result_producer.apply(ActEnvironment(home_and_eds))
            write_act_result(home_and_eds.eds, act_result)

            self._execute_main(environment, instruction)
            self._check('EDS contents',
                        self.expectation.main_side_effects_on_files,
                        environment.eds)
            self._check('contents of HomeAndEds',
                        self.expectation.side_effects_check,
                        home_and_eds)

    def _execute_validate_pre_eds(
            self,
            global_environment: GlobalEnvironmentForPreEdsStep,
            instruction: BeforeAssertPhaseInstruction) -> svh.SuccessOrValidationErrorOrHardError:
        result = instruction.validate_pre_eds(global_environment)
        self._check('result from validate/pre-eds',
                    self.expectation.validation_pre_eds,
                    result)
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
        result = instruction.main(OsServices(), environment)
        self._check('result from main',
                    self.expectation.main_result,
                    result)
        return result
