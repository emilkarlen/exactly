import unittest

from exactly_lib.definitions.entity.all_entity_types import ACTOR_ENTITY_TYPE_NAMES
from exactly_lib.help.entities.actors.contents_structure import ActorDocumentation
from exactly_lib_test.common.help.test_resources import see_also_assertions as asrt_see_also
from exactly_lib_test.definitions.test_resources import cross_reference_id_va as xref_va
from exactly_lib_test.test_resources.test_case_base_with_short_description import \
    TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


def suite_for_actor_documentation(documentation: ActorDocumentation) -> unittest.TestSuite:
    return unittest.TestSuite(tcc(documentation) for tcc in [
        TestName,
        TestSingleLineDescriptionStr,
        TestSingleLineDescription,
        TestNameAndSingleLineDescriptionStr,
        TestNameAndSingleLineDescription,
        TestActPhaseContents,
        TestActPhaseContentsSyntax,
        TestActPhaseNotes,
        TestSeeAlso,
        TestCrossReferenceTarget,
    ])


class WithActorDocumentationBase(TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType):
    def __init__(self, documentation: ActorDocumentation):
        super().__init__(documentation)
        self.documentation = documentation


class TestName(WithActorDocumentationBase):
    def runTest(self):
        actual = self.documentation.singular_name()
        self.assertIsInstance(actual, str, 'name')


class TestSingleLineDescriptionStr(WithActorDocumentationBase):
    def runTest(self):
        actual = self.documentation.single_line_description_str()
        self.assertIsInstance(actual, str, 'single_line_description_str')


class TestSingleLineDescription(WithActorDocumentationBase):
    def runTest(self):
        actual = self.documentation.single_line_description()
        struct_check.is_text.apply_with_message(self, actual, 'single_line_description')


class TestNameAndSingleLineDescriptionStr(WithActorDocumentationBase):
    def runTest(self):
        actual = self.documentation.name_and_single_line_description_str()
        self.assertIsInstance(actual, str, 'name_and_single_line_description_str')


class TestNameAndSingleLineDescription(WithActorDocumentationBase):
    def runTest(self):
        actual = self.documentation.name_and_single_line_description()
        struct_check.is_text.apply_with_message(self, actual, 'name_and_single_line_description')


class TestActPhaseContents(WithActorDocumentationBase):
    def runTest(self):
        actual = self.documentation.act_phase_contents()
        struct_check.is_section_contents.apply_with_message(self, actual, 'act_phase_contents')


class TestActPhaseContentsSyntax(WithActorDocumentationBase):
    def runTest(self):
        actual = self.documentation.act_phase_contents_syntax()
        struct_check.is_section_contents.apply_with_message(self, actual, 'act_phase_contents_syntax')


class TestActPhaseNotes(WithActorDocumentationBase):
    def runTest(self):
        actual = self.documentation.notes()
        struct_check.is_section_contents.apply_with_message(self, actual, 'notes')


class TestSeeAlso(WithActorDocumentationBase):
    def runTest(self):
        actual = self.documentation.see_also_targets()
        asrt_see_also.is_see_also_target_list.apply_with_message(self, actual, 'see_also_items')


class TestCrossReferenceTarget(WithActorDocumentationBase):
    def runTest(self):
        actual = self.documentation.cross_reference_target()
        assertion = xref_va.is_entity_for_type(ACTOR_ENTITY_TYPE_NAMES.identifier)
        assertion.apply_with_message(self, actual, 'cross_reference_target')
