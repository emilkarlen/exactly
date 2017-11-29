import unittest

from exactly_lib.util.textformat.structure import document as sut
from exactly_lib.util.textformat.structure.core import StringText


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(SectionItemVisitorTest)


class SectionItemVisitorThatRecordsExpectedClassAndReturnsArg(sut.SectionItemVisitor):
    def __init__(self):
        self.visited_classes = []

    def visit_section(self, section: sut.Section):
        self.visited_classes.append(sut.Section)
        return section

    def visit_article(self, article: sut.Article):
        self.visited_classes.append(sut.Article)
        return article


class SectionItemVisitorTest(unittest.TestCase):
    def test_section(self):
        # ARRANGE   #
        section = sut.Section(StringText('header'),
                              sut.empty_section_contents())
        visitor = SectionItemVisitorThatRecordsExpectedClassAndReturnsArg()
        # ACT #
        ret_val = visitor.visit(section)
        # ASSERT #
        self.assertEqual([sut.Section],
                         visitor.visited_classes)
        self.assertIs(section, ret_val)

    def test_article(self):
        # ARRANGE   #
        article = sut.Article(StringText('header'),
                              [],
                              sut.empty_section_contents())
        visitor = SectionItemVisitorThatRecordsExpectedClassAndReturnsArg()
        # ACT #
        ret_val = visitor.visit(article)
        # ASSERT #
        self.assertEqual([sut.Article],
                         visitor.visited_classes)
        self.assertIs(article, ret_val)

    def test_visit_SHOULD_raise_type_error_WHEN_argument_is_not_a_valid_section_item(self):
        visitor = SectionItemVisitorThatRecordsExpectedClassAndReturnsArg()
        unknown_section_item = UnknownSectionItem()
        with self.assertRaises(TypeError):
            visitor.visit(unknown_section_item)


class UnknownSectionItem(sut.SectionItem):
    def __init__(self):
        super().__init__(StringText('header of unknown item'),
                         sut.empty_section_contents())


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
