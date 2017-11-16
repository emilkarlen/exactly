import unittest

from exactly_lib.help.entities.concepts.contents_structure import ConceptDocumentation
from exactly_lib.help_texts.entity.all_entity_types import CONCEPT_ENTITY_TYPE_NAMES
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.name import Name
from exactly_lib_test.help_texts.test_resources import cross_reference_id_va as xref_va
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


def suite_for_concept_documentation(
        documentation: ConceptDocumentation) -> unittest.TestSuite:
    return unittest.TestSuite(tcc(documentation) for tcc in [
        TestName,
        TestCrossReferenceTarget,
        TestPurpose,
        TestSummaryParagraphs,
    ])


class WithConceptDocumentationBase(unittest.TestCase):
    def __init__(self, documentation: ConceptDocumentation):
        super().__init__()
        self.documentation = documentation

    def shortDescription(self):
        return str(type(self)) + '/' + str(type(self.documentation))


class TestName(WithConceptDocumentationBase):
    def runTest(self):
        # ACT #
        name = self.documentation.name()
        # ASSERT #
        self.assertIsInstance(name, Name)
        self.assertIsInstance(name.singular, str)


class TestPurpose(WithConceptDocumentationBase):
    def runTest(self):
        # ACT #
        purpose = self.documentation.purpose()
        # ASSERT #
        self.assertIsInstance(purpose, DescriptionWithSubSections)
        struct_check.is_text.apply(self, purpose.single_line_description)
        struct_check.is_section_contents.apply(self, purpose.rest)


class TestSummaryParagraphs(WithConceptDocumentationBase):
    def runTest(self):
        # ACT #
        paragraphs = self.documentation.summary_paragraphs()
        # ASSERT #
        struct_check.is_paragraph_item_list().apply(self, paragraphs)


class TestCrossReferenceTarget(WithConceptDocumentationBase):
    def runTest(self):
        actual = self.documentation.cross_reference_target()
        assertion = xref_va.is_entity_for_type(CONCEPT_ENTITY_TYPE_NAMES.identifier)
        assertion.apply_with_message(self, actual, 'cross_reference_target')
