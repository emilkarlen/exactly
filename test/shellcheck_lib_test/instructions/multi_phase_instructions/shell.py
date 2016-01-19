import unittest

from shellcheck_lib.instructions.multi_phase_instructions import shell as sut
from shellcheck_lib_test.instructions.test_resources.check_description import suite_for_description


def suite() -> unittest.TestSuite:
    return suite_for_description(sut.DescriptionForNonAssertPhaseInstruction('instruction name'))


if __name__ == '__main__':
    unittest.main()
