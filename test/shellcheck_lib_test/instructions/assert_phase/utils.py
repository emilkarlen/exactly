import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser
from shellcheck_lib.test_case.instruction import common as i
from shellcheck_lib.test_case.instruction.result import pfh
from shellcheck_lib.test_case.instruction.result import svh
from shellcheck_lib.test_case.instruction.sections.assert_ import AssertPhaseInstruction
from shellcheck_lib_test.instructions import utils
from shellcheck_lib_test.instructions.utils import SingleInstructionParserSource
from shellcheck_lib_test.util.file_structure import DirContents


class AssertInstructionTest:
    def __init__(self,
                 expected_validation_result: svh.SuccessOrValidationErrorOrHardErrorEnum,
                 expected_application_result: pfh.PassOrFailOrHardErrorEnum,
                 act_result: utils.ActResult,
                 home_dir_contents: DirContents=DirContents([]),
                 act_dir_contents_after_act: DirContents=DirContents([])):
        self._expected_validation_result = expected_validation_result
        self._expected_application_result = expected_application_result
        self._act_result = act_result
        self._home_dir_contents = home_dir_contents
        self._act_dir_contents_after_act = act_dir_contents_after_act

    @property
    def expected_validation_result(self) -> svh.SuccessOrValidationErrorOrHardError:
        return self._expected_validation_result

    @property
    def expected_application_result(self) -> pfh.PassOrFailOrHardErrorEnum:
        return self._expected_application_result

    def apply(self,
              ptc: unittest.TestCase,
              parser: SingleInstructionParser,
              source: SingleInstructionParserSource):
        instruction = parser.apply(source)
        assert isinstance(instruction, AssertPhaseInstruction)
        with utils.home_and_eds_and_test_as_curr_dir() as home_and_eds:
            self._home_dir_contents.write_to(home_and_eds.home_dir_path)
            global_environment = i.GlobalEnvironmentForPostEdsPhase(home_and_eds.home_dir_path,
                                                                    home_and_eds.eds)
            validation_result = instruction.validate(global_environment)
            ptc.assertEqual(self.expected_validation_result,
                            validation_result.status,
                            'Validation result status')
            if self.expected_validation_result == svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS:
                home_and_eds.write_act_result(self._act_result)
                phase_environment = i.PhaseEnvironmentForInternalCommands()
                self._act_dir_contents_after_act.write_to(home_and_eds.eds.act_dir)
                application_result = instruction.main(global_environment, phase_environment)
                ptc.assertEqual(self.expected_application_result,
                                application_result.status,
                                'Application result status')
