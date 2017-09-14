import unittest

from exactly_lib.instructions.assert_ import contents_of_dir as sut
from exactly_lib_test.instructions.assert_.contents_of_dir.test_resources.tr import \
    TestParseInvalidSyntaxBase
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation
from exactly_lib_test.test_resources.name_and_value import NameAndValue


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParseInvalidSyntax),

        suite_for_instruction_documentation(sut.TheInstructionDocumentation('the-instruction-name')),
    ])


class TestParseInvalidSyntax(TestParseInvalidSyntaxBase):
    @property
    def test_cases_with_negation_operator_place_holder(self) -> list:
        return [
            NameAndValue(
                'no arguments',
                '',
            ),
            NameAndValue(
                'valid file argument, but no operator',
                'file-name <not_opt>',
            ),
            NameAndValue(
                'valid file argument, invalid check',
                'file-name <not_opt> invalid-check',
            ),
        ]


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
