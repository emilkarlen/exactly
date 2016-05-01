from exactly_lib.execution import environment_variables
from exactly_lib.help.concepts.concept_structure import PlainConceptDocumentation, Name
from exactly_lib.help.concepts.configuration_parameters.home_directory import HOME_DIRECTORY_CONFIGURATION_PARAMETER
from exactly_lib.help.concepts.plain_concepts.sandbox import SANDBOX_CONCEPT
from exactly_lib.help.utils.description import DescriptionWithSubSections
from exactly_lib.help.utils.formatting import SectionName
from exactly_lib.help.utils.phase_names import SETUP_PHASE_NAME, BEFORE_ASSERT_PHASE_NAME
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.document import SectionContents


class _EnvironmentVariableConcept(PlainConceptDocumentation):
    def __init__(self):
        super().__init__(Name('environment variable', 'environment variables'))

    def purpose(self) -> DescriptionWithSubSections:
        return DescriptionWithSubSections(
            docs.text(_ENVIRONMENT_VARIABLE_SINGLE_LINE_DESCRIPTION),
            SectionContents(normalize_and_parse(_ENVIRONMENT_VARIABLE_REST_DESCRIPTION),
                            [self._variables_from_setup(),
                             self._variables_from_before_assert()]))

    def see_also(self) -> list:
        return [
            SANDBOX_CONCEPT.cross_reference_target(),
            HOME_DIRECTORY_CONFIGURATION_PARAMETER.cross_reference_target(),
        ]

    def _variables_from_setup(self) -> docs.Section:
        return _variables_section(SETUP_PHASE_NAME,
                                  _variables_list_paragraphs([
                                      self._item(environment_variables.ENV_VAR_HOME, _DESCRIPTION_HOME),
                                      self._item(environment_variables.ENV_VAR_ACT, _DESCRIPTION_ACT),
                                      self._item(environment_variables.ENV_VAR_TMP, _DESCRIPTION_TMP),
                                  ]))

    def _variables_from_before_assert(self) -> docs.Section:
        return _variables_section(BEFORE_ASSERT_PHASE_NAME,
                                  _variables_list_paragraphs([
                                      self._item(environment_variables.ENV_VAR_RESULT, _DESCRIPTION_RESULT),
                                  ]))

    def _item(self,
              var_name: str,
              description: str) -> lists.HeaderContentListItem:
        return lists.HeaderContentListItem(docs.text(var_name),
                                           normalize_and_parse(description))


def _variables_section(first_phase_name: SectionName,
                       paragraphs: list) -> docs.Section:
    return docs.section(
        'Variables available in {first_phase_name} and later phases'.format(first_phase_name=first_phase_name.emphasis),
        paragraphs)


def _variables_list_paragraphs(items: list) -> list:
    return [docs.simple_list(items, docs.lists.ListType.VARIABLE_LIST)]


_ENVIRONMENT_VARIABLE_SINGLE_LINE_DESCRIPTION = """\
Environment variables that are available to instructions."""

_ENVIRONMENT_VARIABLE_REST_DESCRIPTION = """\
TODO _ENVIRONMENT_VARIABLE_REST_DESCRIPTION"""

ENVIRONMENT_VARIABLE_CONCEPT = _EnvironmentVariableConcept()

_DESCRIPTION_HOME = """\
TODO
"""

_DESCRIPTION_ACT = """\
TODO
"""

_DESCRIPTION_TMP = """\
TODO
"""

_DESCRIPTION_RESULT = """\
TODO
"""
