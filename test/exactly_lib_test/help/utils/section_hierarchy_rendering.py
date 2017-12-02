import unittest

from exactly_lib.util.textformat.construction.section_contents_constructor import SectionContentsConstructor, \
    ConstructionEnvironment, \
    ConstantSectionContentsConstructor
from exactly_lib.util.textformat.construction.section_hierarchy import structures, hierarchy
from exactly_lib.util.textformat.construction.section_hierarchy.targets import TargetInfoNode, target_info_leaf, \
    CustomTargetInfoFactory
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import StringText
from exactly_lib_test.help.program_modes.test_case.test_resources import TEST_HIERARCHY_ENVIRONMENT
from exactly_lib_test.help.test_resources import CrossReferenceTextConstructorTestImpl
from exactly_lib_test.help.utils.test_resources_.table_of_contents import equals_target_info_node
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.textformat.construction.test_resources import CustomTargetInfoFactoryTestImpl, \
    equals_custom_cross_ref_test_impl
from exactly_lib_test.util.textformat.test_resources import equals_paragraph_item as asrt_para
from exactly_lib_test.util.textformat.test_resources.section_item_assertions import section_matches, \
    section_contents_matches


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def test_leaf(self):
        # ARRANGE #
        target_factory = CustomTargetInfoFactoryTestImpl(['target_component'])
        expected_section_contents_object = doc.empty_section_contents()
        object_to_test = hierarchy.leaf('header', section_contents(expected_section_contents_object))
        # EXPECTATION #
        expected_target_info = target_factory.root(StringText('header'))

        target_info_node_assertion = equals_target_info_node(
            target_info_leaf(expected_target_info),
            mk_equals_cross_ref_id=equals_custom_cross_ref_test_impl)

        section_assertion = section_matches(
            target=equals_custom_cross_ref_test_impl(expected_target_info.target),
            header=asrt_para.equals_text(expected_target_info.presentation_text),
            contents=asrt.Is(expected_section_contents_object))

        # ACT & ASSERT #
        self._act_and_assert(object_to_test,
                             target_factory,
                             target_info_node_assertion,
                             section_assertion)

    def test_parent_without_sub_sections(self):
        # ARRANGE #
        target_factory = CustomTargetInfoFactoryTestImpl(['target_component'])
        object_to_test = hierarchy.parent('top header', [], [])
        # EXPECTATION #
        expected_target_info = target_factory.root(StringText('top header'))

        target_info_node_assertion = equals_target_info_node(
            target_info_leaf(expected_target_info),
            mk_equals_cross_ref_id=equals_custom_cross_ref_test_impl)

        section_assertion = section_matches(
            target=equals_custom_cross_ref_test_impl(expected_target_info.target),
            header=asrt_para.equals_text(expected_target_info.presentation_text),
            contents=asrt.sub_component('is_empty',
                                        doc.SectionContents.is_empty.fget,
                                        asrt.is_true))
        # ACT & ASSERT #
        self._act_and_assert(object_to_test,
                             target_factory,
                             target_info_node_assertion,
                             section_assertion)

    def test_parent_with_sub_sections(self):
        # ARRANGE #
        target_factory = CustomTargetInfoFactoryTestImpl(['target_component'])
        expected_section_contents_object1 = doc.empty_section_contents()
        expected_section_contents_object2 = docs.section_contents(docs.paras('testing testing'))
        expected_root_initial_paras = docs.paras('root initial paras')
        object_to_test = hierarchy.parent(
            'root header',
            expected_root_initial_paras,
            [('sub-target1', hierarchy.leaf('sub1',
                                            section_contents(expected_section_contents_object1))),
             ('sub-target2', hierarchy.leaf('sub2',
                                            section_contents(expected_section_contents_object2)))
             ])
        # EXPECTATION #
        expected_root_target_info = target_factory.root(StringText('root header'))

        sub1_target = target_factory.sub('sub1', 'sub-target1')
        sub2_target = target_factory.sub('sub2', 'sub-target2')
        target_info_node_assertion = equals_target_info_node(
            TargetInfoNode(expected_root_target_info,
                           [
                               target_info_leaf(sub1_target),
                               target_info_leaf(sub2_target),
                           ]),
            mk_equals_cross_ref_id=equals_custom_cross_ref_test_impl)

        section_assertion2 = section_matches(
            target=equals_custom_cross_ref_test_impl(expected_root_target_info.target),
            header=asrt_para.equals_text(expected_root_target_info.presentation_text),
            contents=section_contents_matches(
                initial_paragraphs=asrt.Is(expected_root_initial_paras),
                sections=asrt.matches_sequence([
                    section_matches(
                        target=equals_custom_cross_ref_test_impl(sub1_target.target),
                        header=asrt_para.equals_text(sub1_target.presentation_text),
                        contents=asrt.Is(expected_section_contents_object1)),
                    section_matches(
                        target=equals_custom_cross_ref_test_impl(sub2_target.target),
                        header=asrt_para.equals_text(sub2_target.presentation_text),
                        contents=asrt.Is(expected_section_contents_object2)),
                ])))
        # ACT & ASSERT #
        self._act_and_assert(object_to_test,
                             target_factory,
                             target_info_node_assertion,
                             section_assertion2)

    def _act_and_assert(self,
                        object_to_test: structures.SectionHierarchyGenerator,
                        target_factory: CustomTargetInfoFactory,
                        target_info_node_assertion: asrt.ValueAssertion,
                        section_assertion: asrt.ValueAssertion):
        # ACT #
        section_renderer_node = object_to_test.generator_node(target_factory)
        actual_target_info_node = section_renderer_node.target_info_node()
        actual_section = section_renderer_node.section_item_constructor(TEST_HIERARCHY_ENVIRONMENT).apply(
            CONSTRUCTION_ENVIRONMENT)
        # ASSERT #
        target_info_node_assertion.apply_with_message(self, actual_target_info_node, 'TargetInfoNode')
        section_assertion.apply_with_message(self, actual_section, 'Section')


def section_contents(x: docs.SectionContents) -> SectionContentsConstructor:
    return ConstantSectionContentsConstructor(x)


CONSTRUCTION_ENVIRONMENT = ConstructionEnvironment(CrossReferenceTextConstructorTestImpl())
