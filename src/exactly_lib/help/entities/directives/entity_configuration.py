from exactly_lib.definitions.entity.all_entity_types import DIRECTIVE_ENTITY_TYPE_NAMES
from exactly_lib.help.contents_structure.entity import EntityTypeConfiguration
from exactly_lib.help.entities.directives import render
from exactly_lib.help.entities.directives.all_directives import all_directives
from exactly_lib.help.entities.directives.contents_structure import directives_help
from exactly_lib.help.render.entities_list_renderer import FlatEntityListHierarchyGeneratorGetter
from exactly_lib.help.render.entity_docs import \
    FlatListConstructorWithSingleLineDescriptionGetter

DIRECTIVE_ENTITY_CONFIGURATION = EntityTypeConfiguration(
    directives_help(all_directives()),
    render.IndividualDirectiveConstructor,
    FlatListConstructorWithSingleLineDescriptionGetter(),
    FlatEntityListHierarchyGeneratorGetter(DIRECTIVE_ENTITY_TYPE_NAMES.identifier,
                                           render.IndividualDirectiveConstructor),
)
