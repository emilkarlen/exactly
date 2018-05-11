import unittest

from exactly_lib.instructions.multi_phase_instructions import define_symbol as sut
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_instruction_documentation
from exactly_lib_test.instructions.multi_phase_instructions.define_symbol import \
    common_failing_cases, string_type, path_type, list_type, line_matcher, file_matcher, string_transformer, \
    program_type


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name')),
        common_failing_cases.suite(),
        string_type.suite(),
        path_type.suite(),
        list_type.suite(),
        line_matcher.suite(),
        file_matcher.suite(),
        string_transformer.suite(),
        program_type.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
