import unittest

from exactly_lib.help.program_modes.test_case.contents.phase import act
from exactly_lib.help.program_modes.test_case.contents.phase import \
    assert_, configuration, before_assert, cleanup, setup
from exactly_lib.help.program_modes.test_case.render import phase_documentation as sut
from exactly_lib.util.textformat.construction.section_contents_constructor import ConstructionEnvironment
from exactly_lib_test.help.test_resources import section_instruction_set, \
    CrossReferenceTextConstructorTestImpl
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestCase)


class TestCase(unittest.TestCase):
    def test_configuration(self):
        # ARRANGE #
        tcp_help = configuration.ConfigurationPhaseDocumentation(
            'phase name',
            section_instruction_set('phase name',
                                    ['instr 1',
                                     'instr 2']))
        # ACT #
        actual = sut.TestCasePhaseDocumentationConstructor(tcp_help).apply(CONSTRUCTION_ENVIRONMENT)
        # ASSERT #
        struct_check.is_article_contents.apply(self, actual)

    def test_setup(self):
        # ARRANGE #
        tcp_help = setup.SetupPhaseDocumentation(
            'phase name',
            section_instruction_set('phase name',
                                    ['instr 1',
                                     'instr 2']))
        # ACT #
        actual = sut.TestCasePhaseDocumentationConstructor(tcp_help).apply(CONSTRUCTION_ENVIRONMENT)
        # ASSERT #
        struct_check.is_article_contents.apply(self, actual)

    def test_act(self):
        # ARRANGE #
        tcp_help = act.ActPhaseDocumentation('phase name')
        # ACT #
        actual = sut.TestCasePhaseDocumentationConstructor(tcp_help).apply(CONSTRUCTION_ENVIRONMENT)
        # ASSERT #
        struct_check.is_article_contents.apply(self, actual)

    def test_before_assert(self):
        # ARRANGE #
        tcp_help = before_assert.BeforeAssertPhaseDocumentation(
            'phase name',
            section_instruction_set('phase name',
                                    ['instr 1',
                                     'instr 2']))
        # ACT #
        actual = sut.TestCasePhaseDocumentationConstructor(tcp_help).apply(CONSTRUCTION_ENVIRONMENT)
        # ASSERT #
        struct_check.is_article_contents.apply(self, actual)

    def test_assert(self):
        # ARRANGE #
        tcp_help = assert_.AssertPhaseDocumentation(
            'phase name',
            section_instruction_set('phase name',
                                    ['instr 1',
                                     'instr 2']))
        # ACT #
        actual = sut.TestCasePhaseDocumentationConstructor(tcp_help).apply(CONSTRUCTION_ENVIRONMENT)
        # ASSERT #
        struct_check.is_article_contents.apply(self, actual)

    def test_cleanup(self):
        # ARRANGE
        tcp_help = cleanup.CleanupPhaseDocumentation(
            'phase name',
            section_instruction_set('phase name',
                                    ['instr 1',
                                     'instr 2']))
        # ACT #
        actual = sut.TestCasePhaseDocumentationConstructor(tcp_help).apply(CONSTRUCTION_ENVIRONMENT)
        # ASSERT #
        struct_check.is_article_contents.apply(self, actual)


CONSTRUCTION_ENVIRONMENT = ConstructionEnvironment(CrossReferenceTextConstructorTestImpl())

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
