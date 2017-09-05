import unittest

from exactly_lib.instructions.multi_phase_instructions import assign_symbol as sut
from exactly_lib_test.instructions.multi_phase_instructions.define_named_elem import \
    line_matcher, file_matcher, lines_transformer
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name')),
        line_matcher.suite(),
        file_matcher.suite(),
        lines_transformer.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
