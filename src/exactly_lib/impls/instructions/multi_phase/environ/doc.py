from typing import List, Sequence

from exactly_lib.common.help import headers
from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, invokation_variant_from_args, \
    SyntaxElementDescription
from exactly_lib.definitions import misc_texts
from exactly_lib.definitions.cross_ref import name_and_cross_ref
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import syntax_elements, concepts, types
from exactly_lib.definitions.test_case import phase_names
from exactly_lib.impls.instructions.multi_phase.environ import defs
from exactly_lib.impls.instructions.multi_phase.utils.assert_phase_info import IsAHelperIfInAssertPhase
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure.core import ParagraphItem


class TheInstructionDocumentation(InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase,
                                  IsAHelperIfInAssertPhase):
    def __init__(self, name: str, is_in_assert_phase: bool = False):
        super().__init__(name, _FORMAT_DICT, is_in_assert_phase)

    def single_line_description(self) -> str:
        return self._tp.format('Manipulates {env_var:s}')

    def _main_description_rest_body(self) -> List[ParagraphItem]:
        return []

    def _notes__specific(self) -> List[ParagraphItem]:
        return self._tp.fnap(_NOTES)

    def invokation_variants(self) -> Sequence[InvokationVariant]:
        phase_spec = a.Single(a.Multiplicity.OPTIONAL, a.Named(defs.PHASE_SPEC_ELEMENT))
        name = a.Single(a.Multiplicity.MANDATORY, a.Named(defs.VAR_NAME_ELEMENT))
        assignment = a.Single(a.Multiplicity.MANDATORY, a.Constant(defs.ASSIGNMENT_IDENTIFIER))
        unset_kw = a.Single(a.Multiplicity.MANDATORY, a.Constant(defs.UNSET_IDENTIFIER))
        return [
            invokation_variant_from_args(
                [phase_spec, name, assignment, _VALUE_SE.single_mandatory],
                self._tp.fnap(_DESCRIPTION_OF_SET),
            ),
            invokation_variant_from_args(
                [phase_spec, unset_kw, name],
                self._tp.fnap(_DESCRIPTION_OF_UNSET),
            ),
        ]

    def syntax_element_descriptions(self) -> Sequence[SyntaxElementDescription]:
        return [
            self._phase_spec_sed(),
            self._name_sed(),
        ]

    def _name_sed(self) -> SyntaxElementDescription:
        return SyntaxElementDescription(
            defs.VAR_NAME_ELEMENT,
            self._tp.fnap(_DESCRIPTION__NAME),
            (),
        )

    def _phase_spec_sed(self) -> SyntaxElementDescription:
        phase_spec__act = a.Option(defs.PHASE_SPEC__OPTION_NAME, defs.PHASE_SPEC__ACT)
        phase_spec__non_act = a.Option(defs.PHASE_SPEC__OPTION_NAME, defs.PHASE_SPEC__NON_ACT)
        return SyntaxElementDescription(
            defs.PHASE_SPEC_ELEMENT,
            invokation_variants=[
                invokation_variant_from_args(
                    [a.Single(a.Multiplicity.MANDATORY, phase_spec__act)],
                    self._tp.fnap(_DESCRIPTION__PHASE_SPEC__ACT),
                ),
                invokation_variant_from_args(
                    [a.Single(a.Multiplicity.MANDATORY, phase_spec__non_act)],
                    self._tp.fnap(_DESCRIPTION__PHASE_SPEC__NON_ACT),
                ),
            ],
            before_invokation_variants=(),
        )

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return name_and_cross_ref.cross_reference_id_list([
            concepts.ENVIRONMENT_VARIABLE_CONCEPT_INFO,
            syntax_elements.STRING_SYNTAX_ELEMENT,
        ])


_VALUE_SE = syntax_elements.STRING_SYNTAX_ELEMENT

_FORMAT_DICT = {
    'Note': headers.NOTE_LINE_HEADER,
    'NAME': defs.VAR_NAME_ELEMENT,
    'VALUE': _VALUE_SE.singular_name,
    'PHASE_SPEC': defs.PHASE_SPEC_ELEMENT,
    'env_var': concepts.ENVIRONMENT_VARIABLE_CONCEPT_INFO.name,
    'ATC': concepts.ACTION_TO_CHECK_CONCEPT_INFO.name,
    'os_process': misc_texts.OS_PROCESS_NAME,
    'act_phase': phase_names.ACT,
    'setup_phase': phase_names.SETUP,
    'string_type': types.STRING_TYPE_INFO.name,
}

_DESCRIPTION_OF_SET = """\
Sets the {env_var} {NAME} to {VALUE}.


If {PHASE_SPEC} is given, the {env_var} will only be set in the
specified phase(s).


Elements of the form "${{var_name}}" in {VALUE},
will be replaced with the value of the {env_var} "var_name",
or the empty string, if there is no {env_var} with that name
(in the specified phase).
"""

_DESCRIPTION_OF_UNSET = """\
Removes the {env_var} {NAME}.


If {PHASE_SPEC} is given, the {env_var} will only be removed from the
specified phase(s).
"""

_DESCRIPTION__PHASE_SPEC__ACT = """\
The manipulation will only affect the {env_var:s} of the
{ATC:/q} - the {os_process} executed by the {act_phase} phase.


{Note} If used in phases after {setup_phase}, the manipulation will have no effect.
"""

_DESCRIPTION__PHASE_SPEC__NON_ACT = """\
The manipulation will affect the {env_var:s} of all
{os_process:s} except for the {ATC:/q}.
"""

_DESCRIPTION__NAME = """\
A constant unquoted {string_type}.
"""

_NOTES = """\
The manipulation affects all following phases
(depending on {PHASE_SPEC}).
"""
