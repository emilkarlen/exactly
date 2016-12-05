import unittest

from exactly_lib.cli.program_modes.help import suite_reporters as sut
from exactly_lib.cli.program_modes.help.entities_requests import EntityHelpItem, EntityHelpRequest
from exactly_lib.help.entity_names import SUITE_REPORTER_ENTITY_TYPE_NAME
from exactly_lib.help.suite_reporters.contents_structure import suite_reporters_help, SuiteReporterDocumentation
from exactly_lib.help.utils.section_contents_renderer import RenderingEnvironment, SectionContentsRenderer
from exactly_lib_test.help.suite_reporters.test_resources.documentation import SuiteReporterDocTestImpl
from exactly_lib_test.help.test_resources import CrossReferenceTextConstructorTestImpl
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


class TestSuiteReporterHelpRequestRendererResolver(unittest.TestCase):
    def test_all_suite_reporters_list(self):
        # ARRANGE #
        suite_reporters = [
            SuiteReporterDocTestImpl('first'),
            SuiteReporterDocTestImpl('second'),
        ]
        resolver = sut.suite_reporter_help_request_renderer_resolver(suite_reporters_help(suite_reporters))
        # ACT #
        actual = resolver.renderer_for(_suite_reporter_help_request(EntityHelpItem.ALL_ENTITIES_LIST))
        # ASSERT #
        self.assertIsInstance(actual, SectionContentsRenderer)
        # ACT #
        actual_rendition = actual.apply(_RENDERING_ENVIRONMENT)
        # ASSERT #
        struct_check.is_section_contents.apply(self, actual_rendition)

    def test_individual_suite_reporter(self):
        # ARRANGE #
        first_suite_reporter = SuiteReporterDocTestImpl('first suite_reporter')
        suite_reporters = [
            first_suite_reporter,
        ]
        resolver = sut.suite_reporter_help_request_renderer_resolver(suite_reporters_help(suite_reporters))
        # ACT #
        actual = resolver.renderer_for(
            _suite_reporter_help_request(EntityHelpItem.INDIVIDUAL_ENTITY, first_suite_reporter))
        # ASSERT #
        self.assertIsInstance(actual, SectionContentsRenderer)
        # ACT #
        actual_rendition = actual.apply(_RENDERING_ENVIRONMENT)
        # ASSERT #
        struct_check.is_section_contents.apply(self, actual_rendition)


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestSuiteReporterHelpRequestRendererResolver)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())

_RENDERING_ENVIRONMENT = RenderingEnvironment(CrossReferenceTextConstructorTestImpl())


def _suite_reporter_help_request(item: EntityHelpItem,
                                 individual_suite_reporter: SuiteReporterDocumentation = None) -> EntityHelpRequest:
    return EntityHelpRequest(SUITE_REPORTER_ENTITY_TYPE_NAME, item, individual_suite_reporter)
