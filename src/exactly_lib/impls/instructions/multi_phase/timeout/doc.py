from typing import List

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, invokation_variant_from_args
from exactly_lib.definitions import misc_texts
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.definitions.entity import syntax_elements, concepts
from exactly_lib.impls.instructions.multi_phase.utils.assert_phase_info import IsAHelperIfInAssertPhase
from exactly_lib.util.cli_syntax.elements import argument as a
from . import defs


class TheInstructionDocumentation(InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase,
                                  IsAHelperIfInAssertPhase):
    def __init__(self,
                 name: str,
                 is_in_assert_phase: bool = False,
                 ):
        super().__init__(name, _FORMAT_MAP, is_in_assert_phase)
        self._assignment = a.Single(a.Multiplicity.MANDATORY, a.Constant(defs.ASSIGNMENT_IDENTIFIER))

    def single_line_description(self) -> str:
        return self._tp.format(_SINGLE_LINE_DESCRIPTION)

    def invokation_variants(self) -> List[InvokationVariant]:
        return [
            invokation_variant_from_args(
                self._arguments(syntax_elements.INTEGER_SYNTAX_ELEMENT.single_mandatory),
                self._tp.fnap(_DESCRIPTION_INTEGER),
            ),
            invokation_variant_from_args(
                self._arguments(a.Single(a.Multiplicity.MANDATORY, a.Constant(defs.NONE_TOKEN))),
                self._tp.fnap(_DESCRIPTION_NONE),
            ),
        ]

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return cross_reference_id_list([
            syntax_elements.INTEGER_SYNTAX_ELEMENT,
            concepts.TIMEOUT_CONCEPT_INFO,
        ])

    def _arguments(self, value: a.ArgumentUsage) -> List[a.ArgumentUsage]:
        return [
            self._assignment,
            value,
        ]


_SINGLE_LINE_DESCRIPTION = """\
Sets the timeout of individual {os_process:s}
"""

_DESCRIPTION_INTEGER = """\
Sets the timeout to a number of seconds.
"""

_DESCRIPTION_NONE = """\
Sets no timeout.
"""

_FORMAT_MAP = {
    'os_process': misc_texts.OS_PROCESS_NAME,
}
