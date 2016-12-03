from exactly_lib.cli.program_modes.help.actors.help_request import ActorHelpRequest
from exactly_lib.cli.program_modes.help.concepts.help_request import ConceptHelpRequest
from exactly_lib.cli.program_modes.help.html_documentation.help_request import HtmlDocHelpRequest
from exactly_lib.cli.program_modes.help.html_documentation.request_rendering import HtmlGenerationRequestHandler
from exactly_lib.cli.program_modes.help.program_modes.help_request import *
from exactly_lib.cli.program_modes.help.program_modes.main_program.help_request import MainProgramHelpRequest
from exactly_lib.cli.program_modes.help.program_modes.main_program.request_rendering import \
    MainProgramHelpRendererResolver
from exactly_lib.cli.program_modes.help.program_modes.test_case.help_request import TestCaseHelpRequest
from exactly_lib.cli.program_modes.help.program_modes.test_case.request_rendering import TestCaseHelpRendererResolver
from exactly_lib.cli.program_modes.help.program_modes.test_suite.help_request import TestSuiteHelpRequest
from exactly_lib.cli.program_modes.help.program_modes.test_suite.request_rendering import \
    TestSuiteHelpRendererResolver
from exactly_lib.cli.program_modes.help.request_handling.console_help import ConsoleHelpRequestHandler
from exactly_lib.cli.program_modes.help.request_handling.request_handler import RequestHandler
from exactly_lib.help.contents_structure import ApplicationHelp
from exactly_lib.help.utils.render import SectionContentsRenderer
from exactly_lib.util.std import StdOutputFiles


def handle_help_request(output: StdOutputFiles,
                        application_help: ApplicationHelp,
                        help_request: HelpRequest):
    handler = _resolve_handler(application_help,
                               help_request)
    handler.handle(output)


def _resolve_handler(application_help: ApplicationHelp,
                     request: HelpRequest) -> RequestHandler:
    if isinstance(request, HtmlDocHelpRequest):
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
        from exactly_lib.cli.program_modes.help.concepts import request_rendering
        resolver = request_rendering.concept_help_request_renderer_resolver(application_help.concepts_help)
        return resolver.renderer_for(request)
    if isinstance(request, ActorHelpRequest):
        from exactly_lib.cli.program_modes.help.actors import request_rendering
        resolver = request_rendering.actor_help_request_renderer_resolver(application_help.actors_help)
        return resolver.renderer_for(request)
    if isinstance(request, TestCaseHelpRequest):
        resolver = TestCaseHelpRendererResolver(application_help.test_case_help)
        return resolver.resolve(request)
    if isinstance(request, TestSuiteHelpRequest):
        resolver = TestSuiteHelpRendererResolver(application_help.test_suite_help)
        return resolver.resolve(request)
    raise TypeError('Invalid %s: %s' % (str(HelpRequest), str(type(request))))
