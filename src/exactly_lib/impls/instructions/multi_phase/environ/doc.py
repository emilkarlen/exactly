from typing import List, Sequence, Dict

from exactly_lib.common.help import headers
from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, invokation_variant_from_args, \
    SyntaxElementDescription
from exactly_lib.definitions import misc_texts
from exactly_lib.definitions.cross_ref import name_and_cross_ref
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import syntax_elements, concepts
from exactly_lib.definitions.test_case import phase_names
from exactly_lib.impls.instructions.multi_phase.environ import defs
from exactly_lib.impls.instructions.multi_phase.utils.assert_phase_info import IsAHelperIfInAssertPhase
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure.core import ParagraphItem


class TheInstructionDocumentation(InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase,
                                  IsAHelperIfInAssertPhase):
    def __init__(self,
                 name: str,
                 is_in_setup_phase: bool = False,
                 is_in_assert_phase: bool = False,
                 ):
        super().__init__(name, _format_dict(is_in_setup_phase), is_in_assert_phase)
        self._is_in_setup_phase = is_in_setup_phase

    def single_line_description(self) -> str:
        return self._tp.format('Manipulates {env_var:s}')

    def _main_description_rest_body(self) -> List[ParagraphItem]:
        return []

    def _notes__specific(self) -> List[ParagraphItem]:
        template = (
            _NOTES__SETUP
            if self._is_in_setup_phase
            else
            _NOTES__NON_SETUP
        )
        return self._tp.fnap(template)

    def invokation_variants(self) -> Sequence[InvokationVariant]:
        phase_spec_args = self._phase_spec_args()
        name = a.Single(a.Multiplicity.MANDATORY, a.Named(defs.VAR_NAME_ELEMENT))
        assignment = a.Single(a.Multiplicity.MANDATORY, a.Constant(defs.ASSIGNMENT_IDENTIFIER))
        unset_kw = a.Single(a.Multiplicity.MANDATORY, a.Constant(defs.UNSET_IDENTIFIER))
        return [
            invokation_variant_from_args(
                phase_spec_args + [name, assignment, _VALUE_SE.single_mandatory],
                self._tp.fnap(_DESCRIPTION_OF_SET),
            ),
            invokation_variant_from_args(
                phase_spec_args + [unset_kw, name],
                self._tp.fnap(_DESCRIPTION_OF_UNSET),
            ),
        ]

    def _phase_spec_args(self) -> List[a.ArgumentUsage]:
        return (
            [a.Single(a.Multiplicity.OPTIONAL, a.Named(defs.PHASE_SPEC_ELEMENT))]
            if self._is_in_setup_phase
            else
            []
        )

    def syntax_element_descriptions(self) -> Sequence[SyntaxElementDescription]:
        ret_val = []

        if self._is_in_setup_phase:
            ret_val.append(self._phase_spec_sed())
        ret_val.append(self._name_sed())

        return ret_val

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


def _format_dict(is_in_setup_phase: bool) -> Dict[str, str]:
    in_the_specified_phase = (
        ' (in the specified phase)'.format(defs.PHASE_SPEC_ELEMENT)
        if is_in_setup_phase
        else
        ''
    )
    return {
        'Note': headers.NOTE_LINE_HEADER,
        'NAME': defs.VAR_NAME_ELEMENT,
        'VALUE': _VALUE_SE.singular_name,
        'PHASE_SPEC': defs.PHASE_SPEC_ELEMENT,
        'env_var': concepts.ENVIRONMENT_VARIABLE_CONCEPT_INFO.name,
        'ATC': concepts.ACTION_TO_CHECK_CONCEPT_INFO.name,
        'os_process': misc_texts.OS_PROCESS_NAME,
        'act_phase': phase_names.ACT,
        'setup_phase': phase_names.SETUP,
        'string_se': syntax_elements.STRING_SYNTAX_ELEMENT.singular_name,
        'in_the_specified_phase': in_the_specified_phase,
    }


_DESCRIPTION_OF_SET = """\
Sets the {env_var} {NAME} to {VALUE}.


Elements of the form "${{var_name}}" in {VALUE},
will be replaced with the value of the {env_var} "var_name",
or the empty string, if there is no {env_var} with that name{in_the_specified_phase}.
"""

_DESCRIPTION_OF_UNSET = """\
Removes the {env_var} {NAME}.
"""

_DESCRIPTION__PHASE_SPEC__ACT = """\
The manipulation will only affect the {env_var:s} of the
{ATC:/q} - the {os_process} executed by the {act_phase} phase.
"""

_DESCRIPTION__PHASE_SPEC__NON_ACT = """\
The manipulation will affect the {env_var:s} of all
{os_process:s} in all phases except for the {ATC:/q} in the {act_phase} phase.
"""

_DESCRIPTION__NAME = """\
A {string_se}.
"""

_NOTES__NON_SETUP = """\
The manipulation affects all following phases.
"""

_NOTES__SETUP = """\
If {PHASE_SPEC} is not given,
the manipulation will affect all phases (and the {ATC:/q}).
"""
