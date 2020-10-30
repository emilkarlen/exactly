import os
import unittest
from pathlib import Path
from typing import Dict

from exactly_lib.appl_env.os_services import OsServices
from exactly_lib.cli.test_case_def import TestCaseDefinitionForMainProgram
from exactly_lib.definitions.test_case import phase_names
from exactly_lib.processing.instruction_setup import InstructionsSetup
from exactly_lib.section_document import model
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction, SetupSettingsBuilder
from exactly_lib.test_case.result import sh
from exactly_lib_test.cli.program_modes.test_resources.main_program_execution import fail_if_test_case_does_not_pass
from exactly_lib_test.cli.program_modes.test_resources.test_case_setup import test_case_definition_for
from exactly_lib_test.common.test_resources.instruction_setup import single_instruction_setup_for_parser
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
            phase_names.SETUP.syntax,
            INSTR_THAT_ASSERTS_ENV_VARS,
        ])

        cwd_dir_contents = DirContents([
            root_file_in_cwd
        ])

        with tmp_dir_as_cwd(cwd_dir_contents):
            expected_env_vars_to_exist_at_least = os.environ

            # ACT & ASSERT #

            fail_if_test_case_does_not_pass(
                self,
                Path(root_file_base_name),
                test_case_definition_with_setup_phase_assertion_instruction(self,
                                                                            expected_env_vars_to_exist_at_least))


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
            if k not in environment.proc_exe_settings.environ:
                self.put.fail('Missing env var: ' + k)
            self.put.assertEqual(v,
                                 environment.proc_exe_settings.environ[k],
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


def test_case_definition_with_setup_phase_assertion_instruction(
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


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
