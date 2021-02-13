from typing import List, Sequence

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import syntax_elements, concepts
from exactly_lib.impls.instructions.multi_phase.environ.defs import UNSET_IDENTIFIER, VAR_NAME_ELEMENT
from exactly_lib.impls.instructions.multi_phase.utils.assert_phase_info import IsAHelperIfInAssertPhase
from exactly_lib.util.textformat.structure.core import ParagraphItem


class TheInstructionDocumentation(InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase,
                                  IsAHelperIfInAssertPhase):
    def __init__(self, name: str, is_in_assert_phase: bool = False):
        super().__init__(name, _FORMAT_DICT, is_in_assert_phase)

    def single_line_description(self) -> str:
        return 'Manipulates environment variables'

    def _main_description_rest_body(self) -> List[ParagraphItem]:
        return []

    def _notes__specific(self) -> List[ParagraphItem]:
        return self._tp.fnap(_NOTES)

    def invokation_variants(self) -> Sequence[InvokationVariant]:
        return [
            InvokationVariant(
                self._tp.format('{NAME} = {VALUE}'),
                self._tp.fnap(_DESCRIPTION_OF_SET)),
            InvokationVariant(
                self._tp.format('{unset_keyword} {NAME}'),
                self._tp.fnap('Removes the environment variable {NAME}.')),
        ]

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return [
            syntax_elements.STRING_SYNTAX_ELEMENT.cross_reference_target,
        ]


_FORMAT_DICT = {
    'NAME': VAR_NAME_ELEMENT,
    'VALUE': syntax_elements.STRING_SYNTAX_ELEMENT.singular_name,
    'SYMBOLS': concepts.SYMBOL_CONCEPT_INFO.name.plural,
    'unset_keyword': UNSET_IDENTIFIER,
}

_DESCRIPTION_OF_SET = """\
Sets the environment variable {NAME} to {VALUE}.


Elements of the form "${{var_name}}" in {VALUE}, will be replaced with the value of the environment variable "var_name",
or the empty string, if there is no environment variable with that name.
"""

_NOTES = """\
The manipulation affects all following phases.
"""
