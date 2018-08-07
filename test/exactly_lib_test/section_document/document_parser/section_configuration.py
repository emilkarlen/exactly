import unittest

from exactly_lib.section_document.section_parsing import SectionConfiguration, SectionsConfiguration
from exactly_lib_test.section_document.document_parser.test_resources.misc import \
    SectionElementParserForEmptyCommentAndInstructionLines


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestSectionsConfiguration)


class TestSectionsConfiguration(unittest.TestCase):
    def test_WHEN_the_default_section_name_is_not_a_name_of_a_section_THEN_an_exception_SHOULD_be_raised(self):
        # ARRANGE #
        section_names = ['section 1', 'section 2']
        sections = [SectionConfiguration(name,
                                         SectionElementParserForEmptyCommentAndInstructionLines(
                                             name))
                    for name in section_names]
        default_section_name = 'not the name of a section'
        # ACT & ASSERT #
        with self.assertRaises(ValueError):
            SectionsConfiguration(
                tuple(sections),
                default_section_name=default_section_name)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
