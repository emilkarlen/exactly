import unittest

from exactly_lib_test.processing.parse import act_phase_source_parser, file_inclusion_directive_parser


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        act_phase_source_parser.suite(),
        file_inclusion_directive_parser.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
