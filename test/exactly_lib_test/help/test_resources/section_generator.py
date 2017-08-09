import unittest

from exactly_lib.help.utils.rendering.section_contents_renderer import RenderingEnvironment
from exactly_lib.help.utils.rendering.section_hierarchy_rendering import SectionGenerator
from exactly_lib.help_texts.cross_reference_id import CustomTargetInfoFactory
from exactly_lib_test.help.test_resources import CrossReferenceTextConstructorTestImpl
from exactly_lib_test.help.utils.test_resources_.table_of_contents import is_target_info_node
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


def generator_generates_valid_data(put: unittest.TestCase,
                                   sut: SectionGenerator):
    node = sut.section_renderer_node(_TARGET_FACTORY)

    actual_section = node.section(_RENDERING_ENVIRONMENT)
    struct_check.is_section.apply_with_message(put, actual_section, 'section')

    actual_target_info_node = node.target_info_node()
    is_target_info_node.apply_with_message(put, actual_target_info_node, 'target-info-node')


_RENDERING_ENVIRONMENT = RenderingEnvironment(CrossReferenceTextConstructorTestImpl())

_TARGET_FACTORY = CustomTargetInfoFactory('target-prefix')
