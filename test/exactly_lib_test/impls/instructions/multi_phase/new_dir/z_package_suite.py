import unittest

from exactly_lib.impls.instructions.multi_phase import new_dir as sut
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_instruction_documentation
from exactly_lib_test.impls.instructions.multi_phase.new_dir import create_implicitly_empty, explicit_contents


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        create_implicitly_empty.suite(),
        explicit_contents.suite(),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name')),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
