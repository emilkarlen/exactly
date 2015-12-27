import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, SingleInstructionParserSource
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections import common as i
from shellcheck_lib.test_case.sections.assert_ import AssertPhaseInstruction
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase
from shellcheck_lib.test_case.sections.result import pfh
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib_test.instructions.test_resources import eds_contents_check
from shellcheck_lib_test.instructions.test_resources import eds_populator
from shellcheck_lib_test.instructions.test_resources import pfh_check
from shellcheck_lib_test.instructions.test_resources import svh_check
from shellcheck_lib_test.instructions.test_resources import utils
from shellcheck_lib_test.instructions.test_resources.utils import write_act_result, SideEffectsCheck
from shellcheck_lib_test.util import file_structure


class ActEnvironment(tuple):
    def __new__(cls,
                home_and_eds: i.HomeAndEds):
        return tuple.__new__(cls, (home_and_eds,))

    @property
    def home_and_eds(self) -> i.HomeAndEds:
        return self[0]


class ActResultProducer:
    def __init__(self, act_result: utils.ActResult = utils.ActResult()):
        self.act_result = act_result

    def apply(self, act_environment: ActEnvironment) -> utils.ActResult:
        return self.act_result


class Flow:
    def __init__(self,
                 parser: SingleInstructionParser,
                 home_dir_contents: file_structure.DirContents = file_structure.DirContents([]),
                 eds_contents_before_main: eds_populator.EdsPopulator = eds_populator.empty(),
                 act_result_producer: ActResultProducer = ActResultProducer(),
                 expected_validation_result: svh_check.Assertion = svh_check.is_success(),
                 expected_main_result: pfh_check.Assertion = pfh_check.is_pass(),
                 expected_main_side_effects_on_files: eds_contents_check.Assertion = eds_contents_check.AnythingGoes(),
                 side_effects_check: SideEffectsCheck = SideEffectsCheck(),
                 ):
        self.parser = parser
        self.home_dir_contents = home_dir_contents
        self.expected_validation_result = expected_validation_result
        self.eds_contents_before_main = eds_contents_before_main
        self.act_result_producer = act_result_producer
        self.expected_main_result = expected_main_result
        self.expected_main_side_effects_on_files = expected_main_side_effects_on_files
        self.side_effects_check = side_effects_check


class Arrangement:
    def __init__(self,
                 home_dir_contents: file_structure.DirContents = file_structure.DirContents([]),
                 eds_contents_before_main: eds_populator.EdsPopulator = eds_populator.empty(),
                 act_result_producer: ActResultProducer = ActResultProducer(),
                 ):
        self.home_dir_contents = home_dir_contents
        self.eds_contents_before_main = eds_contents_before_main
        self.act_result_producer = act_result_producer


class Expectation:
    def __init__(self,
                 expected_validation_result: svh_check.Assertion = svh_check.is_success(),
                 expected_main_result: pfh_check.Assertion = pfh_check.is_pass(),
                 expected_main_side_effects_on_files: eds_contents_check.Assertion = eds_contents_check.AnythingGoes(),
                 side_effects_check: SideEffectsCheck = SideEffectsCheck(),
                 ):
        self.expected_validation_result = expected_validation_result
        self.expected_main_result = expected_main_result
        self.expected_main_side_effects_on_files = expected_main_side_effects_on_files
        self.side_effects_check = side_effects_check


success = Expectation


class TestCaseBase(unittest.TestCase):
    def _chekk(self,
               check: Flow,
               source: SingleInstructionParserSource):
        self._check(check.parser,
                    source,
                    Arrangement(
                            home_dir_contents=check.home_dir_contents,
                            eds_contents_before_main=check.eds_contents_before_main,
                            act_result_producer=check.act_result_producer),

                    Expectation(
                            expected_validation_result=check.expected_validation_result,
                            expected_main_result=check.expected_main_result,
                            expected_main_side_effects_on_files=check.expected_main_side_effects_on_files,
                            side_effects_check=check.side_effects_check))

    def _check(self,
               parser: SingleInstructionParser,
               source: SingleInstructionParserSource,
               arrangement: Arrangement,
               expectation: Expectation):
        Executor(self, arrangement, expectation).execute(parser, source)


class Executor:
    def __init__(self,
                 put: unittest.TestCase,
                 arrangement: Arrangement,
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
                home_dir_contents=self.arrangement.home_dir_contents,
                eds_contents=self.arrangement.eds_contents_before_main) as home_and_eds:
            act_result = self.arrangement.act_result_producer.apply(ActEnvironment(home_and_eds))
            write_act_result(home_and_eds.eds, act_result)

            environment = i.GlobalEnvironmentForPostEdsPhase(home_and_eds.home_dir_path,
                                                             home_and_eds.eds)
            validate_result = self._execute_validate(environment, instruction)
            if not validate_result.is_success:
                return
            self._execute_main(environment, instruction)
            self.expectation.expected_main_side_effects_on_files.apply(self.put, environment.eds)
            self.expectation.side_effects_check.apply(self.put, home_and_eds)

    def _execute_validate(self,
                          global_environment: GlobalEnvironmentForPostEdsPhase,
                          instruction: AssertPhaseInstruction) -> svh.SuccessOrValidationErrorOrHardError:
        result = instruction.validate(global_environment)
        self.put.assertIsNotNone(result,
                                 'Result from validate method cannot be None')
        self.expectation.expected_validation_result.apply(self.put, result)
        return result

    def _execute_main(self,
                      environment: GlobalEnvironmentForPostEdsPhase,
                      instruction: AssertPhaseInstruction) -> pfh.PassOrFailOrHardError:
        main_result = instruction.main(environment, OsServices())
        self.put.assertIsNotNone(main_result,
                                 'Result from main method cannot be None')
        self.expectation.expected_main_result.apply(self.put, main_result)
        self.expectation.expected_main_side_effects_on_files.apply(self.put, environment.eds)
        return main_result
