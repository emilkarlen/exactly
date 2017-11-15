from exactly_lib.help.utils.entity_documentation import EntityDocumentation, EntitiesHelp, \
    EntityTypeNames
from exactly_lib.help_texts.entity.concepts import CONFIGURATION_PARAMETER_CONCEPT_INFO
from exactly_lib.help_texts.entity.conf_params import ConfigurationParameterInfo
from exactly_lib.help_texts.name_and_cross_ref import CrossReferenceId
from exactly_lib.help_texts.names import formatting
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.structure.core import ParagraphItem, Text
from exactly_lib.util.textformat.structure.structures import para

CONF_PARAM_ENTITY_TYPE_NAMES = EntityTypeNames(
    CONFIGURATION_PARAMETER_CONCEPT_INFO,
    'confparam',
    formatting.syntax_element(CONFIGURATION_PARAMETER_CONCEPT_INFO.singular_name))


class ConfigurationParameterDocumentation(EntityDocumentation):
    def __init__(self, info: ConfigurationParameterInfo):
        self._info = info

    def single_line_description(self) -> Text:
        return self._info.single_line_description

    def singular_name(self) -> str:
        return self._info.singular_name

    def configuration_parameter_name(self) -> str:
        return self._info.configuration_parameter_name

    def cross_reference_target(self) -> CrossReferenceId:
        return self._info.cross_reference_target

    def purpose(self) -> DescriptionWithSubSections:
        raise NotImplementedError()

    def default_value_str(self) -> str:
        raise NotImplementedError()

    def default_value_para(self) -> ParagraphItem:
        return para(self.default_value_str())

    def summary_paragraphs(self) -> list:
        return [para(self.purpose().single_line_description),
                para('Default value: ' + self.default_value_str())]

    def see_also_targets(self) -> list:
        """
        :returns: A new list of :class:`SeeAlsoTarget`, which may contain duplicate elements.
        """
        return []


def configuration_parameters_help(conf_param_docs: iter) -> EntitiesHelp:
    """
    :param conf_param_docs: [ConfigurationParameterDocumentation]
    """
    return EntitiesHelp(CONF_PARAM_ENTITY_TYPE_NAMES,
                        conf_param_docs)
