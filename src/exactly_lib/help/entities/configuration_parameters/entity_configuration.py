from exactly_lib.definitions.entity.all_entity_types import CONF_PARAM_ENTITY_TYPE_NAMES
from exactly_lib.help.contents_structure.entity import EntityTypeConfiguration
from exactly_lib.help.entities.configuration_parameters import all_configuration_parameters
from exactly_lib.help.entities.configuration_parameters import render
from exactly_lib.help.entities.configuration_parameters.contents_structure import configuration_parameters_help
from exactly_lib.help.render.entities_list_renderer import FlatEntityListHierarchyGeneratorGetter
from exactly_lib.help.render.entity_docs import \
    FlatListConstructorWithSingleLineDescriptionGetter

CONF_PARAM_ENTITY_CONFIGURATION = EntityTypeConfiguration(
    configuration_parameters_help(all_configuration_parameters.all_configuration_parameters()),
    render.IndividualConfParamConstructor,
    FlatListConstructorWithSingleLineDescriptionGetter(),
    FlatEntityListHierarchyGeneratorGetter(CONF_PARAM_ENTITY_TYPE_NAMES.identifier,
                                           render.IndividualConfParamConstructor))
