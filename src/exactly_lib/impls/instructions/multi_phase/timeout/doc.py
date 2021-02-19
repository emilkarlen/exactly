from typing import List

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, invokation_variant_from_args, \
    SyntaxElementDescription
from exactly_lib.definitions import misc_texts
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.definitions.entity import syntax_elements, concepts
from exactly_lib.definitions.test_case.phase_names import PHASE_NAME_DICTIONARY
from exactly_lib.impls.instructions.multi_phase.utils.assert_phase_info import IsAHelperIfInAssertPhase
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure.core import ParagraphItem
from . import defs


class TheInstructionDocumentation(InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase,
                                  IsAHelperIfInAssertPhase):
    def __init__(self,
                 name: str,
                 is_in_assert_phase: bool = False,
                 ):
        super().__init__(name, _FORMAT_MAP, is_in_assert_phase)

    def single_line_description(self) -> str:
        return self._tp.format(_SINGLE_LINE_DESCRIPTION)

    def invokation_variants(self) -> List[InvokationVariant]:
        assignment = a.Single(a.Multiplicity.MANDATORY, a.Constant(defs.ASSIGNMENT_IDENTIFIER))
        return [
            invokation_variant_from_args([
                assignment,
                syntax_elements.INTEGER_SYNTAX_ELEMENT.single_mandatory,
            ])
        ]

    def syntax_element_descriptions(self) -> List[ParagraphItem]:
        return [
            SyntaxElementDescription(
                syntax_elements.INTEGER_SYNTAX_ELEMENT.singular_name,
                self._tp.fnap(_INTEGER_DESCRIPTION))
        ]

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return cross_reference_id_list([
            syntax_elements.INTEGER_SYNTAX_ELEMENT,
            concepts.TIMEOUT_CONCEPT_INFO,
        ])


_SINGLE_LINE_DESCRIPTION = """\
Sets the timeout of individual {os_process:s}
"""

_INTEGER_DESCRIPTION = """\
Timeout in seconds.
"""

_FORMAT_MAP = {
    'default_value_str': concepts.TIMEOUT_CONCEPT_INFO.default,
    'os_process': misc_texts.OS_PROCESS_NAME,
    'phase': PHASE_NAME_DICTIONARY,
    'instruction': concepts.INSTRUCTION_CONCEPT_INFO.name,
}
