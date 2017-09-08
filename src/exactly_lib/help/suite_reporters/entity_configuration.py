from exactly_lib.help.contents_structure import EntityConfiguration
from exactly_lib.help.suite_reporters.contents_structure import suite_reporters_help
from exactly_lib.help.suite_reporters.render import IndividualSuiteReporterRenderer
from exactly_lib.help.suite_reporters.suite_reporter.all_suite_reporters import ALL_SUITE_REPORTERS
from exactly_lib.help.utils.rendering.entity_documentation_rendering import \
    FlatListRendererWithSingleLineDescriptionGetter

SUITE_REPORTER_ENTITY_CONFIGURATION = EntityConfiguration(suite_reporters_help(ALL_SUITE_REPORTERS),
                                                          IndividualSuiteReporterRenderer,
                                                          FlatListRendererWithSingleLineDescriptionGetter())
