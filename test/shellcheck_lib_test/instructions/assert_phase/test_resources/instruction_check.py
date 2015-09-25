import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser

from shellcheck_lib.test_case.instruction import common as i

from shellcheck_lib.test_case.instruction.common import GlobalEnvironmentForPostEdsPhase, \
    PhaseEnvironmentForInternalCommands
from shellcheck_lib.test_case.instruction.result import svh
from shellcheck_lib.test_case.instruction.result import pfh
from shellcheck_lib.test_case.instruction.sections.assert_ import AssertPhaseInstruction
from shellcheck_lib_test.util import file_structure
from shellcheck_lib_test.instructions.test_resources import svh_check
from shellcheck_lib_test.instructions.test_resources import pfh_check
from shellcheck_lib_test.instructions.test_resources import eds_populator
from shellcheck_lib_test.instructions.test_resources import eds_contents_check
from shellcheck_lib_test.instructions import utils


class Flow:
    def __init__(self,
                 parser: SingleInstructionParser,
                 home_dir_contents: file_structure.DirContents=file_structure.DirContents([]),
                 eds_contents_before_main: eds_populator.EdsPopulator=eds_populator.Empty(),
                 act_result: utils.ActResult=utils.ActResult(),
                 expected_validation_result: svh_check.Assertion=svh_check.AnythingGoes(),
                 expected_main_result: pfh_check.Assertion=pfh_check.AnythingGoes(),
                 expected_main_side_effects_on_files: eds_contents_check.Assertion=eds_contents_check.AnythingGoes(),
                 ):
        self.parser = parser
        self.home_dir_contents = home_dir_contents
        self.expected_validation_result = expected_validation_result
        self.eds_contents_before_main = eds_contents_before_main
        self.act_result = act_result
        self.expected_main_result = expected_main_result
        self.expected_main_side_effects_on_files = expected_main_side_effects_on_files


class TestCaseBase(unittest.TestCase):
    def _check(self,
               check: Flow,
               source: utils.SingleInstructionParserSource):
        execute(self, check, source)


def execute(put: unittest.TestCase,
            setup: Flow,
            source: utils.SingleInstructionParserSource):
    instruction = setup.parser.apply(source.line_sequence, source.instruction_argument)
    put.assertIsNotNone(instruction,
                        'Result from parser cannot be None')
    put.assertIsInstance(instruction,
                         AssertPhaseInstruction,
                         'The instruction must be an instance of ' + str(AssertPhaseInstruction))
    assert isinstance(instruction, AssertPhaseInstruction)
    with utils.home_and_eds_and_test_as_curr_dir() as home_and_eds:
        home_and_eds.write_act_result(setup.act_result)
        setup.home_dir_contents.write_to(home_and_eds.home_dir_path)
        setup.eds_contents_before_main.apply(home_and_eds.eds)
        environment = i.GlobalEnvironmentForPostEdsPhase(home_and_eds.home_dir_path,
                                                         home_and_eds.eds)
        validate_result = _execute_validate(environment, instruction, put, setup)
        if not validate_result.is_success:
            return
        _execute_main(environment, instruction, put, setup)
        setup.expected_main_side_effects_on_files.apply(put, environment.eds)


def _execute_post_validate(global_environment_with_eds, instruction, put, setup):
    post_validate_result = instruction.post_validate(global_environment_with_eds)
    put.assertIsNotNone(post_validate_result,
                        'Result from post_validate method cannot be None')
    setup.expected_post_validation_result.apply(put, post_validate_result)


def _execute_validate(global_environment: GlobalEnvironmentForPostEdsPhase,
                      instruction: AssertPhaseInstruction,
                      put: unittest.TestCase,
                      setup: Flow) -> svh.SuccessOrValidationErrorOrHardError:
    result = instruction.validate(global_environment)
    put.assertIsNotNone(result,
                        'Result from validate method cannot be None')
    setup.expected_validation_result.apply(put, result)
    return result


def _execute_main(environment: GlobalEnvironmentForPostEdsPhase,
                  instruction: AssertPhaseInstruction,
                  put: unittest.TestCase,
                  setup: Flow) -> pfh.PassOrFailOrHardError:
    main_result = instruction.main(environment,
                                   PhaseEnvironmentForInternalCommands())
    put.assertIsNotNone(main_result,
                        'Result from main method cannot be None')
    setup.expected_main_result.apply(put, main_result)
    setup.expected_main_side_effects_on_files.apply(put, environment.eds)
    return main_result
