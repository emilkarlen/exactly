from exactly_lib.definitions.entity.all_entity_types import SUITE_REPORTER_ENTITY_TYPE_NAMES
from exactly_lib.help.contents_structure.entity import EntityTypeConfiguration
from exactly_lib.help.entities.suite_reporters import render
from exactly_lib.help.entities.suite_reporters.contents_structure import suite_reporters_help
from exactly_lib.help.entities.suite_reporters.objects.all_suite_reporters import ALL_SUITE_REPORTERS
from exactly_lib.help.render.entities_list_renderer import FlatEntityListHierarchyGeneratorGetter
from exactly_lib.help.render.entity_docs import \
    FlatListConstructorWithSingleLineDescriptionGetter

SUITE_REPORTER_ENTITY_CONFIGURATION = EntityTypeConfiguration(
    suite_reporters_help(ALL_SUITE_REPORTERS),
    render.IndividualSuiteReporterConstructor,
    FlatListConstructorWithSingleLineDescriptionGetter(),
    FlatEntityListHierarchyGeneratorGetter(SUITE_REPORTER_ENTITY_TYPE_NAMES.identifier,
                                           render.IndividualSuiteReporterConstructor),
)
