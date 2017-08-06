import pathlib
import unittest

from exactly_lib.common.help.instruction_documentation import InstructionDocumentation
from exactly_lib.instructions.configuration import act_home as sut
from exactly_lib.section_document.parser_implementations.section_element_parsers import InstructionParser
from exactly_lib.test_case.phases.configuration import ConfigurationBuilder
from exactly_lib.test_case_file_structure.path_relativity import RelHomeOptionType
from exactly_lib_test.instructions.configuration.test_resources import set_home_dir


def suite() -> unittest.TestSuite:
    return set_home_dir.suite_for(TheConfiguration())


class TheConfiguration(set_home_dir.Configuration):
    def __init__(self):
        super().__init__(RelHomeOptionType.REL_HOME_ACT)

    def get_property_dir_path(self,
                              configuration_builder: ConfigurationBuilder) -> pathlib.Path:
        return configuration_builder.home_act_dir_path

    def parser(self) -> InstructionParser:
        return sut.Parser()

    def instruction_documentation(self) -> InstructionDocumentation:
        return sut.TheInstructionDocumentation('instruction mame')


# class Test(setting_of_home_dirs.TestSuccessfulExecution_change_to_parent_dir):
#     def __init__(self, methodName):
#         super().__init__(TheConfiguration())
#
#
if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
