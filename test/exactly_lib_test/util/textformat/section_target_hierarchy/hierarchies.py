import unittest

from exactly_lib.util.textformat.constructor import sections, paragraphs
from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib.util.textformat.constructor.section import \
    SectionContentsConstructor
from exactly_lib.util.textformat.section_target_hierarchy import hierarchies as sut, generator
from exactly_lib.util.textformat.section_target_hierarchy.targets import TargetInfoNode, target_info_leaf, \
    TargetInfoFactory, TargetInfo
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import StringText
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.util.textformat.constructor.test_resources import equals_custom_cross_ref_test_impl, \
    CrossReferenceTextConstructorTestImpl, CustomCrossReferenceTargetTestImpl
from exactly_lib_test.util.textformat.section_target_hierarchy.test_resources.misc import \
    TEST_NODE_ENVIRONMENT, TargetInfoFactoryTestImpl, ConstantTargetInfoFactoryTestImpl
from exactly_lib_test.util.textformat.section_target_hierarchy.test_resources.target_info_assertions import \
    equals_target_info_node
from exactly_lib_test.util.textformat.test_resources import equals_paragraph_item as asrt_para
from exactly_lib_test.util.textformat.test_resources.section_item_assertions import section_matches, \
    section_contents_matches


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(Test),
        unittest.makeSuite(TestAdjusters),
    ])


class TestBase(unittest.TestCase):

    def _act_and_assert(self,
                        object_to_test: generator.SectionHierarchyGenerator,
                        target_factory: TargetInfoFactory,
                        target_info_node_assertion: Assertion[TargetInfoNode],
                        section_item_assertion: Assertion[docs.SectionItem]):
        # ACT #
        section_renderer_node = object_to_test.generate(target_factory)
        actual_target_info_node = section_renderer_node.target_info_node()
        actual_section = section_renderer_node.section_item_constructor(TEST_NODE_ENVIRONMENT).apply(
            CONSTRUCTION_ENVIRONMENT)
        # ASSERT #
        target_info_node_assertion.apply_with_message(self, actual_target_info_node, 'TargetInfoNode')
        section_item_assertion.apply_with_message(self, actual_section, 'Section')


class TestAdjusters(TestBase):
    def test_leaf_not_in_toc(self):
        # ARRANGE #
        target_factory = TargetInfoFactoryTestImpl(['target_component'])
        expected_section_contents_object = doc.empty_section_contents()
        header = StringText('header')
        generator_to_test = sut.leaf_not_in_toc(header.value,
                                                section_contents(expected_section_contents_object))
        # EXPECTATION #

        target_info_node_assertion = asrt.is_none

        section_assertion = section_matches(
            target=asrt.is_none,
            header=asrt_para.equals_text(header),
            contents=asrt.Is(expected_section_contents_object))

        # ACT & ASSERT #
        self._act_and_assert(generator_to_test,
                             target_factory,
                             target_info_node_assertion,
                             section_assertion)

    def test_with_fixed_root_target(self):
        # ARRANGE #

        root_header = StringText('root header')
        sub_header = StringText('sub header')
        sub_local_target_name = 'should not be used'

        fixed_target = CustomCrossReferenceTargetTestImpl('the fixed root target')

        default_target = CustomCrossReferenceTargetTestImpl('default target component')

        target_factory = ConstantTargetInfoFactoryTestImpl(default_target)

        unadjusted_object = sut.hierarchy(root_header,
                                          paragraphs.empty(),
                                          [sut.child(sub_local_target_name,
                                                     sut.leaf(sub_header.value,
                                                              section_contents(doc.empty_section_contents())))
                                           ]
                                          )
        adjusted_object = sut.with_fixed_root_target(fixed_target,
                                                     unadjusted_object)

        # EXPECTATION #

        expected_root_target_info = TargetInfo(root_header,
                                               fixed_target)

        expected_sub_target_info = TargetInfo(sub_header,
                                              default_target)

        target_info_node_assertion = equals_target_info_node(
            TargetInfoNode(expected_root_target_info,
                           [target_info_leaf(expected_sub_target_info)]),
            mk_equals_cross_ref_id=equals_custom_cross_ref_test_impl)

        section_assertion = section_matches(
            target=equals_custom_cross_ref_test_impl(fixed_target),
            header=asrt_para.equals_text(expected_root_target_info.presentation_text),
            contents=section_contents_matches(
                initial_paragraphs=asrt.is_empty_sequence,
                sections=asrt.matches_sequence([
                    section_matches(
                        target=equals_custom_cross_ref_test_impl(default_target),
                        header=asrt_para.equals_text(sub_header),
                        contents=section_contents_matches(
                            initial_paragraphs=asrt.is_empty_sequence,
                            sections=asrt.is_empty_sequence
                        )
                    )
                ])
            ))

        # ACT & ASSERT #

        self._act_and_assert(adjusted_object,
                             target_factory,
                             target_info_node_assertion,
                             section_assertion)


class Test(TestBase):
    def test_leaf(self):
        # ARRANGE #
        target_factory = TargetInfoFactoryTestImpl(['target_component'])
        expected_section_contents_object = doc.empty_section_contents()
        object_to_test = sut.leaf('header', section_contents(expected_section_contents_object))
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

    def test_hierarchy_without_sub_sections(self):
        # ARRANGE #
        target_factory = TargetInfoFactoryTestImpl(['target_component'])
        root_header_text = StringText('root header')
        object_to_test = sut.hierarchy(root_header_text, paragraphs.empty(), [])
        # EXPECTATION #
        expected_target_info = target_factory.root(root_header_text)

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

    def test_hierarchy_with_sub_sections(self):
        # ARRANGE #

        target_factory = TargetInfoFactoryTestImpl(['target_component'])
        expected_section_contents_object1 = doc.empty_section_contents()
        expected_section_contents_object2 = docs.section_contents(docs.paras('testing testing'))
        expected_root_initial_para = docs.para('root initial paras')
        expected_root_initial_paras = [expected_root_initial_para]

        root_header = StringText('root header')

        sub_section_header_1 = 'sub1'
        sub_section_header_2 = 'sub2'
        sub_section_local_target_1 = 'sub-target1'
        sub_section_local_target_2 = 'sub-target2'

        object_to_test = sut.hierarchy(
            root_header,
            paragraphs.constant(expected_root_initial_paras),
            [sut.child(sub_section_local_target_1,
                       sut.leaf(sub_section_header_1,
                                section_contents(expected_section_contents_object1))),
             sut.child(sub_section_local_target_2,
                       sut.leaf(sub_section_header_2,
                                section_contents(expected_section_contents_object2)))
             ])
        # EXPECTATION #
        expected_root_target_info = target_factory.root(root_header)

        sub1_target = target_factory.sub(sub_section_header_1, sub_section_local_target_1)
        sub2_target = target_factory.sub(sub_section_header_2, sub_section_local_target_2)
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
                initial_paragraphs=asrt.matches_sequence([asrt.Is(expected_root_initial_para)]),
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


def section_contents(x: docs.SectionContents) -> SectionContentsConstructor:
    return sections.constant_contents(x)


CONSTRUCTION_ENVIRONMENT = ConstructionEnvironment(CrossReferenceTextConstructorTestImpl())
