import unittest

from exactly_lib.util.textformat.structure import document as sut
from exactly_lib.util.textformat.structure.core import StringText
from exactly_lib.util.textformat.structure.document import ArticleContents


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestAccept)


class SectionItemVisitorThatRecordsExpectedClassAndReturnsArg(sut.SectionItemVisitor[sut.SectionItem]):
    def __init__(self):
        self.visited_classes = []

    def visit_section(self, section: sut.Section) -> sut.SectionItem:
        self.visited_classes.append(sut.Section)
        return section

    def visit_article(self, article: sut.Article) -> sut.SectionItem:
        self.visited_classes.append(sut.Article)
        return article


class TestAccept(unittest.TestCase):
    def test_section(self):
        # ARRANGE   #
        section = sut.Section(StringText('header'),
                              sut.empty_section_contents())
        visitor = SectionItemVisitorThatRecordsExpectedClassAndReturnsArg()
        # ACT #
        ret_val = section.accept(visitor)
        # ASSERT #
        self.assertEqual([sut.Section],
                         visitor.visited_classes)
        self.assertIs(section, ret_val)

    def test_article(self):
        # ARRANGE   #
        article = sut.Article(StringText('header'),
                              ArticleContents([],
                                              sut.empty_section_contents()))
        visitor = SectionItemVisitorThatRecordsExpectedClassAndReturnsArg()
        # ACT #
        ret_val = article.accept(visitor)
        # ASSERT #
        self.assertEqual([sut.Article],
                         visitor.visited_classes)
        self.assertIs(article, ret_val)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
