import pathlib
import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, SingleInstructionParserSource
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections import common as i
from shellcheck_lib.test_case.sections.cleanup import CleanupPhaseInstruction
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase, GlobalEnvironmentForPreEdsStep
from shellcheck_lib.test_case.sections.result import pfh
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib_test.instructions.test_resources import eds_contents_check
from shellcheck_lib_test.instructions.test_resources import eds_populator
from shellcheck_lib_test.instructions.test_resources import sh_check
from shellcheck_lib_test.instructions.test_resources import svh_check
from shellcheck_lib_test.instructions.test_resources import utils
from shellcheck_lib_test.instructions.test_resources.utils import write_act_result, SideEffectsCheck
from shellcheck_lib_test.test_resources import file_structure


class Arrangement:
    def __init__(self,
                 home_dir_contents: file_structure.DirContents = file_structure.DirContents([]),
                 eds_contents_before_main: eds_populator.EdsPopulator = eds_populator.empty(),
                 ):
        self.home_dir_contents = home_dir_contents
        self.eds_contents_before_main = eds_contents_before_main


class Expectation:
    def __init__(self,
                 act_result: utils.ActResult = utils.ActResult(),
                 validate_pre_eds_result: svh_check.Assertion = svh_check.is_success(),
                 main_result: sh_check.Assertion = sh_check.IsSuccess(),
                 main_side_effects_on_files: eds_contents_check.Assertion = eds_contents_check.AnythingGoes(),
                 side_effects_check: SideEffectsCheck = SideEffectsCheck(),
                 ):
        self.act_result = act_result
        self.validate_pre_eds_result = validate_pre_eds_result
        self.main_result = main_result
        self.main_side_effects_on_files = main_side_effects_on_files
        self.side_effects_check = side_effects_check


is_success = Expectation


class TestCaseBase(unittest.TestCase):
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
                                  CleanupPhaseInstruction,
                                  'The instruction must be an instance of ' + str(CleanupPhaseInstruction))
        assert isinstance(instruction, CleanupPhaseInstruction)
        with utils.home_and_eds_and_test_as_curr_dir(
                home_dir_contents=self.arrangement.home_dir_contents,
                eds_contents=self.arrangement.eds_contents_before_main) as home_and_eds:
            write_act_result(home_and_eds.eds, self.expectation.act_result)
            self._execute_pre_validate(home_and_eds.home_dir_path, instruction)
            environment = i.GlobalEnvironmentForPostEdsPhase(home_and_eds.home_dir_path,
                                                             home_and_eds.eds)
            self._execute_main(environment, instruction)
            self.expectation.main_side_effects_on_files.apply(self.put, environment.eds)
            self.expectation.side_effects_check.apply(self.put, home_and_eds)

    def _execute_pre_validate(self,
                              home_dir_path: pathlib.Path,
                              instruction: CleanupPhaseInstruction) -> svh.SuccessOrValidationErrorOrHardError:
        pre_validation_environment = GlobalEnvironmentForPreEdsStep(home_dir_path)
        pre_validate_result = instruction.validate_pre_eds(pre_validation_environment)
        self.put.assertIsInstance(pre_validate_result,
                                  svh.SuccessOrValidationErrorOrHardError,
                                  'pre_validate must return a ' + str(svh.SuccessOrValidationErrorOrHardError))
        self.put.assertIsNotNone(pre_validate_result,
                                 'Result from pre_validate method cannot be None')
        self.expectation.validate_pre_eds_result.apply(self.put, pre_validate_result)
        return pre_validate_result

    def _execute_main(self,
                      environment: GlobalEnvironmentForPostEdsPhase,
                      instruction: CleanupPhaseInstruction) -> pfh.PassOrFailOrHardError:
        main_result = instruction.main(environment, OsServices())
        self.put.assertIsNotNone(main_result,
                                 'Result from main method cannot be None')
        self.expectation.main_result.apply(self.put, main_result)
        self.expectation.main_side_effects_on_files.apply(self.put, environment.eds)
        return main_result
