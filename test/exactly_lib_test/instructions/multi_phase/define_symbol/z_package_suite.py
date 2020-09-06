import unittest

from exactly_lib.instructions.multi_phase.define_symbol import doc
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_instruction_documentation
from exactly_lib_test.instructions.multi_phase.define_symbol import \
    source_location, common_failing_cases, string_type, path_type, list_type, line_matcher, file_matcher, \
    string_transformer, string_matcher, files_condition, files_matcher, program_type


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        suite_for_instruction_documentation(doc.TheInstructionDocumentation('instruction name', False)),
        suite_for_instruction_documentation(doc.TheInstructionDocumentation('instruction name', True)),
        common_failing_cases.suite(),
        string_type.suite(),
        path_type.suite(),
        list_type.suite(),
        line_matcher.suite(),
        file_matcher.suite(),
        files_condition.suite(),
        files_matcher.suite(),
        string_transformer.suite(),
        string_matcher.suite(),
        program_type.suite(),
        source_location.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
