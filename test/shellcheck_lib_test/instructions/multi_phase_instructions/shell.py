import unittest

from shellcheck_lib.instructions.multi_phase_instructions import shell as sut
from shellcheck_lib.test_case.instruction_description import Description
from shellcheck_lib_test.instructions.test_resources.check_description import TestDescriptionBase, \
    suite_for_description


class TestDescription(TestDescriptionBase):
    def _description(self) -> Description:
        return sut.TheDescription('instruction name')


def suite() -> unittest.TestSuite:
    return suite_for_description(sut.DescriptionForNonAssertPhaseInstruction('instruction name'))


if __name__ == '__main__':
    unittest.main()
