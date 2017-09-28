import operator

from exactly_lib.help.entities.concepts.contents_structure import PlainConceptDocumentation
from exactly_lib.help_texts import environment_variables
from exactly_lib.help_texts.entity.concepts import ENVIRONMENT_VARIABLE_CONCEPT_INFO, \
    SANDBOX_CONCEPT_INFO, \
    HOME_CASE_DIRECTORY_CONCEPT_INFO, HOME_ACT_DIRECTORY_CONCEPT_INFO
from exactly_lib.help_texts.names import formatting
from exactly_lib.help_texts.test_case.phase_names import SETUP_PHASE_NAME, BEFORE_ASSERT_PHASE_NAME
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.document import SectionContents


class _EnvironmentVariableConcept(PlainConceptDocumentation):
    def __init__(self):
        super().__init__(ENVIRONMENT_VARIABLE_CONCEPT_INFO)

    def purpose(self) -> DescriptionWithSubSections:
        return DescriptionWithSubSections(
            self.single_line_description(),
            SectionContents([],
                            [self._variables_from_setup(),
                             self._variables_from_before_assert()]))

    def _see_also_cross_refs(self) -> list:
        return [
            SANDBOX_CONCEPT_INFO.cross_reference_target,
            HOME_CASE_DIRECTORY_CONCEPT_INFO.cross_reference_target,
            HOME_ACT_DIRECTORY_CONCEPT_INFO.cross_reference_target,
        ]

    def _variables_from_setup(self) -> docs.Section:
        return _variables_section(SETUP_PHASE_NAME,
                                  _variables_list_paragraphs([
                                      self._item(var_name)
                                      for var_name in map(operator.itemgetter(0),
                                                          environment_variables.ENVIRONMENT_VARIABLES_SET_BEFORE_ACT)
                                  ]))

    def _variables_from_before_assert(self) -> docs.Section:
        return _variables_section(BEFORE_ASSERT_PHASE_NAME,
                                  _variables_list_paragraphs([
                                      self._item(var_name)
                                      for var_name in map(operator.itemgetter(0),
                                                          environment_variables.ENVIRONMENT_VARIABLES_SET_AFTER_ACT)
                                  ]))

    def _item(self, var_name: str) -> lists.HeaderContentListItem:
        return lists.HeaderContentListItem(docs.text(var_name),
                                           environment_variables.ENVIRONMENT_VARIABLE_DESCRIPTION.as_description_paragraphs(
                                               var_name))


def _variables_section(first_phase_name: formatting.SectionName,
                       paragraphs: list) -> docs.Section:
    return docs.section(
        'Variables available in {first_phase_name} and later phases'.format(first_phase_name=first_phase_name.syntax),
        paragraphs)


def _variables_list_paragraphs(items: list) -> list:
    return [docs.simple_list(items, docs.lists.ListType.VARIABLE_LIST)]


ENVIRONMENT_VARIABLE_CONCEPT = _EnvironmentVariableConcept()
