import unittest

from exactly_lib.util.textformat.construction.section_hierarchy.generator import SectionHierarchyGenerator
from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib_test.util.textformat.construction.section_hierarchy.test_resources.misc import \
    TEST_NODE_ENVIRONMENT
from exactly_lib_test.util.textformat.construction.section_hierarchy.test_resources.target_info_assertions import \
    is_target_info_node
from exactly_lib_test.util.textformat.construction.test_resources import TargetInfoFactoryTestImpl, \
    CrossReferenceTextConstructorTestImpl
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


def generator_generates_valid_data(put: unittest.TestCase,
                                   sut: SectionHierarchyGenerator):
    node = sut.generate(_TARGET_FACTORY)

    actual_section = node.section_item(TEST_NODE_ENVIRONMENT, _CONSTRUCTION_ENVIRONMENT)
    struct_check.is_section_item.apply_with_message(put, actual_section, 'section')

    actual_target_info_node = node.target_info_node()
    is_target_info_node.apply_with_message(put, actual_target_info_node, 'target-info-node')


_CONSTRUCTION_ENVIRONMENT = ConstructionEnvironment(CrossReferenceTextConstructorTestImpl())

_TARGET_FACTORY = TargetInfoFactoryTestImpl(['target-prefix'])
