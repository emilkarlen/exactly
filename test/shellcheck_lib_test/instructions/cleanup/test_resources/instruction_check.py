import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, SingleInstructionParserSource
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections import common as i
from shellcheck_lib.test_case.sections.cleanup import CleanupPhaseInstruction
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase
from shellcheck_lib.test_case.sections.result import pfh
from shellcheck_lib_test.instructions.test_resources import eds_contents_check
from shellcheck_lib_test.instructions.test_resources import eds_populator
from shellcheck_lib_test.instructions.test_resources import sh_check
from shellcheck_lib_test.instructions.test_resources import utils
from shellcheck_lib_test.instructions.test_resources.utils import write_act_result, SideEffectsCheck
from shellcheck_lib_test.util import file_structure


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
                 main_result: sh_check.Assertion = sh_check.IsSuccess(),
                 main_side_effects_on_files: eds_contents_check.Assertion = eds_contents_check.AnythingGoes(),
                 side_effects_check: SideEffectsCheck = SideEffectsCheck(),
                 ):
        self.act_result = act_result
        self.main_result = main_result
        self.main_side_effects_on_files = main_side_effects_on_files
        self.side_effects_check = side_effects_check


class TestCaseBase(unittest.TestCase):
    def _check(self,
               parser: SingleInstructionParser,
               arrangement: Arrangement,
               expectation: Expectation,
               source: SingleInstructionParserSource):
        execute(self, parser, arrangement, expectation, source)


def execute(put: unittest.TestCase,
            parser: SingleInstructionParser,
            arrangement: Arrangement,
            expectation: Expectation,
            source: SingleInstructionParserSource):
    instruction = parser.apply(source)
    put.assertIsNotNone(instruction,
                        'Result from parser cannot be None')
    put.assertIsInstance(instruction,
                         CleanupPhaseInstruction,
                         'The instruction must be an instance of ' + str(CleanupPhaseInstruction))
    assert isinstance(instruction, CleanupPhaseInstruction)
    with utils.home_and_eds_and_test_as_curr_dir(
            home_dir_contents=arrangement.home_dir_contents,
            eds_contents=arrangement.eds_contents_before_main) as home_and_eds:
        write_act_result(home_and_eds.eds, expectation.act_result)
        environment = i.GlobalEnvironmentForPostEdsPhase(home_and_eds.home_dir_path,
                                                         home_and_eds.eds)
        _execute_main(environment, instruction, put, expectation)
        expectation.main_side_effects_on_files.apply(put, environment.eds)
        expectation.side_effects_check.apply(put, home_and_eds)


def _execute_main(environment: GlobalEnvironmentForPostEdsPhase,
                  instruction: CleanupPhaseInstruction,
                  put: unittest.TestCase,
                  expectation: Expectation) -> pfh.PassOrFailOrHardError:
    main_result = instruction.main(environment, OsServices())
    put.assertIsNotNone(main_result,
                        'Result from main method cannot be None')
    expectation.main_result.apply(put, main_result)
    expectation.main_side_effects_on_files.apply(put, environment.eds)
    return main_result
