import os
import unittest
from pathlib import Path
from typing import Dict, Optional

from exactly_lib.cli.test_case_def import TestCaseDefinitionForMainProgram
from exactly_lib.definitions.test_case import phase_names
from exactly_lib.processing.instruction_setup import InstructionsSetup
from exactly_lib.section_document import model
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib.test_case.phases.setup.instruction import SetupPhaseInstruction
from exactly_lib.test_case.phases.setup.settings_builder import SetupSettingsBuilder
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
            expected_default = None
            expected_from_defaults_getter = dict(os.environ)

            # ACT & ASSERT #

            fail_if_test_case_does_not_pass(
                self,
                Path(root_file_base_name),
                test_case_definition_with_setup_phase_assertion_instruction(self,
                                                                            expected_default,
                                                                            expected_from_defaults_getter))


class SetupPhaseInstructionThatAssertsEnvVars(SetupPhaseInstruction):
    def __init__(self,
                 put: unittest.TestCase,
                 expected_default: Optional[Dict[str, str]],
                 expected_from_defaults_getter: Dict[str, str],
                 ):
        self.put = put
        self.expected_default = expected_default
        self.expected_from_defaults_getter = expected_from_defaults_getter

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             settings: InstructionSettings,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        self.put.assertEqual(self.expected_default, environment.proc_exe_settings.environ,
                             'environ of proc-exe-settings')
        self.put.assertEqual(self.expected_default, settings.environ(),
                             'environ of instruction-settings')

        default_environ = settings.default_environ_getter()

        for k, v in self.expected_from_defaults_getter.items():
            if k not in default_environ:
                self.put.fail('Missing env var: ' + k)
            self.put.assertEqual(v,
                                 default_environ[k],
                                 'Env var value for var ' + k)

        return sh.new_sh_success()


class SetupPhaseInstructionParserThatAssertsEnvVars(InstructionParser):
    def __init__(self,
                 put: unittest.TestCase,
                 expected_default: Optional[Dict[str, str]],
                 expected_from_defaults_getter: Dict[str, str],
                 ):
        self.put = put
        self.expected_default = expected_default
        self.expected_from_defaults_getter = expected_from_defaults_getter

    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource) -> model.Instruction:
        source.consume_current_line()
        return SetupPhaseInstructionThatAssertsEnvVars(self.put,
                                                       self.expected_default,
                                                       self.expected_from_defaults_getter)


def test_case_definition_with_setup_phase_assertion_instruction(
        put: unittest.TestCase,
        expected_default: Optional[Dict[str, str]],
        expected_from_defaults_getter: Dict[str, str],
) -> TestCaseDefinitionForMainProgram:
    return test_case_definition_for(
        InstructionsSetup(
            setup_instruction_set={
                INSTR_THAT_ASSERTS_ENV_VARS: single_instruction_setup_for_parser(
                    INSTR_THAT_ASSERTS_ENV_VARS,
                    SetupPhaseInstructionParserThatAssertsEnvVars(
                        put,
                        expected_default,
                        expected_from_defaults_getter))
            })
    )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
