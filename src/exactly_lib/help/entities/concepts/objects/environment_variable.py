import operator
from typing import List, Iterable

from exactly_lib import program_info
from exactly_lib.definitions import environment_variables, formatting
from exactly_lib.definitions.cross_ref import name_and_cross_ref
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.doc_format import directory_variable_name_text
from exactly_lib.definitions.entity import conf_params, concepts
from exactly_lib.definitions.entity.concepts import ENVIRONMENT_VARIABLE_CONCEPT_INFO
from exactly_lib.definitions.formatting import InstructionName
from exactly_lib.definitions.test_case import phase_names, phase_infos
from exactly_lib.definitions.test_case.instructions import instruction_names
from exactly_lib.help.entities.concepts.contents_structure import ConceptDocumentation
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.textformat_parser import TextParser


class _EnvironmentVariableConcept(ConceptDocumentation):
    def __init__(self):
        super().__init__(ENVIRONMENT_VARIABLE_CONCEPT_INFO)
        self._tp = TextParser({
            'program_name': formatting.program_name(program_info.PROGRAM_NAME),

            'env_vars__plain': self.name().plural,
            'env_instruction': InstructionName(instruction_names.ENV_VAR_INSTRUCTION_NAME),
            'tcds_concept': formatting.concept_(concepts.TCDS_CONCEPT_INFO),
        })

    def purpose(self) -> DescriptionWithSubSections:
        return DescriptionWithSubSections(
            self.single_line_description(),
            docs.section_contents(
                self._tp.fnap(_INITIAL_PARAGRAPHS),
                [
                    docs.section(self._tp.text('Environment variables set by {program_name}'),
                                 self._tp.fnap(_E_SETS_EXTRA_ENV_VARS),
                                 [
                                     self._variables_from_setup(),
                                     self._variables_from_before_assert(),
                                 ])

                ]))

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        ret_val = name_and_cross_ref.cross_reference_id_list([
            concepts.TCDS_CONCEPT_INFO,
            conf_params.HDS_CASE_DIRECTORY_CONF_PARAM_INFO,
            conf_params.HDS_ACT_DIRECTORY_CONF_PARAM_INFO,
        ])
        ret_val += [
            phase_infos.SETUP.instruction_cross_reference_target(instruction_names.ENV_VAR_INSTRUCTION_NAME)
        ]
        return ret_val

    def _variables_from_setup(self) -> docs.Section:
        return _variables_section(phase_names.SETUP,
                                  _variables_list_paragraphs([
                                      self._item(var_name)
                                      for var_name in map(operator.itemgetter(0),
                                                          environment_variables.ENVIRONMENT_VARIABLES_SET_BEFORE_ACT)
                                  ]))

    def _variables_from_before_assert(self) -> docs.Section:
        return _variables_section(phase_names.BEFORE_ASSERT,
                                  _variables_list_paragraphs([
                                      self._item(var_name)
                                      for var_name in map(operator.itemgetter(0),
                                                          environment_variables.ENVIRONMENT_VARIABLES_SET_AFTER_ACT)
                                  ]))

    def _item(self, var_name: str) -> lists.HeaderContentListItem:
        return docs.list_item(directory_variable_name_text(var_name),
                              environment_variables.ENVIRONMENT_VARIABLE_DESCRIPTION.as_description_paragraphs(
                                  var_name))


def _variables_section(first_phase_name: formatting.SectionName,
                       paragraphs: List[docs.ParagraphItem]) -> docs.Section:
    return docs.section(
        'Variables available in {first_phase_name} and later phases'.format(first_phase_name=first_phase_name.syntax),
        paragraphs)


def _variables_list_paragraphs(items: Iterable[lists.HeaderContentListItem]) -> List[docs.ParagraphItem]:
    return [docs.simple_list(items, docs.lists.ListType.VARIABLE_LIST)]


############################################################
# MENTION
#
# - Which env vars are available
# - Manipulating env vars
# - Scope of change of env vars
############################################################
_INITIAL_PARAGRAPHS = """\
All OS {env_vars__plain}
that are set when {program_name} is started
are available in processes run from a test case.


Environment variables can be manipulated
by the {env_instruction} instruction.


A change of {env_vars__plain} stay in effect for all following instructions and phases.
"""

_E_SETS_EXTRA_ENV_VARS = """\
{program_name} sets additional {env_vars__plain}
that correspond to directories in the {tcds_concept}:
"""

ENVIRONMENT_VARIABLE_CONCEPT = _EnvironmentVariableConcept()
