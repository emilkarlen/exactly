import unittest
from pathlib import Path

from exactly_lib.cli.main_program import TestCaseDefinitionForMainProgram
from exactly_lib.definitions.test_case.phase_names import CONFIGURATION_PHASE_NAME
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.processing.instruction_setup import InstructionsSetup
from exactly_lib.processing.preprocessor import IDENTITY_PREPROCESSOR
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.section_document import model
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.test_case import os_services
from exactly_lib.test_case.phases.configuration import ConfigurationPhaseInstruction, ConfigurationBuilder
from exactly_lib.test_case.result import sh
from exactly_lib.test_case_file_structure.path_relativity import RelHomeOptionType
from exactly_lib_test.cli.program_modes.test_case.config_from_suite.test_resources import \
    test_suite_definition_without_instructions
from exactly_lib_test.cli.program_modes.test_resources import source_file_paths as tr
from exactly_lib_test.cli.program_modes.test_resources.test_case_setup import test_case_definition_for
from exactly_lib_test.common.test_resources.instruction_setup import single_instruction_setup_for_parser
from exactly_lib_test.test_case.act_phase_handling.test_resources.act_source_and_executor_constructors import \
    ActSourceAndExecutorConstructorThatRunsConstantActions
from exactly_lib_test.test_resources.files.file_structure import DirContents
from exactly_lib_test.test_resources.files.file_structure import file_with_lines, \
    Dir
from exactly_lib_test.test_resources.files.tmp_dir import tmp_dir_as_cwd
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestInitialHdsDirPaths)


INSTR_THAT_ASSERTS_HDS_DIR_MATCHES_PATH = 'assert-hds-dir-matches-path'


class TestInitialHdsDirPaths(unittest.TestCase):
    def test_relative_path_to_root_file_in_cwd(self):
        # ARRANGE #

        root_file_base_name = 'root-file-base-name.src'

        root_file_in_cwd = file_with_lines(root_file_base_name, [
            CONFIGURATION_PHASE_NAME.syntax,
            INSTR_THAT_ASSERTS_HDS_DIR_MATCHES_PATH,
        ])

        cwd_dir_contents = DirContents([
            root_file_in_cwd
        ])

        file_arg_to_parser_rel_cwd = Path(root_file_base_name)

        with tmp_dir_as_cwd(cwd_dir_contents) as abs_cwd_dir_path:
            hds_dir_assertion = asrt.equals(abs_cwd_dir_path)

            # ACT & ASSERT #

            fail_if_test_case_does_not_pass(self,
                                            file_arg_to_parser_rel_cwd,
                                            hds_dir_assertion)

    def test_abs_path_to_root_file_in_cwd(self):
        # ARRANGE #

        root_file_base_name = 'root-file-base-name.src'

        root_file_in_cwd = file_with_lines(root_file_base_name, [
            CONFIGURATION_PHASE_NAME.syntax,
            INSTR_THAT_ASSERTS_HDS_DIR_MATCHES_PATH,
        ])

        cwd_dir_contents = DirContents([
            root_file_in_cwd
        ])

        with tmp_dir_as_cwd(cwd_dir_contents) as abs_cwd_dir_path:
            abs_file_arg_to_parser = abs_cwd_dir_path / root_file_base_name

            hds_dir_assertion = asrt.equals(abs_cwd_dir_path)

            # ACT & ASSERT #

            fail_if_test_case_does_not_pass(self,
                                            abs_file_arg_to_parser,
                                            hds_dir_assertion)

    def test_relative_path_to_root_file_in_sub_dir_of_cwd(self):
        # ARRANGE #

        root_file_sub_dir_path = Path('sub-dir')
        root_file_base_name = 'root-file-base-name.src'

        root_file_in_sub_dir = file_with_lines(root_file_base_name, [
            CONFIGURATION_PHASE_NAME.syntax,
            INSTR_THAT_ASSERTS_HDS_DIR_MATCHES_PATH,
        ])

        cwd_dir_contents = DirContents([
            Dir(str(root_file_sub_dir_path), [
                root_file_in_sub_dir,
            ])
        ])

        file_arg_to_parser_rel_cwd = root_file_sub_dir_path / root_file_base_name

        with tmp_dir_as_cwd(cwd_dir_contents) as abs_cwd_dir_path:
            hds_dir_assertion = asrt.equals(abs_cwd_dir_path / root_file_sub_dir_path)

            # ACT & ASSERT #

            fail_if_test_case_does_not_pass(self,
                                            file_arg_to_parser_rel_cwd,
                                            hds_dir_assertion)


class ConfigPhaseInstructionThatAssertsHdsDirs(ConfigurationPhaseInstruction):
    def __init__(self,
                 put: unittest.TestCase,
                 assertion: asrt.ValueAssertion[Path]):
        self.put = put
        self.assertion = assertion

    def main(self, configuration_builder: ConfigurationBuilder) -> sh.SuccessOrHardError:
        for hds_dir in RelHomeOptionType:
            self.assertion.apply_with_message(self.put,
                                              configuration_builder.get_hds_dir(hds_dir),
                                              str(hds_dir))
        return sh.new_sh_success()


class ConfigPhaseInstructionParserThatAssertsSourceFileLocationInfo(InstructionParser):
    def __init__(self,
                 put: unittest.TestCase,
                 assertion: asrt.ValueAssertion[Path]):
        self.put = put
        self.assertion = assertion

    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource) -> model.Instruction:
        source.consume_current_line()
        return ConfigPhaseInstructionThatAssertsHdsDirs(self.put, self.assertion)


def fail_if_test_case_does_not_pass(put: unittest.TestCase,
                                    root_file_path_argument: Path,
                                    hds_dir_assertion: asrt.ValueAssertion[Path],
                                    ):
    # SETUP #

    tc_definition = test_case_definition_with_config_phase_assertion_instruction(put,
                                                                                 hds_dir_assertion)

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
        hds_dir_assertion: asrt.ValueAssertion[Path],
) -> TestCaseDefinitionForMainProgram:
    return test_case_definition_for(
        InstructionsSetup(
            config_instruction_set={
                INSTR_THAT_ASSERTS_HDS_DIR_MATCHES_PATH: single_instruction_setup_for_parser(
                    INSTR_THAT_ASSERTS_HDS_DIR_MATCHES_PATH,
                    ConfigPhaseInstructionParserThatAssertsSourceFileLocationInfo(
                        put,
                        hds_dir_assertion))
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
