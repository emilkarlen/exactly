import unittest

from exactly_lib.help.concepts import concept_structure as sut
from exactly_lib.help.utils.description import Description
from exactly_lib.util.textformat.structure.structures import text


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestVisitor),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())


class TestVisitor(unittest.TestCase):
    def test_visit_plain_concept(self):
        # ARRANGE #
        recording_visitor = VisitorThatRegisterClassOfVisitMethod()
        concept = _PlainConceptDocumentationTestImpl()
        # ACT #
        recording_visitor.visit(concept)
        # ASSERT #
        self.assertEqual([sut.PlainConceptDocumentation],
                         recording_visitor.visited_classes,
                         'The method for visiting a %s should have been invoked'
                         % str(sut.PlainConceptDocumentation))

    def test_visit_configuration_parameter(self):
        # ARRANGE #
        recording_visitor = VisitorThatRegisterClassOfVisitMethod()
        concept = _ConfigurationParameterDocumentationTestImpl()
        # ACT #
        recording_visitor.visit(concept)
        # ASSERT #
        self.assertEqual([sut.ConfigurationParameterDocumentation],
                         recording_visitor.visited_classes,
                         'The method for visiting a %s should have been invoked'
                         % str(sut.ConfigurationParameterDocumentation))

    def test_visit_invalid_object_should_raise_exception(self):
        # ARRANGE #
        recording_visitor = VisitorThatRegisterClassOfVisitMethod()
        non_concept = 'a string is not a sub class of ' + str(sut.ConceptDocumentation)
        # ACT & ASSERT #
        with self.assertRaises(ValueError):
            recording_visitor.visit(non_concept)


class VisitorThatRegisterClassOfVisitMethod(sut.ConceptDocumentationVisitor):
    def __init__(self):
        self.visited_classes = []

    def visit_plain_concept(self, x: sut.PlainConceptDocumentation):
        self.visited_classes.append(sut.PlainConceptDocumentation)

    def visit_configuration_parameter(self, x: sut.ConfigurationParameterDocumentation):
        self.visited_classes.append(sut.ConfigurationParameterDocumentation)


class _PlainConceptDocumentationTestImpl(sut.PlainConceptDocumentation):
    def __init__(self):
        super().__init__(sut.Name(str(type(self))))

    def purpose(self) -> Description:
        return Description(text('PlainConceptDocumentation'), [])


class _ConfigurationParameterDocumentationTestImpl(sut.ConfigurationParameterDocumentation):
    def __init__(self):
        super().__init__(sut.Name(str(type(self))))

    def default_value_str(self) -> str:
        return 'default value str'

    def purpose(self) -> Description:
        return Description(text('ConfigurationParameterDocumentation'), [])
