import unittest

from exactly_lib.help.entities.types.contents_structure import TypeDocumentation
from exactly_lib.help_texts.entity.all_entity_types import TYPE_ENTITY_TYPE_NAMES
from exactly_lib.type_system.value_type import TypeCategory
from exactly_lib_test.common.help.test_resources import syntax_contents_structure_assertions as asrt_syntax_struct
from exactly_lib_test.help_texts.test_resources import cross_reference_id_va as asrt_cross_ref
from exactly_lib_test.help_texts.test_resources.entity_cross_ref_va import equals_entity_cross_ref
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources.name import is_name
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


def suite_for_single_documentation(
        documentation: TypeDocumentation) -> unittest.TestSuite:
    return unittest.TestSuite(tcc(documentation) for tcc in [
        TestIsDocumentationInstance,
        TestTypeCategory,
        TestCrossReferenceTarget,
        TestSingularName,
        TestInvokationVariants,
        TestSeeAlsoTargets,
        TestMainDescriptionRest,
    ])


class WithDocumentationBase(unittest.TestCase):
    def __init__(self, documentation: TypeDocumentation):
        super().__init__()
        self.documentation = documentation

    def shortDescription(self):
        return str(type(self)) + '/' + self.documentation.singular_name()


class TestIsDocumentationInstance(WithDocumentationBase):
    def runTest(self):
        # ACT #
        actual = self.documentation
        # ASSERT #
        self.assertIsInstance(actual, TypeDocumentation)


class TestTypeCategory(WithDocumentationBase):
    def runTest(self):
        # ACT #
        actual = self.documentation.type_category
        # ASSERT #
        self.assertIsInstance(actual, TypeCategory)


class TestTestTypeIdentifier(WithDocumentationBase):
    def runTest(self):
        # ACT #
        actual = self.documentation.type_identifier()
        # ASSERT #
        self.assertIsInstance(actual, str)


class TestCrossReferenceTarget(WithDocumentationBase):
    def runTest(self):
        assertion = equals_entity_cross_ref(TYPE_ENTITY_TYPE_NAMES,
                                            self.documentation.singular_name())

        actual = self.documentation.cross_reference_target()

        assertion.apply_with_message(self, actual, 'cross_reference_target')


class TestSingularName(WithDocumentationBase):
    def runTest(self):
        # ACT #
        name = self.documentation.singular_name()
        # ASSERT #
        self.assertIsInstance(name, str)


class TestName(WithDocumentationBase):
    def runTest(self):
        # ACT #
        actual = self.documentation.singular_name()
        # ASSERT #
        is_name().apply_without_message(self, actual)


class TestInvokationVariants(WithDocumentationBase):
    def runTest(self):
        # ACT #
        actual = self.documentation.invokation_variants()
        # ASSERT #
        assertion = asrt.is_list_of(asrt_syntax_struct.is_invokation_variant)
        assertion.apply_without_message(self, actual)


class TestSeeAlsoTargets(WithDocumentationBase):
    def runTest(self):
        # ACT #
        actual = self.documentation.see_also_targets()
        # ASSERT #
        assertion = asrt.is_list_of(asrt_cross_ref.is_any)
        assertion.apply_without_message(self, actual)


class TestMainDescriptionRest(WithDocumentationBase):
    def runTest(self):
        # ACT #
        actual = self.documentation.main_description_rest()
        # ASSERT #
        struct_check.is_section_contents.apply_without_message(self, actual)
