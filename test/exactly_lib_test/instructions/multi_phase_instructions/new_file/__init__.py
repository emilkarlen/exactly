import unittest

from exactly_lib.instructions.multi_phase_instructions import new_file as sut
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_instruction_documentation
from exactly_lib_test.instructions.multi_phase_instructions.new_file import contents_from_file, no_contents, \
    contents_from_program, contents_from_string


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([

        no_contents.suite(),
        contents_from_string.suite(),
        contents_from_file.suite(),
        contents_from_program.suite(),

        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name', False)),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name', True)),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
