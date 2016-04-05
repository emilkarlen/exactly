from shellcheck_lib.cli.program_modes.help.concepts.help_request import ConceptHelpRequest
from shellcheck_lib.cli.program_modes.help.concepts.request_rendering import ConceptHelpRequestRendererResolver
from shellcheck_lib.cli.program_modes.help.html_page.help_request import XHtmlHelpRequest
from shellcheck_lib.cli.program_modes.help.program_modes.help_request import *
from shellcheck_lib.cli.program_modes.help.program_modes.main_program.help_request import MainProgramHelpRequest
from shellcheck_lib.cli.program_modes.help.program_modes.main_program.request_rendering import \
    MainProgramHelpRendererResolver
from shellcheck_lib.cli.program_modes.help.program_modes.test_case.help_request import TestCaseHelpRequest
from shellcheck_lib.cli.program_modes.help.program_modes.test_case.request_rendering import TestCaseHelpRendererResolver
from shellcheck_lib.cli.program_modes.help.program_modes.test_suite.help_request import TestSuiteHelpRequest
from shellcheck_lib.cli.program_modes.help.program_modes.test_suite.request_rendering import \
    TestSuiteHelpRendererResolver
from shellcheck_lib.cli.program_modes.help.request_handling_.console_help import ConsoleHelpRequestHandler
from shellcheck_lib.cli.program_modes.help.request_handling_.html_generation import HtmlGenerationRequestHandler
from shellcheck_lib.cli.program_modes.help.request_handling_.request_handler import RequestHandler
from shellcheck_lib.help.contents_structure import ApplicationHelp
from shellcheck_lib.help.utils.render import SectionContentsRenderer
from shellcheck_lib.util.std import StdOutputFiles


def handle_help_request(output: StdOutputFiles,
                        application_help: ApplicationHelp,
                        help_request: HelpRequest):
    handler = _resolve_handler(application_help,
                               help_request)
    handler.handle(output)


def _resolve_handler(application_help: ApplicationHelp,
                     request: HelpRequest) -> RequestHandler:
    if isinstance(request, XHtmlHelpRequest):
        return HtmlGenerationRequestHandler(application_help)
    else:
        renderer = _renderer(application_help, request)
        return ConsoleHelpRequestHandler(application_help, renderer)


def _renderer(application_help: ApplicationHelp,
              request: HelpRequest) -> SectionContentsRenderer:
    if isinstance(request, MainProgramHelpRequest):
        resolver = MainProgramHelpRendererResolver(application_help.main_program_help)
        return resolver.renderer_for(request)
    if isinstance(request, ConceptHelpRequest):
        resolver = ConceptHelpRequestRendererResolver(application_help.concepts_help)
        return resolver.renderer_for(request)
    if isinstance(request, TestCaseHelpRequest):
        resolver = TestCaseHelpRendererResolver(application_help.test_case_help)
        return resolver.resolve(request)
    if isinstance(request, TestSuiteHelpRequest):
        resolver = TestSuiteHelpRendererResolver(application_help.test_suite_help)
        return resolver.resolve(request)
    raise ValueError('Invalid %s: %s' % (str(HelpRequest), str(type(request))))
