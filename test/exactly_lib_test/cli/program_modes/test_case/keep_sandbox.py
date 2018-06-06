import unittest

from exactly_lib.cli.cli_environment.program_modes.test_case.command_line_options import \
    OPTION_FOR_KEEPING_SANDBOX_DIRECTORY
from exactly_lib.cli.main_program import TestCaseDefinitionForMainProgram
from exactly_lib.common.exit_value import ExitValue
from exactly_lib.processing import exit_values
from exactly_lib.processing.instruction_setup import TestCaseParsingSetup, InstructionsSetup
from exactly_lib.processing.parse.act_phase_source_parser import ActPhaseParser
from exactly_lib.section_document.syntax import section_header
from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.phase_identifier import Phase, PhaseEnum
from exactly_lib.test_case.phases.common import TestCaseInstruction
from exactly_lib.test_case.phases.result import sh
from exactly_lib.util.string import lines_content
from exactly_lib_test.cli.program_modes.test_case.config_from_suite.test_resources import run_test_case, \
    test_suite_definition_without_instructions
from exactly_lib_test.common.test_resources.instruction_setup import single_instruction_setup
from exactly_lib_test.execution.test_resources.instruction_test_resources import setup_phase_instruction_that
from exactly_lib_test.test_resources.actions import do_return
from exactly_lib_test.test_resources.file_structure import DirContents, File
from exactly_lib_test.test_suite.execution.test_resources import instruction_name_extractor
from exactly_lib_test.test_suite.test_resources.execution_utils import \
    test_case_handling_setup_with_identity_preprocessor


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Arrangement:
    def __init__(self,
                 phase: Phase,
                 instruction: TestCaseInstruction
                 ):
        self.phase = phase
        self.instruction = instruction

    def instruction_setup_with_the_instruction(self, instruction_name: str) -> InstructionsSetup:
        instruction_setup = single_instruction_setup(instruction_name, self.instruction)
        config = dict([])
        setup = dict([])
        before_assert = dict([])
        assert_ = dict([])
        cleanup = dict([])

        phase_enum = self.phase.the_enum
        if phase_enum is PhaseEnum.SETUP:
            setup[instruction_name] = instruction_setup
        elif phase_enum is PhaseEnum.BEFORE_ASSERT:
            before_assert[instruction_name] = instruction_setup
        elif phase_enum is PhaseEnum.ASSERT:
            assert_[instruction_name] = instruction_setup
        elif phase_enum is PhaseEnum.CLEANUP:
            cleanup[instruction_name] = instruction_setup
        else:
            raise ValueError('Unhandled phase: ' + str(phase_enum))

        return InstructionsSetup(config_instruction_set=config,
                                 setup_instruction_set=setup,
                                 before_assert_instruction_set=before_assert,
                                 assert_instruction_set=assert_,
                                 cleanup_instruction_set=cleanup
                                 )


class Expectation:
    def __init__(self,
                 exit_vale: ExitValue
                 ):
        self.exit_vale = exit_vale


class Case:
    def __init__(self,
                 arrangement: Arrangement,
                 expectation: Expectation
                 ):
        self.arrangement = arrangement
        self.expectation = expectation


def check(put: unittest.TestCase,
          case: Case):
    # ARRANGE #

    instruction_name = 'the_instruction'

    test_case_definition = TestCaseDefinitionForMainProgram(
        TestCaseParsingSetup(instruction_name_extractor,
                             case.arrangement.instruction_setup_with_the_instruction(instruction_name),
                             ActPhaseParser()),
        [])

    test_case_source = lines_content([
        section_header(case.arrangement.phase.identifier),
        instruction_name,
    ])

    case_file = File('the-test.case', test_case_source)
    source_files_dir_contents = DirContents([case_file])

    tc_handling_setup = test_case_handling_setup_with_identity_preprocessor()
    test_suite_definition = test_suite_definition_without_instructions()

    command_line_arguments = [
        OPTION_FOR_KEEPING_SANDBOX_DIRECTORY,
        case_file.name,
    ]

    # ACT #

    actual_result = run_test_case(command_line_arguments,
                                  source_files_dir_contents,
                                  test_case_definition,
                                  test_suite_definition,
                                  tc_handling_setup)

    # ASSERT #

    put.assertEqual(case.expectation.exit_vale.exit_code,
                    actual_result.exitcode,
                    'exit code')


class Test(unittest.TestCase):
    def test(self):
        check(self,
              Case(
                  Arrangement(phase_identifier.SETUP,
                              setup_phase_instruction_that(main=do_return(sh.new_sh_success()))
                              ),
                  Expectation(exit_values.EXECUTION__PASS)
              ))


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
