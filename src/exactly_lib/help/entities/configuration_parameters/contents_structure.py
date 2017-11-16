from exactly_lib.help.utils.entity_documentation import EntitiesHelp, \
    EntityDocumentationBase
from exactly_lib.help_texts.entity.conf_params import ConfigurationParameterInfo, CONF_PARAM_ENTITY_TYPE_NAMES
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.structures import para


class ConfigurationParameterDocumentation(EntityDocumentationBase):
    def __init__(self, info: ConfigurationParameterInfo):
        super().__init__(info)
        self._info = info

    @property
    def name_and_cross_ref_target(self) -> ConfigurationParameterInfo:
        return self._info

    def configuration_parameter_name(self) -> str:
        return self._info.configuration_parameter_name

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
