from exactly_lib.cli.program_modes.help.argument_parsing import ENTITY_TYPE_NAME_2_ENTITY_HELP_FROM_APP_HELP_GETTER
from exactly_lib.cli.program_modes.help.entities_requests import EntityHelpRequest, EntityHelpRequestRendererResolver
from exactly_lib.cli.program_modes.help.html_doc.help_request import HtmlDocHelpRequest
from exactly_lib.cli.program_modes.help.html_doc.request_rendering import HtmlGenerationRequestHandler
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
from exactly_lib.help.utils.section_contents_renderer import SectionContentsRenderer
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
    if isinstance(request, TestCaseHelpRequest):
        resolver = TestCaseHelpRendererResolver(application_help.test_case_help)
        return resolver.resolve(request)
    if isinstance(request, TestSuiteHelpRequest):
        resolver = TestSuiteHelpRendererResolver(application_help.test_suite_help)
        return resolver.resolve(request)
    if isinstance(request, EntityHelpRequest):
        resolver = _entity_help_request_renderer_resolver_for(application_help, request)
        return resolver.renderer_for(request)
    raise TypeError('Invalid %s: %s' % (str(HelpRequest), str(type(request))))


def _entity_help_request_renderer_resolver_for(application_help: ApplicationHelp,
                                               request: EntityHelpRequest) -> EntityHelpRequestRendererResolver:
    from exactly_lib.cli.program_modes.help.actors import actor_help_request_renderer_resolver
    from exactly_lib.cli.program_modes.help.concepts import concept_help_request_renderer_resolver
    from exactly_lib.cli.program_modes.help.suite_reporters import suite_reporter_help_request_renderer_resolver
    from exactly_lib.help.entity_names import ACTOR_ENTITY_TYPE_NAME, CONCEPT_ENTITY_TYPE_NAME, \
        SUITE_REPORTER_ENTITY_TYPE_NAME
    resolvers = {
        ACTOR_ENTITY_TYPE_NAME: actor_help_request_renderer_resolver,
        CONCEPT_ENTITY_TYPE_NAME: concept_help_request_renderer_resolver,
        SUITE_REPORTER_ENTITY_TYPE_NAME: suite_reporter_help_request_renderer_resolver,
    }
    try:
        renderer_resolver = resolvers[request.entity_type]
    except KeyError:
        raise ValueError('Non existing entity: ' + str(request.entity_type))
    get_entity_help_from_app_help = ENTITY_TYPE_NAME_2_ENTITY_HELP_FROM_APP_HELP_GETTER[request.entity_type]
    return renderer_resolver(get_entity_help_from_app_help(application_help))
