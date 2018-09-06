from typing import List

from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity.all_entity_types import CONF_PARAM_ENTITY_TYPE_NAMES
from exactly_lib.definitions.entity.conf_params import ConfigurationParameterInfo
from exactly_lib.help.contents_structure.entity import EntityTypeHelp, \
    EntityDocumentation
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.structure.core import ParagraphItem, StringText, Text
from exactly_lib.util.textformat.structure.structures import para


class ConfigurationParameterDocumentation(EntityDocumentation):
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
        return self._info.default_value_single_line_description

    def default_value_text(self) -> Text:
        return StringText(self.default_value_str())

    def default_value_para(self) -> ParagraphItem:
        return para(self.default_value_text())

    def summary_paragraphs(self) -> list:
        return [para(self.purpose().single_line_description),
                para('Default value: ' + self.default_value_str())]

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        """
        :returns: A new list, which may contain duplicate elements.
        """
        return []


def configuration_parameters_help(conf_param_docs: iter) -> EntityTypeHelp:
    """
    :param conf_param_docs: [ConfigurationParameterDocumentation]
    """
    return EntityTypeHelp(CONF_PARAM_ENTITY_TYPE_NAMES,
                          conf_param_docs)
