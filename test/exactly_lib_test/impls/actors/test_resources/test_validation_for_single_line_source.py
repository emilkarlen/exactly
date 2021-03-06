import pathlib
import unittest
from typing import Sequence

from exactly_lib.test_case.phases.act.actor import Actor, ParseException
from exactly_lib.test_case.phases.act.instruction import ActPhaseInstruction
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep
from exactly_lib_test.impls.actors.test_resources.action_to_check import Configuration
from exactly_lib_test.tcfs.test_resources.fake_ds import fake_hds
from exactly_lib_test.tcfs.test_resources.hds_populators import hds_case_dir_contents
from exactly_lib_test.tcfs.test_resources.hds_utils import home_directory_structure
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_case.test_resources.instruction_environment import InstructionEnvironmentPreSdsBuilder
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_dir_contents
from exactly_lib_test.test_resources.programs.python_program_execution import abs_path_to_interpreter_quoted_for_exactly


def suite_for(conf: Configuration) -> unittest.TestSuite:
    test_cases = [
        test_fails_when_there_are_no_instructions,
        test_fails_when_there_is_more_than_one_instruction,
        test_fails_when_there_are_no_statements,
        test_fails_when_there_is_more_than_one_statement,
    ]
    return unittest.TestSuite([tc(conf) for tc in test_cases])


class TestCaseForConfigurationForValidation(unittest.TestCase):
    def __init__(self, configuration: Configuration):
        super().__init__()
        self.conf = configuration
        self.actor = configuration.actor
        assert isinstance(self.actor, Actor)
        self.home_dir_as_current_dir = pathlib.Path()

    def runTest(self):
        raise NotImplementedError()

    @staticmethod
    def _new_environment() -> InstructionEnvironmentForPreSdsStep:
        hds = fake_hds()
        return InstructionEnvironmentPreSdsBuilder.of_empty_env(hds).build

    def _do_parse(self, instructions: Sequence[ActPhaseInstruction]):
        self.actor.parse(instructions)

    def _do_parse_and_validate_pre_sds(self,
                                       instructions: Sequence[ActPhaseInstruction],
                                       home_dir_contents: DirContents = empty_dir_contents()
                                       ):
        with home_directory_structure(
                contents=hds_case_dir_contents(home_dir_contents)) as hds:
            pre_sds_env = InstructionEnvironmentPreSdsBuilder.of_empty_env(hds=hds).build
            executor = self.actor.parse(instructions)
            return executor.validate_pre_sds(pre_sds_env)


class test_fails_when_there_are_no_instructions(TestCaseForConfigurationForValidation):
    def runTest(self):
        act_phase_instructions = []
        with self.assertRaises(ParseException):
            self._do_parse(act_phase_instructions)


class test_fails_when_there_is_more_than_one_instruction(TestCaseForConfigurationForValidation):
    def runTest(self):
        act_phase_instructions = [instr(['']),
                                  instr([''])]
        with self.assertRaises(ParseException):
            self._do_parse(act_phase_instructions)


class test_fails_when_there_are_no_statements(TestCaseForConfigurationForValidation):
    def runTest(self):
        act_phase_instructions = [instr([''])]
        with self.assertRaises(ParseException):
            self._do_parse(act_phase_instructions)


class test_fails_when_there_is_more_than_one_statement(TestCaseForConfigurationForValidation):
    def runTest(self):
        existing_file = abs_path_to_interpreter_quoted_for_exactly()
        act_phase_instructions = [instr([existing_file,
                                         existing_file])]
        with self.assertRaises(ParseException):
            self._do_parse(act_phase_instructions)
