import unittest

from exactly_lib.impls.instructions.multi_phase import new_file as sut
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_instruction_documentation
from exactly_lib_test.impls.instructions.multi_phase.new_file import contents_from_file, no_contents, \
    contents_from_program, contents_from_string, contents_from_symbol


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([

        no_contents.suite(),
        contents_from_string.suite(),
        contents_from_file.suite(),
        contents_from_program.suite(),
        contents_from_symbol.suite(),

        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name')),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
