import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, SingleInstructionParserSource
from shellcheck_lib.test_case.instruction import common as i
from shellcheck_lib.test_case.instruction.common import GlobalEnvironmentForPostEdsPhase, \
    PhaseEnvironmentForInternalCommands
from shellcheck_lib.test_case.instruction.result import pfh
from shellcheck_lib.test_case.instruction.sections.cleanup import CleanupPhaseInstruction
from shellcheck_lib_test.util import file_structure
from shellcheck_lib_test.instructions.test_resources import sh_check
from shellcheck_lib_test.instructions.test_resources import eds_populator
from shellcheck_lib_test.instructions.test_resources import eds_contents_check
from shellcheck_lib_test.instructions import utils


class Flow:
    def __init__(self,
                 parser: SingleInstructionParser,
                 home_dir_contents: file_structure.DirContents=file_structure.DirContents([]),
                 eds_contents_before_main: eds_populator.EdsPopulator=eds_populator.Empty(),
                 act_result: utils.ActResult=utils.ActResult(),
                 expected_main_result: sh_check.Assertion=sh_check.AnythingGoes(),
                 expected_main_side_effects_on_files: eds_contents_check.Assertion=eds_contents_check.AnythingGoes(),
                 ):
        self.parser = parser
        self.home_dir_contents = home_dir_contents
        self.eds_contents_before_main = eds_contents_before_main
        self.act_result = act_result
        self.expected_main_result = expected_main_result
        self.expected_main_side_effects_on_files = expected_main_side_effects_on_files


class TestCaseBase(unittest.TestCase):
    def _check(self,
               check: Flow,
               source: SingleInstructionParserSource):
        execute(self, check, source)


def execute(put: unittest.TestCase,
            setup: Flow,
            source: SingleInstructionParserSource):
    instruction = setup.parser.apply(source)
    put.assertIsNotNone(instruction,
                        'Result from parser cannot be None')
    put.assertIsInstance(instruction,
                         CleanupPhaseInstruction,
                         'The instruction must be an instance of ' + str(CleanupPhaseInstruction))
    assert isinstance(instruction, CleanupPhaseInstruction)
    with utils.home_and_eds_and_test_as_curr_dir() as home_and_eds:
        home_and_eds.write_act_result(setup.act_result)
        setup.home_dir_contents.write_to(home_and_eds.home_dir_path)
        setup.eds_contents_before_main.apply(home_and_eds.eds)
        environment = i.GlobalEnvironmentForPostEdsPhase(home_and_eds.home_dir_path,
                                                         home_and_eds.eds)
        _execute_main(environment, instruction, put, setup)
        setup.expected_main_side_effects_on_files.apply(put, environment.eds)


def _execute_main(environment: GlobalEnvironmentForPostEdsPhase,
                  instruction: CleanupPhaseInstruction,
                  put: unittest.TestCase,
                  setup: Flow) -> pfh.PassOrFailOrHardError:
    main_result = instruction.main(environment,
                                   PhaseEnvironmentForInternalCommands())
    put.assertIsNotNone(main_result,
                        'Result from main method cannot be None')
    setup.expected_main_result.apply(put, main_result)
    setup.expected_main_side_effects_on_files.apply(put, environment.eds)
    return main_result
