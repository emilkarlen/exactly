from exactly_lib.help.contents_structure import EntityConfiguration
from exactly_lib.help.entities.suite_reporters import render
from exactly_lib.help.entities.suite_reporters.contents_structure import suite_reporters_help
from exactly_lib.help.entities.suite_reporters.objects.all_suite_reporters import ALL_SUITE_REPORTERS
from exactly_lib.help.html_doc.parts.utils.entities_list_renderer import FlatEntityListHierarchyGeneratorGetter
from exactly_lib.help.utils.rendering.entity_documentation_rendering import \
    FlatListRendererWithSingleLineDescriptionGetter

SUITE_REPORTER_ENTITY_CONFIGURATION = EntityConfiguration(
    suite_reporters_help(ALL_SUITE_REPORTERS),
    render.IndividualSuiteReporterRenderer,
    FlatListRendererWithSingleLineDescriptionGetter(),
    FlatEntityListHierarchyGeneratorGetter(render.IndividualSuiteReporterRenderer),
)
