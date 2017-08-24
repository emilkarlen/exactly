import unittest

from exactly_lib.instructions.multi_phase_instructions import assign_symbol as sut
from exactly_lib_test.instructions.multi_phase_instructions.define_named_elem import file_selector
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name')),
        file_selector.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
