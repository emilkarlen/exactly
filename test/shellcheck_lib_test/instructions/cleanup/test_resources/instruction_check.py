import pathlib
import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, SingleInstructionParserSource
from shellcheck_lib.test_case.os_services import OsServices, new_default
from shellcheck_lib.test_case.sections import common as i
from shellcheck_lib.test_case.sections.cleanup import CleanupPhaseInstruction, PreviousPhase
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase, GlobalEnvironmentForPreEdsStep
from shellcheck_lib.test_case.sections.result import pfh
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib_test.instructions.test_resources import sh_check
from shellcheck_lib_test.instructions.test_resources import svh_check
from shellcheck_lib_test.instructions.test_resources.arrangements import ArrangementWithEds
from shellcheck_lib_test.instructions.test_resources.assertion_utils.side_effects import SideEffectsCheck
from shellcheck_lib_test.instructions.test_resources.instruction_check_utils import \
    InstructionExecutionToBeReplacedByVaBase
from shellcheck_lib_test.test_resources import file_structure
from shellcheck_lib_test.test_resources.execution import eds_populator, utils, eds_contents_check


class Arrangement(ArrangementWithEds):
    def __init__(self,
                 home_dir_contents: file_structure.DirContents = file_structure.DirContents([]),
                 eds_contents_before_main: eds_populator.EdsPopulator = eds_populator.empty(),
                 os_services: OsServices = new_default(),
                 previous_phase: PreviousPhase = PreviousPhase.ASSERT):
        super().__init__(home_dir_contents,
                         eds_contents_before_main,
                         os_services)
        self.previous_phase = previous_phase


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
        check(self, parser, source, arrangement, expectation)


def check(put: unittest.TestCase,
          parser: SingleInstructionParser,
          source: SingleInstructionParserSource,
          arrangement: Arrangement,
          expectation: Expectation):
    Executor(put, arrangement, expectation).execute(parser, source)


class Executor(InstructionExecutionToBeReplacedByVaBase):
    def __init__(self,
                 put: unittest.TestCase,
                 arrangement: Arrangement,
                 expectation: Expectation):
        super().__init__(put, arrangement)
        self.arrangement = arrangement
        self.expectation = expectation

    def execute(self,
                parser: SingleInstructionParser,
                source: SingleInstructionParserSource):
        instruction = parser.apply(source)
        self._check_instruction(CleanupPhaseInstruction, instruction)
        assert isinstance(instruction, CleanupPhaseInstruction)
        with utils.home_and_eds_and_test_as_curr_dir(
                home_dir_contents=self.arrangement.home_contents,
                eds_contents=self.arrangement.eds_contents) as home_and_eds:
            result_of_validate_pre_eds = self._execute_pre_validate(home_and_eds.home_dir_path, instruction)
            if not result_of_validate_pre_eds.is_success:
                return
            environment = i.GlobalEnvironmentForPostEdsPhase(home_and_eds.home_dir_path,
                                                             home_and_eds.eds)
            self._execute_main(environment, instruction)
            self.expectation.main_side_effects_on_files.apply(self.put, environment.eds)
            self.expectation.side_effects_check.apply(self.put, home_and_eds)

    def _execute_pre_validate(self,
                              home_dir_path: pathlib.Path,
                              instruction: CleanupPhaseInstruction) -> svh.SuccessOrValidationErrorOrHardError:
        pre_validation_environment = GlobalEnvironmentForPreEdsStep(home_dir_path)
        result = instruction.validate_pre_eds(pre_validation_environment)
        self._check_result_of_validate_pre_eds(result)
        self.expectation.validate_pre_eds_result.apply(self.put, result)
        return result

    def _execute_main(self,
                      environment: GlobalEnvironmentForPostEdsPhase,
                      instruction: CleanupPhaseInstruction) -> pfh.PassOrFailOrHardError:
        result = instruction.main(environment,
                                  self.arrangement.previous_phase,
                                  self.arrangement.os_services)
        self._check_result_of_main__sh(result)
        self.expectation.main_result.apply(self.put, result)
        self.expectation.main_side_effects_on_files.apply(self.put, environment.eds)
        return result
