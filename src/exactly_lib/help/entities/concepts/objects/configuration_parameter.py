from typing import List

from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.name_and_cross_ref import SingularNameAndCrossReferenceId
from exactly_lib.definitions.entity.concepts import CONFIGURATION_PARAMETER_CONCEPT_INFO
from exactly_lib.definitions.entity.conf_params import ALL_CONF_PARAM_INFOS
from exactly_lib.definitions.test_case import phase_infos
from exactly_lib.definitions.test_suite import section_infos
from exactly_lib.help.entities.concepts.contents_structure import ConceptDocumentation
from exactly_lib.util.description import Description, DescriptionWithSubSections, from_simple_description
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem


class _ConfigurationParameterConcept(ConceptDocumentation):
    def __init__(self):
        super().__init__(CONFIGURATION_PARAMETER_CONCEPT_INFO)

    def purpose(self) -> DescriptionWithSubSections:
        return from_simple_description(
            Description(self.single_line_description(),
                        [_sorted_conf_params_list()]))

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return [
            phase_infos.CONFIGURATION.cross_reference_target,
            section_infos.CONFIGURATION.cross_reference_target,
        ]


def _sorted_conf_params_list() -> ParagraphItem:
    all_cfs = sorted(ALL_CONF_PARAM_INFOS,
                     key=SingularNameAndCrossReferenceId.singular_name.fget)
    items = [docs.list_item(docs.cross_reference(cf.configuration_parameter_name_text,
                                                 cf.cross_reference_target,
                                                 allow_rendering_of_visible_extra_target_text=False),
                            docs.paras(cf.single_line_description_str))
             for cf in all_cfs]
    return lists.HeaderContentList(items,
                                   lists.Format(lists.ListType.VARIABLE_LIST,
                                                custom_indent_spaces=0,
                                                custom_separations=docs.SEPARATION_OF_HEADER_AND_CONTENTS))


CONFIGURATION_PARAMETER_CONCEPT = _ConfigurationParameterConcept()
