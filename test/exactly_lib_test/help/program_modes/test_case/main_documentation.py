import unittest

from exactly_lib.help.program_modes.test_case.contents.main import specification as sut
from exactly_lib.help.utils.rendering.section_contents_renderer import RenderingEnvironment
from exactly_lib.help_texts.cross_reference_id import CustomTargetInfoFactory
from exactly_lib_test.help.program_modes.test_case.test_resources import test_case_help_with_production_phases
from exactly_lib_test.help.test_resources import CrossReferenceTextConstructorTestImpl
from exactly_lib_test.help.utils.test_resources_.table_of_contents import is_target_info_node
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    test_case_help = test_case_help_with_production_phases()

    def test_document_structure(self):
        # ARRANGE #
        rendering_environment = RenderingEnvironment(CrossReferenceTextConstructorTestImpl())
        generator = sut.generator('header', self.test_case_help)
        # ACT #
        actual = generator.section_renderer_node(CustomTargetInfoFactory('prefix')).section(rendering_environment)
        # ASSERT #
        struct_check.is_section.apply(self, actual)

    def test_target_info_hierarchy(self):
        # ARRANGE #
        generator = sut.generator('header', self.test_case_help)
        # ACT #
        actual = generator.section_renderer_node(CustomTargetInfoFactory('prefix')).target_info_node()
        # ASSERT #
        is_target_info_node.apply(self, actual)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
