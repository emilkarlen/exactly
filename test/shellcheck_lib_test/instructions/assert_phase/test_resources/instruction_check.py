import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, SingleInstructionParserSource
from shellcheck_lib.test_case.os_services import OsServices, new_default
from shellcheck_lib.test_case.sections import common as i
from shellcheck_lib.test_case.sections.assert_ import AssertPhaseInstruction
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase, GlobalEnvironmentForPreEdsStep
from shellcheck_lib.test_case.sections.result import pfh
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib_test.instructions.test_resources import eds_contents_check
from shellcheck_lib_test.instructions.test_resources import eds_populator
from shellcheck_lib_test.instructions.test_resources import pfh_check
from shellcheck_lib_test.instructions.test_resources import svh_check
from shellcheck_lib_test.instructions.test_resources import utils
from shellcheck_lib_test.instructions.test_resources.arrangement import ArrangementPostAct, ActResultProducer, \
    ActEnvironment
from shellcheck_lib_test.instructions.test_resources.assertion_utils.side_effects import SideEffectsCheck
from shellcheck_lib_test.instructions.test_resources.utils import write_act_result
from shellcheck_lib_test.test_resources import file_structure


def arrangement(home_dir_contents: file_structure.DirContents = file_structure.DirContents([]),
                eds_contents_before_main: eds_populator.EdsPopulator = eds_populator.empty(),
                act_result_producer: ActResultProducer = ActResultProducer(),
                os_services: OsServices = new_default()
                ) -> ArrangementPostAct:
    return ArrangementPostAct(home_dir_contents,
                              eds_contents_before_main,
                              act_result_producer,
                              os_services)


class Expectation:
    def __init__(self,
                 validation_post_eds: svh_check.Assertion = svh_check.is_success(),
                 validation_pre_eds: svh_check.Assertion = svh_check.is_success(),
                 main_result: pfh_check.Assertion = pfh_check.is_pass(),
                 main_side_effects_on_files: eds_contents_check.Assertion = eds_contents_check.AnythingGoes(),
                 side_effects_check: SideEffectsCheck = SideEffectsCheck(),
                 ):
        self.validation_post_eds = validation_post_eds
        self.validation_pre_eds = validation_pre_eds
        self.main_result = main_result
        self.main_side_effects_on_files = main_side_effects_on_files
        self.side_effects_check = side_effects_check


is_pass = Expectation


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

    def execute(self,
                parser: SingleInstructionParser,
                source: SingleInstructionParserSource):
        instruction = parser.apply(source)
        self.put.assertIsNotNone(instruction,
                                 'Result from parser cannot be None')
        self.put.assertIsInstance(instruction,
                                  AssertPhaseInstruction,
                                  'The instruction must be an instance of ' + str(AssertPhaseInstruction))
        assert isinstance(instruction, AssertPhaseInstruction)
        with utils.home_and_eds_and_test_as_curr_dir(
                home_dir_contents=self.arrangement.home_contents,
                eds_contents=self.arrangement.eds_contents) as home_and_eds:
            act_result = self.arrangement.act_result_producer.apply(ActEnvironment(home_and_eds))
            write_act_result(home_and_eds.eds, act_result)
            # TODO Execution of validate/pre-eds should be done before act-result is written.
            # But cannot do this for the moment, since many tests write home-dir contents
            # as part of the act-result.
            environment = i.GlobalEnvironmentForPreEdsStep(home_and_eds.home_dir_path)
            validate_result = self._execute_validate_pre_eds(environment, instruction)
            if not validate_result.is_success:
                return
            environment = i.GlobalEnvironmentForPostEdsPhase(home_and_eds.home_dir_path,
                                                             home_and_eds.eds)
            validate_result = self._execute_validate_post_setup(environment, instruction)
            if not validate_result.is_success:
                return
            self._execute_main(environment, instruction)
            self.expectation.main_side_effects_on_files.apply(self.put, environment.eds)
            self.expectation.side_effects_check.apply(self.put, home_and_eds)

    def _execute_validate_pre_eds(self,
                                  global_environment: GlobalEnvironmentForPreEdsStep,
                                  instruction: AssertPhaseInstruction) -> svh.SuccessOrValidationErrorOrHardError:
        result = instruction.validate_pre_eds(global_environment)
        self.put.assertIsNotNone(result,
                                 'Result from validate method cannot be None')
        self.expectation.validation_pre_eds.apply(self.put, result)
        return result

    def _execute_validate_post_setup(self,
                                     global_environment: GlobalEnvironmentForPostEdsPhase,
                                     instruction: AssertPhaseInstruction) -> svh.SuccessOrValidationErrorOrHardError:
        result = instruction.validate_post_setup(global_environment)
        self.put.assertIsNotNone(result,
                                 'Result from validate method cannot be None')
        self.expectation.validation_post_eds.apply(self.put, result)
        return result

    def _execute_main(self,
                      environment: GlobalEnvironmentForPostEdsPhase,
                      instruction: AssertPhaseInstruction) -> pfh.PassOrFailOrHardError:
        main_result = instruction.main(environment, self.arrangement.os_services)
        self.put.assertIsNotNone(main_result,
                                 'Result from main method cannot be None')
        self.expectation.main_result.apply(self.put, main_result)
        self.expectation.main_side_effects_on_files.apply(self.put, environment.eds)
        return main_result
