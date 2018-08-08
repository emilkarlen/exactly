import os
import unittest
from pathlib import Path
from typing import Dict

from exactly_lib.cli.main_program import TestCaseDefinitionForMainProgram
from exactly_lib.definitions.test_case.phase_names import SETUP_PHASE_NAME
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.processing.instruction_setup import InstructionsSetup
from exactly_lib.processing.preprocessor import IDENTITY_PREPROCESSOR
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.section_document import model
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.test_case import os_services
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction, SetupSettingsBuilder
from exactly_lib.test_case.result import sh
from exactly_lib_test.cli.program_modes.test_case.config_from_suite.test_resources import \
    test_suite_definition_without_instructions
from exactly_lib_test.cli.program_modes.test_resources import main_program_execution as tr
from exactly_lib_test.cli.program_modes.test_resources.test_case_setup import test_case_definition_for
from exactly_lib_test.common.test_resources.instruction_setup import single_instruction_setup_for_parser
from exactly_lib_test.test_case.act_phase_handling.test_resources.act_source_and_executor_constructors import \
    ActSourceAndExecutorConstructorThatRunsConstantActions
from exactly_lib_test.test_resources.files.file_structure import DirContents
from exactly_lib_test.test_resources.files.file_structure import file_with_lines
from exactly_lib_test.test_resources.files.tmp_dir import tmp_dir_as_cwd


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestInitialEnvVarsInInstructionEnvironment)


INSTR_THAT_ASSERTS_ENV_VARS = 'assert-env-vars'


class TestInitialEnvVarsInInstructionEnvironment(unittest.TestCase):
    def test_relative_path_to_root_file_in_cwd(self):
        # ARRANGE #

        root_file_base_name = 'root-file-base-name.src'

        root_file_in_cwd = file_with_lines(root_file_base_name, [
            SETUP_PHASE_NAME.syntax,
            INSTR_THAT_ASSERTS_ENV_VARS,
        ])

        cwd_dir_contents = DirContents([
            root_file_in_cwd
        ])

        with tmp_dir_as_cwd(cwd_dir_contents):
            expected_env_vars_to_exist_at_least = os.environ

            # ACT & ASSERT #

            fail_if_test_case_does_not_pass(self,
                                            Path(root_file_base_name),
                                            expected_env_vars_to_exist_at_least)


class SetupPhaseInstructionThatAssertsEnvVars(SetupPhaseInstruction):
    def __init__(self,
                 put: unittest.TestCase,
                 expected_to_exist: Dict[str, str]):
        self.put = put
        self.expected_to_exist = expected_to_exist

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        for k, v in self.expected_to_exist.items():
            if k not in environment.environ:
                self.put.fail('Missing env var: ' + k)
            self.put.assertEqual(v,
                                 environment.environ[k],
                                 'Env var value for var ' + k)

        return sh.new_sh_success()


class SetupPhaseInstructionParserThatAssertsEnvVars(InstructionParser):
    def __init__(self,
                 put: unittest.TestCase,
                 expected_to_exist: Dict[str, str]):
        self.put = put
        self.expected_to_exist = expected_to_exist

    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource) -> model.Instruction:
        source.consume_current_line()
        return SetupPhaseInstructionThatAssertsEnvVars(self.put, self.expected_to_exist)


def fail_if_test_case_does_not_pass(put: unittest.TestCase,
                                    root_file_path_argument: Path,
                                    expected_to_exist: Dict[str, str],
                                    ):
    # SETUP #

    tc_definition = test_case_definition_with_config_phase_assertion_instruction(put,
                                                                                 expected_to_exist)

    command_line_arguments = [
        str(root_file_path_argument),
    ]

    # ACT & ASSERT #

    sub_process_result = tr.run_main_program_and_collect_process_result(
        command_line_arguments,
        main_program_config(tc_definition)
    )

    if sub_process_result.exitcode != 0:
        put.fail('Exit code is non zero. Error message: ' + sub_process_result.stderr)


def test_case_definition_with_config_phase_assertion_instruction(
        put: unittest.TestCase,
        expected_to_exist: Dict[str, str],
) -> TestCaseDefinitionForMainProgram:
    return test_case_definition_for(
        InstructionsSetup(
            setup_instruction_set={
                INSTR_THAT_ASSERTS_ENV_VARS: single_instruction_setup_for_parser(
                    INSTR_THAT_ASSERTS_ENV_VARS,
                    SetupPhaseInstructionParserThatAssertsEnvVars(
                        put,
                        expected_to_exist))
            })
    )


def main_program_config(tc_definition: TestCaseDefinitionForMainProgram) -> tr.MainProgramConfig:
    return tr.MainProgramConfig(TestCaseHandlingSetup(
        ActPhaseSetup(ActSourceAndExecutorConstructorThatRunsConstantActions()),
        IDENTITY_PREPROCESSOR),
        os_services.DEFAULT_ACT_PHASE_OS_PROCESS_EXECUTOR,
        tc_definition,
        test_suite_definition_without_instructions(),
    )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
