from typing import List

from exactly_lib.common.help import headers
from exactly_lib.common.help.instruction_documentation import InstructionDocumentation
from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithTextParserBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, invokation_variant_from_args
from exactly_lib.definitions import formatting, misc_texts
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.definitions.entity import concepts, syntax_elements, types
from exactly_lib.definitions.entity.syntax_elements import SyntaxElementInfo
from exactly_lib.impls import texts
from exactly_lib.impls.instructions.assert_.process_output import defs
from exactly_lib.impls.types.program.help_texts import TRANSFORMATION_ARE_IGNORED__TMPL
from exactly_lib.test_case.phases.assert_ import WithAssertPhasePurpose
from exactly_lib.util.cli_syntax.elements import argument as a


def for_std_output_file(name: str, output_file: str) -> InstructionDocumentation:
    checked_property = 'contents of ' + output_file
    return FileContentsCheckerHelp(name, output_file, checked_property,
                                   syntax_elements.STRING_MATCHER_SYNTAX_ELEMENT,
                                   transformations_are_ignored=False)


def for_exit_code(name: str) -> InstructionDocumentation:
    return FileContentsCheckerHelp(name,
                                   'the ' + misc_texts.EXIT_CODE.singular,
                                   misc_texts.EXIT_CODE.singular,
                                   syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT,
                                   transformations_are_ignored=True)


class FileContentsCheckerHelp(InstructionDocumentationWithTextParserBase, WithAssertPhasePurpose):
    def __init__(self,
                 instruction_name: str,
                 checked_file: str,
                 name_of_checked_property: str,
                 matcher: SyntaxElementInfo,
                 transformations_are_ignored: bool,
                 ):
        transformations_are_ignored_text = (
            TRANSFORMATION_ARE_IGNORED__TMPL.format(
                Note=headers.NOTE_LINE_HEADER,
                PROGRAM=syntax_elements.PROGRAM_SYNTAX_ELEMENT.singular_name,
            )
            if transformations_are_ignored
            else
            ''
        )
        super().__init__(instruction_name,
                         {
                             'checked_file': checked_file,
                             'matcher': matcher.singular_name,
                             'checked_property': name_of_checked_property,
                             'action_to_check': formatting.concept_(concepts.ACTION_TO_CHECK_CONCEPT_INFO),
                             'program_type': types.PROGRAM_TYPE_INFO.name,
                             'The_program_type_must_terminate': texts.THE_PROGRAM_TYPE_MUST_TERMINATE_SENTENCE,
                             'Transformations_are_ignored': transformations_are_ignored_text
                         })
        self._checked_file = checked_file
        self._matcher = matcher

    def single_line_description(self) -> str:
        return self._tp.format(_SINGLE_LINE_DESCRIPTION)

    def invokation_variants(self) -> List[InvokationVariant]:
        return [
            invokation_variant_from_args(
                self._invokation_variant__non_program(),
                self._tp.fnap(_MAIN_INVOKATION__STDOUT_ERR_ACTION_TO_CHECK__SYNTAX_DESCRIPTION)
            ),
            invokation_variant_from_args(
                self._invokation_variant__program(defs.OUTPUT_FROM_PROGRAM_OPTION_NAME),
                self._tp.fnap(_MAIN_INVOKATION__STDOUT_ERR_PROGRAM__SYNTAX_DESCRIPTION)
            ),
        ]

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return cross_reference_id_list([
            self._matcher,
            syntax_elements.PROGRAM_SYNTAX_ELEMENT,
            concepts.ACTION_TO_CHECK_CONCEPT_INFO,
        ])

    def _invokation_variant__non_program(self) -> List[a.ArgumentUsage]:
        return [
            self._matcher.single_mandatory,
        ]

    def _invokation_variant__program(self, program_option: a.OptionName) -> List[a.ArgumentUsage]:
        program_output_option = a.Single(a.Multiplicity.MANDATORY,
                                         a.Option(program_option))

        program_arg = a.Single(a.Multiplicity.MANDATORY,
                               syntax_elements.PROGRAM_SYNTAX_ELEMENT.argument)
        return [
            program_output_option,
            program_arg,
            self._matcher.single_mandatory,
        ]


_SINGLE_LINE_DESCRIPTION = 'Tests the {checked_property} from the {action_to_check}, or from {program_type:a/q}'

_MAIN_INVOKATION__STDOUT_ERR_ACTION_TO_CHECK__SYNTAX_DESCRIPTION = """\
Asserts that {checked_file} from the {action_to_check} satisfies {matcher}.
"""

_MAIN_INVOKATION__STDOUT_ERR_PROGRAM__SYNTAX_DESCRIPTION = """\
Asserts that {checked_file} from {program_type:a/q} satisfies {matcher}.


{matcher} must appear on a separate line.


The {program_type} is executed once, and only once.


{The_program_type_must_terminate}


{Transformations_are_ignored}
"""
