import unittest

from shellcheck_lib.document import parse
from shellcheck_lib.general import line_source
from shellcheck_lib.general.line_source import LineSequenceBuilder
from shellcheck_lib.instructions.instruction_parser_for_single_phase import \
    SingleInstructionParser
from shellcheck_lib.test_case import instructions as i
from shellcheck_lib_test.instructions import utils
from shellcheck_lib_test.util.file_structure import DirContents


class SingleInstructionParserSource:
    def __init__(self,
                 line_sequence: line_source.LineSequenceBuilder,
                 instruction_argument: str):
        self.line_sequence = line_sequence
        self.instruction_argument = instruction_argument


def new_source(instruction_name: str, arguments: str) -> SingleInstructionParserSource:
    first_line = instruction_name + ' ' + arguments
    return SingleInstructionParserSource(
        new_line_sequence(first_line),
        arguments)


def new_line_sequence(first_line: str) -> LineSequenceBuilder:
    return line_source.LineSequenceBuilder(
        parse.LineSequenceSourceFromListOfLines(
            parse.ListOfLines([])),
        1,
        first_line)


class AssertInstructionTest:
    def __init__(self,
                 expected_validation_result: i.SuccessOrValidationErrorOrHardErrorEnum,
                 expected_application_result: i.PassOrFailOrHardErrorEnum,
                 act_result: utils.ActResult,
                 home_dir_contents: DirContents=DirContents([]),
                 act_dir_contents_after_act: DirContents=DirContents([])):
        self._expected_validation_result = expected_validation_result
        self._expected_application_result = expected_application_result
        self._act_result = act_result
        self._home_dir_contents = home_dir_contents
        self._act_dir_contents_after_act = act_dir_contents_after_act

    @property
    def expected_validation_result(self) -> i.SuccessOrValidationErrorOrHardError:
        return self._expected_validation_result

    @property
    def expected_application_result(self) -> i.PassOrFailOrHardErrorEnum:
        return self._expected_application_result

    def apply(self,
              ptc: unittest.TestCase,
              parser: SingleInstructionParser,
              source: SingleInstructionParserSource):
        instruction = parser.apply(source.line_sequence, source.instruction_argument)
        assert isinstance(instruction, i.AssertPhaseInstruction)
        with utils.home_and_eds_and_test_as_curr_dir() as home_and_eds:
            self._home_dir_contents.write_to(home_and_eds.home_dir_path)
            global_environment = i.GlobalEnvironmentForPostEdsPhase(home_and_eds.home_dir_path,
                                                                    home_and_eds.eds)
            validation_result = instruction.validate(global_environment)
            ptc.assertEqual(self.expected_validation_result,
                            validation_result.status,
                            'Validation result status')
            home_and_eds.write_act_result(self._act_result)
            phase_environment = i.PhaseEnvironmentForInternalCommands()
            self._act_dir_contents_after_act.write_to(home_and_eds.eds.test_root_dir)
            application_result = instruction.main(global_environment, phase_environment)
            ptc.assertEqual(self.expected_application_result,
                            application_result.status,
                            'Application result status')
