import unittest
from pathlib import Path

from exactly_lib.cli.test_case_def import TestCaseDefinitionForMainProgram
from exactly_lib.definitions.test_case import phase_names
from exactly_lib.processing.instruction_setup import InstructionsSetup
from exactly_lib.section_document import model
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.tcfs.path_relativity import RelHdsOptionType
from exactly_lib.test_case.phases.configuration import ConfigurationPhaseInstruction, ConfigurationBuilder
from exactly_lib.test_case.result import sh
from exactly_lib_test.cli.program_modes.test_resources.main_program_execution import fail_if_test_case_does_not_pass
from exactly_lib_test.cli.program_modes.test_resources.test_case_setup import test_case_definition_for
from exactly_lib_test.common.test_resources.instruction_setup import single_instruction_setup_for_parser
from exactly_lib_test.test_resources.files.file_structure import DirContents
from exactly_lib_test.test_resources.files.file_structure import file_with_lines, \
    Dir
from exactly_lib_test.test_resources.files.tmp_dir import tmp_dir_as_cwd
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestInitialHdsDirPaths)


INSTR_THAT_ASSERTS_HDS_DIR_MATCHES_PATH = 'assert-hds-dir-matches-path'


class TestInitialHdsDirPaths(unittest.TestCase):
    def test_relative_path_to_root_file_in_cwd(self):
        # ARRANGE #

        root_file_base_name = 'root-file-base-name.src'

        root_file_in_cwd = file_with_lines(root_file_base_name, [
            phase_names.CONFIGURATION.syntax,
            INSTR_THAT_ASSERTS_HDS_DIR_MATCHES_PATH,
        ])

        cwd_dir_contents = DirContents([
            root_file_in_cwd
        ])

        file_arg_to_parser_rel_cwd = Path(root_file_base_name)

        with tmp_dir_as_cwd(cwd_dir_contents) as abs_cwd_dir_path:
            hds_dir_assertion = asrt.equals(abs_cwd_dir_path)

            # ACT & ASSERT #

            fail_if_test_case_does_not_pass(
                self,
                file_arg_to_parser_rel_cwd,
                test_case_definition_with_config_phase_assertion_instruction(self,
                                                                             hds_dir_assertion))

    def test_abs_path_to_root_file_in_cwd(self):
        # ARRANGE #

        root_file_base_name = 'root-file-base-name.src'

        root_file_in_cwd = file_with_lines(root_file_base_name, [
            phase_names.CONFIGURATION.syntax,
            INSTR_THAT_ASSERTS_HDS_DIR_MATCHES_PATH,
        ])

        cwd_dir_contents = DirContents([
            root_file_in_cwd
        ])

        with tmp_dir_as_cwd(cwd_dir_contents) as abs_cwd_dir_path:
            abs_file_arg_to_parser = abs_cwd_dir_path / root_file_base_name

            hds_dir_assertion = asrt.equals(abs_cwd_dir_path)

            # ACT & ASSERT #

            fail_if_test_case_does_not_pass(
                self,
                abs_file_arg_to_parser,
                test_case_definition_with_config_phase_assertion_instruction(self,
                                                                             hds_dir_assertion))

    def test_relative_path_to_root_file_in_sub_dir_of_cwd(self):
        # ARRANGE #

        root_file_sub_dir_path = Path('sub-dir')
        root_file_base_name = 'root-file-base-name.src'

        root_file_in_sub_dir = file_with_lines(root_file_base_name, [
            phase_names.CONFIGURATION.syntax,
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

            fail_if_test_case_does_not_pass(
                self,
                file_arg_to_parser_rel_cwd,
                test_case_definition_with_config_phase_assertion_instruction(self,
                                                                             hds_dir_assertion))


class ConfigPhaseInstructionThatAssertsHdsDirs(ConfigurationPhaseInstruction):
    def __init__(self,
                 put: unittest.TestCase,
                 assertion: ValueAssertion[Path]):
        self.put = put
        self.assertion = assertion

    def main(self, configuration_builder: ConfigurationBuilder) -> sh.SuccessOrHardError:
        for hds_dir in RelHdsOptionType:
            self.assertion.apply_with_message(self.put,
                                              configuration_builder.get_hds_dir(hds_dir),
                                              str(hds_dir))
        return sh.new_sh_success()


class ConfigPhaseInstructionParserThatAssertsSourceFileLocationInfo(InstructionParser):
    def __init__(self,
                 put: unittest.TestCase,
                 assertion: ValueAssertion[Path]):
        self.put = put
        self.assertion = assertion

    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource) -> model.Instruction:
        source.consume_current_line()
        return ConfigPhaseInstructionThatAssertsHdsDirs(self.put, self.assertion)


def test_case_definition_with_config_phase_assertion_instruction(
        put: unittest.TestCase,
        hds_dir_assertion: ValueAssertion[Path],
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


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
