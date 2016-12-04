from exactly_lib.cli.program_modes.help.entities_requests import EntityHelpRequestRendererResolver
from exactly_lib.help.suite_reporters import render
from exactly_lib.help.utils.entity_documentation import EntitiesHelp


def suite_reporter_help_request_renderer_resolver(
        suite_reporters_help: EntitiesHelp) -> EntityHelpRequestRendererResolver:
    return EntityHelpRequestRendererResolver(render.IndividualSuiteReporterRenderer,
                                             render.all_suite_reporters_list_renderer,
                                             suite_reporters_help.all_entities)
