import unittest

from exactly_lib.common.help.cross_reference_id import CustomTargetInfoFactory, target_info_leaf, TargetInfo, \
    TargetInfoNode
from exactly_lib.help.utils import section_hierarchy_rendering as sut
from exactly_lib.help.utils.section_contents_renderer import SectionContentsRenderer, RenderingEnvironment
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import AnchorText
from exactly_lib_test.common.help.test_resources import cross_reference_id_va as cross_ref_id_asrt
from exactly_lib_test.help.test_resources import CrossReferenceTextConstructorTestImpl
from exactly_lib_test.help.utils.test_resources_.table_of_contents import equals_target_info_node
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.textformat.test_resources.structure import is_anchor_text, is_string_text_that_equals


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def test_leaf(self):
        # ARRANGE #
        target_factory = CustomTargetInfoFactory('target_component')
        expected_section_contents_object = doc.empty_contents()
        object_to_test = sut.leaf('header', section_contents(expected_section_contents_object))
        # EXPECTATION #
        expected_target_info = target_factory.root('header')

        target_info_node_assertion = equals_target_info_node(target_info_leaf(expected_target_info))

        section_assertion = asrt.And([
            asrt.sub_component('header',
                               doc.Section.header.fget,
                               is_anchor_text_that_corresponds_to(expected_target_info)),
            asrt.sub_component('contents',
                               doc.Section.contents.fget,
                               asrt.Is(expected_section_contents_object))
        ])
        # ACT & ASSERT #
        self._act_and_assert(object_to_test, target_factory,
                             target_info_node_assertion,
                             section_assertion)

    def test_parent_without_sub_sections(self):
        # ARRANGE #
        target_factory = CustomTargetInfoFactory('target_component')
        expected_section_contents_object = doc.empty_contents()
        object_to_test = sut.parent('top header', [], [])
        # EXPECTATION #
        expected_target_info = target_factory.root('top header')

        target_info_node_assertion = equals_target_info_node(target_info_leaf(expected_target_info))

        section_assertion = assert_section(
            header=is_anchor_text_that_corresponds_to(expected_target_info),
            contents=asrt.sub_component('is_empty',
                                        doc.SectionContents.is_empty.fget,
                                        asrt.is_true))
        # ACT & ASSERT #
        self._act_and_assert(object_to_test, target_factory,
                             target_info_node_assertion,
                             section_assertion)

    def test_parent_with_sub_sections(self):
        # ARRANGE #
        target_factory = CustomTargetInfoFactory('target_component')
        expected_section_contents_object1 = doc.empty_contents()
        expected_section_contents_object2 = docs.section_contents(docs.paras('testing testing'))
        expected_root_initial_paras = docs.paras('root initial paras')
        object_to_test = sut.parent(
            'root header',
            expected_root_initial_paras,
            [('sub-target1', sut.leaf('sub1',
                                      section_contents(expected_section_contents_object1))),
             ('sub-target2', sut.leaf('sub2',
                                      section_contents(expected_section_contents_object2)))
             ])
        # EXPECTATION #
        expected_root_target_info = target_factory.root('root header')

        target_info_node_assertion = equals_target_info_node(
            TargetInfoNode(expected_root_target_info,
                           [
                               target_info_leaf(target_factory.sub('sub1', 'sub-target1')),
                               target_info_leaf(target_factory.sub('sub2', 'sub-target2')),
                           ]))

        section_assertion = asrt.And([
            asrt.sub_component(
                'header',
                doc.Section.header.fget,
                is_anchor_text_that_corresponds_to(expected_root_target_info)),
            asrt.sub_component(
                'contents',
                doc.Section.contents.fget,
                asrt.And([
                    asrt.sub_component(
                        'initial_paragraphs',
                        doc.SectionContents.initial_paragraphs.fget,
                        asrt.Is(expected_root_initial_paras)),
                    asrt.sub_component(
                        'sections',
                        doc.SectionContents.sections.fget,
                        asrt.matches_sequence([
                            assert_section(
                                header=is_anchor_text_that_corresponds_to(target_factory.sub('sub1', 'sub-target1')),
                                contents=asrt.Is(expected_section_contents_object1)),
                            assert_section(
                                header=is_anchor_text_that_corresponds_to(target_factory.sub('sub2', 'sub-target2')),
                                contents=asrt.Is(expected_section_contents_object2)),
                        ]))
                ]))
        ])
        # ACT & ASSERT #
        self._act_and_assert(object_to_test, target_factory,
                             target_info_node_assertion,
                             section_assertion)

    def _act_and_assert(self,
                        object_to_test: sut.SectionGenerator,
                        target_factory: CustomTargetInfoFactory,
                        target_info_node_assertion: asrt.ValueAssertion,
                        section_assertion: asrt.ValueAssertion):
        section_renderer_node = object_to_test.section_renderer_node(target_factory)
        actual_target_info_node = section_renderer_node.target_info_node()
        actual_section = section_renderer_node.section_renderer().apply(RENDERING_ENVIRONMENT)

        target_info_node_assertion.apply_with_message(self, actual_target_info_node, 'TargetInfoNode')
        section_assertion.apply_with_message(self, actual_section, 'Section')


def is_anchor_text_that_corresponds_to(expected: TargetInfo) -> asrt.ValueAssertion:
    return asrt.And([
        is_anchor_text,
        asrt.sub_component('anchor',
                           AnchorText.anchor.fget,
                           cross_ref_id_asrt.equals(expected.target)),
        asrt.sub_component('anchored_text',
                           AnchorText.anchored_text.fget,
                           is_string_text_that_equals(expected.presentation_str)),
    ])


def assert_section(header: asrt.ValueAssertion,
                   contents: asrt.ValueAssertion) -> asrt.ValueAssertion:
    return asrt.And([
        asrt.sub_component('header',
                           doc.Section.header.fget,
                           header),
        asrt.sub_component('contents',
                           doc.Section.contents.fget,
                           contents)
    ])


def section_contents(x: docs.SectionContents) -> SectionContentsRenderer:
    return ConstantSectionContentsRenderer(x)


class ConstantSectionContentsRenderer(SectionContentsRenderer):
    def __init__(self, section_contents: docs.SectionContents):
        self.section_contents = section_contents

    def apply(self, environment: RenderingEnvironment) -> docs.SectionContents:
        return self.section_contents


RENDERING_ENVIRONMENT = RenderingEnvironment(CrossReferenceTextConstructorTestImpl())
