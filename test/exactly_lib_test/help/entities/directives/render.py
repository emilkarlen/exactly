import unittest

from exactly_lib.help.entities.directives import all_directives
from exactly_lib.help.entities.directives import render as sut
from exactly_lib.help.entities.directives.entity_configuration import DIRECTIVE_ENTITY_CONFIGURATION
from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib_test.util.textformat.constructor.test_resources import CrossReferenceTextConstructorTestImpl
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestIndividualDirective),
        unittest.makeSuite(TestAllDirectivesList),
    ])


CONSTRUCTION_ENVIRONMENT = ConstructionEnvironment(CrossReferenceTextConstructorTestImpl())


class TestAllDirectivesList(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        renderer = DIRECTIVE_ENTITY_CONFIGURATION.cli_list_constructor_getter.get_constructor(
            all_directives.all_directives())
        # ACT #
        actual = renderer.apply(CONSTRUCTION_ENVIRONMENT)
        # ASSERT #
        struct_check.is_section_contents.apply(self, actual)


class TestIndividualDirective(unittest.TestCase):
    def runTest(self):
        for directive in all_directives.all_directives():
            with self.subTest(directive.singular_name()):
                # ARRANGE #
                renderer = sut.IndividualDirectiveConstructor(directive)
                # ACT #
                actual = renderer.apply(CONSTRUCTION_ENVIRONMENT)
                # ASSERT #
                struct_check.is_article_contents.apply(self, actual)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
