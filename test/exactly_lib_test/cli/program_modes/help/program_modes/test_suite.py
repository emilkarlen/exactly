import unittest

from exactly_lib.cli.program_modes.help.program_modes.test_suite import request_rendering as sut
from exactly_lib.cli.program_modes.help.program_modes.test_suite.help_request import TestSuiteHelpItem
from exactly_lib.help.program_modes.test_case.contents_structure import TestCaseHelp
from exactly_lib_test.common.test_resources.instruction_documentation import instruction_documentation
from exactly_lib_test.help.test_resources.rendering_environment import RENDERING_ENVIRONMENT
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestRenderInstruction)


class TestRenderInstruction(unittest.TestCase):
    def test_renderer_for_instruction_without_including_name(self):
        request = sut.TestSuiteHelpRequest(TestSuiteHelpItem.INSTRUCTION,
                                           'name',
                                           instruction_documentation('name'))
        self._check_resolver_gives_renderer_that_produces_section_contents(request)

    def test_renderer_for_instruction_with_including_name(self):
        request = sut.TestSuiteHelpRequest(TestSuiteHelpItem.INSTRUCTION,
                                           'name',
                                           instruction_documentation('name'),
                                           True)
        self._check_resolver_gives_renderer_that_produces_section_contents(request)

    def _check_resolver_gives_renderer_that_produces_section_contents(self,
                                                                      request: sut.TestSuiteHelpRequest):
        # ARRANGE #
        renderer_resolver = sut.TestSuiteHelpRendererResolver(TestCaseHelp(()))
        # ACT #
        renderer = renderer_resolver.resolve(request)
        # ASSERT #
        actual = renderer.apply(RENDERING_ENVIRONMENT)
        struct_check.is_section_contents.apply_with_message(self, actual,
                                                            'result of rendering')
