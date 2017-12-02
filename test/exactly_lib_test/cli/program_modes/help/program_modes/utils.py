import unittest

from exactly_lib.cli.program_modes.help.program_modes import utils as sut
from exactly_lib.util.textformat.structure import document as doc, structures as docs
from exactly_lib_test.util.textformat.construction.test_resources import CONSTRUCTION_ENVIRONMENT
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestWithOrWithoutName)


class TestWithOrWithoutName(unittest.TestCase):
    def test_without_name(self):
        constructor = sut.with_or_without_name(False, 'name', ArticleContentsConstructorTestImpl())
        construction = constructor.apply(CONSTRUCTION_ENVIRONMENT)
        struct_check.is_section_contents.apply(self, construction)

    def test_with_name(self):
        constructor = sut.with_or_without_name(True, 'name', ArticleContentsConstructorTestImpl())
        construction = constructor.apply(CONSTRUCTION_ENVIRONMENT)
        struct_check.is_section_contents.apply(self, construction)


class ArticleContentsConstructorTestImpl(sut.ArticleContentsConstructor):
    def apply(self, environment: sut.ConstructionEnvironment) -> doc.ArticleContents:
        return doc.ArticleContents(docs.paras('abstract paragraph'),
                                   doc.SectionContents(docs.paras('initial paragraph'),
                                                       []))
