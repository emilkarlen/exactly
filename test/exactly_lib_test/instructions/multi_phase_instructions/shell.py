import unittest

from exactly_lib.instructions.multi_phase_instructions import shell as sut
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation


def suite() -> unittest.TestSuite:
    return suite_for_instruction_documentation(sut.DescriptionForNonAssertPhaseInstruction('instruction name'))


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
