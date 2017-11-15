from exactly_lib.help.contents_structure import EntityConfiguration
from exactly_lib.help.entities.configuration_parameters import all_configuration_parameters
from exactly_lib.help.entities.configuration_parameters import render
from exactly_lib.help.entities.configuration_parameters.contents_structure import configuration_parameters_help
from exactly_lib.help.html_doc.parts.utils.entities_list_renderer import FlatEntityListHierarchyGeneratorGetter
from exactly_lib.help.utils.rendering.entity_documentation_rendering import \
    FlatListRendererWithSingleLineDescriptionGetter

CONF_PARAM_ENTITY_CONFIGURATION = EntityConfiguration(
    configuration_parameters_help(all_configuration_parameters.all_configuration_parameters()),
    render.IndividualConfParamRenderer,
    FlatListRendererWithSingleLineDescriptionGetter(),
    FlatEntityListHierarchyGeneratorGetter(render.IndividualConfParamRenderer))
