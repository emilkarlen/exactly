from exactly_lib.cli.definitions import exit_codes
from exactly_lib.cli.program_modes.help.entities_requests import EntityHelpRequest, EntityHelpRequestRendererResolver
from exactly_lib.cli.program_modes.help.html_doc.help_request import HtmlDocHelpRequest
from exactly_lib.cli.program_modes.help.html_doc.request_rendering import HtmlGenerationRequestHandler
from exactly_lib.cli.program_modes.help.program_modes.help_request import *
from exactly_lib.cli.program_modes.help.program_modes.main_program.help_request import MainProgramHelpRequest
from exactly_lib.cli.program_modes.help.program_modes.main_program.request_rendering import \
    MainProgramHelpRendererResolver
from exactly_lib.cli.program_modes.help.program_modes.symbol.help_request import SymbolHelpRequest
from exactly_lib.cli.program_modes.help.program_modes.symbol.request_rendering import SymbolHelpConstructorResolver
from exactly_lib.cli.program_modes.help.program_modes.test_case.help_request import TestCaseHelpRequest
from exactly_lib.cli.program_modes.help.program_modes.test_case.request_rendering import TestCaseHelpConstructorResolver
from exactly_lib.cli.program_modes.help.program_modes.test_suite.help_request import TestSuiteHelpRequest
from exactly_lib.cli.program_modes.help.program_modes.test_suite.request_rendering import \
    TestSuiteHelpConstructorResolver
from exactly_lib.cli.program_modes.help.request_handling.console_help import ConsoleHelpRequestHandler
from exactly_lib.cli.program_modes.help.request_handling.request_handler import RequestHandler
from exactly_lib.common.process_result_reporter import ProcessResultReporter, Environment
from exactly_lib.help.contents_structure.application import ApplicationHelp
from exactly_lib.help.contents_structure.entity import EntityTypeConfiguration
from exactly_lib.util.std import StdOutputFiles
from exactly_lib.util.textformat.constructor.section import \
    SectionContentsConstructor


def handle_help_request(output: StdOutputFiles,
                        application_help: ApplicationHelp,
                        help_request: HelpRequest):
    handler = _resolve_handler(application_help,
                               help_request)
    handler.handle(output)


def handle_help_request_rr(application_help: ApplicationHelp,
                           help_request: HelpRequest) -> ProcessResultReporter:
    handler = _resolve_handler(application_help,
                               help_request)
    return _ReporterOfHandler(handler)


class _ReporterOfHandler(ProcessResultReporter):
    def __init__(self, handler: RequestHandler):
        self._handler = handler

    def report(self, environment: Environment) -> int:
        self._handler.handle(environment.std_files)

        return exit_codes.EXIT_OK


def _resolve_handler(application_help: ApplicationHelp,
                     request: HelpRequest) -> RequestHandler:
    if isinstance(request, HtmlDocHelpRequest):
        return HtmlGenerationRequestHandler(application_help)
    else:
        renderer = _renderer(application_help, request)
        return ConsoleHelpRequestHandler(application_help, renderer)


def _renderer(application_help: ApplicationHelp,
              request: HelpRequest) -> SectionContentsConstructor:
    if isinstance(request, MainProgramHelpRequest):
        resolver = MainProgramHelpRendererResolver(application_help.main_program_help)
        return resolver.renderer_for(request)
    if isinstance(request, TestCaseHelpRequest):
        resolver = TestCaseHelpConstructorResolver(application_help.test_case_help)
        return resolver.resolve(request)
    if isinstance(request, TestSuiteHelpRequest):
        resolver = TestSuiteHelpConstructorResolver(application_help.test_suite_help)
        return resolver.resolve(request)
    if isinstance(request, SymbolHelpRequest):
        resolver = SymbolHelpConstructorResolver()
        return resolver.resolve(request)
    if isinstance(request, EntityHelpRequest):
        resolver = _entity_help_request_renderer_resolver_for(application_help, request)
        return resolver.renderer_for(request)
    raise TypeError('Invalid %s: %s' % (str(HelpRequest), str(type(request))))


def _entity_help_request_renderer_resolver_for(application_help: ApplicationHelp,
                                               request: EntityHelpRequest) -> EntityHelpRequestRendererResolver:
    try:
        entity_conf = application_help.entity_type_id_2_entity_type_conf[request.entity_type]
        assert isinstance(entity_conf, EntityTypeConfiguration), ('Must be an ' + str(EntityTypeConfiguration))
    except KeyError:
        raise ValueError('Entity is not found in application help: ' + request.entity_type)
    return EntityHelpRequestRendererResolver(entity_conf.entity_doc_2_article_contents_renderer,
                                             entity_conf.cli_list_constructor_getter,
                                             entity_conf.entities_help.all_entities)
