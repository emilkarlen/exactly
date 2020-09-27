import unittest

from exactly_lib.common.help.instruction_documentation import InstructionDocumentation
from exactly_lib.instructions.configuration import hds_case as sut
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.tcfs.path_relativity import RelHdsOptionType
from exactly_lib_test.instructions.configuration.test_resources import set_hds_dir


def suite() -> unittest.TestSuite:
    return set_hds_dir.suite_for(TheConfiguration())


class TheConfiguration(set_hds_dir.Configuration):
    def __init__(self):
        super().__init__(RelHdsOptionType.REL_HDS_CASE)

    def parser(self) -> InstructionParser:
        return sut.parser()

    def instruction_documentation(self) -> InstructionDocumentation:
        return sut.TheInstructionDocumentation('instruction mame')


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
