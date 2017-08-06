from exactly_lib import program_info
from exactly_lib.execution import environment_variables
from exactly_lib.help.concepts.configuration_parameters.home_case_directory import \
    HOME_CASE_DIRECTORY_CONFIGURATION_PARAMETER
from exactly_lib.help.concepts.contents_structure import PlainConceptDocumentation
from exactly_lib.help.concepts.names_and_cross_references import ENVIRONMENT_VARIABLE_CONCEPT_INFO, \
    SANDBOX_CONCEPT_INFO, \
    HOME_CASE_DIRECTORY_CONCEPT_INFO
from exactly_lib.help_texts.names import formatting
from exactly_lib.help_texts.test_case.phase_names import SETUP_PHASE_NAME, BEFORE_ASSERT_PHASE_NAME
from exactly_lib.test_case_file_structure import sandbox_directory_structure as sds
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.document import SectionContents


class _EnvironmentVariableConcept(PlainConceptDocumentation):
    def __init__(self):
        super().__init__(ENVIRONMENT_VARIABLE_CONCEPT_INFO)
        self.format_map = {
            'program_name': formatting.program_name(program_info.PROGRAM_NAME),
            'home_directory': formatting.concept(HOME_CASE_DIRECTORY_CONFIGURATION_PARAMETER.name().singular),
            'act_sub_dir': sds.SUB_DIRECTORY__ACT,
            'tmp_sub_dir': sds.PATH__TMP_USER,
            'result_sub_dir': sds.SUB_DIRECTORY__RESULT,
        }

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
        ]

    def _variables_from_setup(self) -> docs.Section:
        return _variables_section(SETUP_PHASE_NAME,
                                  _variables_list_paragraphs([
                                      self._item(environment_variables.ENV_VAR_HOME_CASE, _DESCRIPTION_HOME),
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
                                           normalize_and_parse(description.format_map(self.format_map)))


def _variables_section(first_phase_name: formatting.SectionName,
                       paragraphs: list) -> docs.Section:
    return docs.section(
        'Variables available in {first_phase_name} and later phases'.format(first_phase_name=first_phase_name.syntax),
        paragraphs)


def _variables_list_paragraphs(items: list) -> list:
    return [docs.simple_list(items, docs.lists.ListType.VARIABLE_LIST)]


ENVIRONMENT_VARIABLE_CONCEPT = _EnvironmentVariableConcept()

_DESCRIPTION_HOME = """\
The absolute path of the {home_directory}.
"""

_DESCRIPTION_ACT = """\
The absolute path of the {act_sub_dir}/ sub directory of the sandbox directory.
"""

_DESCRIPTION_TMP = """\
The absolute path of the {tmp_sub_dir}/ sub directory of the sandbox directory.
"""

_DESCRIPTION_RESULT = """\
The absolute path of the {result_sub_dir}/ sub directory of the sandbox directory.
"""
